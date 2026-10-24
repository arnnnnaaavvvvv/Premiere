"""Pipeline orchestrator running analyze, script, capture, and render sequentially."""

import os
import time
from pathlib import Path
from sqlalchemy import select
import structlog
from api.config import settings
from api.database import AsyncSessionLocal
from api.models import Asset, Job, JobStatus, Render, Script
from worker.analyze import analyze_repository
from worker.audio import select_track_for_mood
from worker.capture import capture_page
from worker.render import render_video
from worker.script import generate_scene_plan

logger = structlog.get_logger()

async def update_job_status(job_id: str, status: JobStatus, progress: int, stage: str, error: str | None = None):
    """Atomically update database record with current pipeline stage and progress."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Job).where(Job.id == job_id))
        job = res.scalar_one_or_none()
        if job:
            job.status = status
            job.progress = progress
            job.current_stage = stage
            if error:
                job.error_message = error
            await db.commit()

async def run_pipeline(job_id: str) -> str:
    """Execute end-to-end video pipeline for given job ID."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Job).where(Job.id == job_id))
        job = res.scalar_one_or_none()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        live_url, repo_url, mood = job.live_url, job.repo_url, job.mood

    job_storage_dir = Path(settings.storage_dir) / job_id
    os.makedirs(job_storage_dir, exist_ok=True)
    start_time = time.time()
    logger.info("Pipeline started", job_id=job_id, live_url=live_url, repo_url=repo_url)

    try:
        # 1. Analyze Stage
        t0 = time.time()
        await update_job_status(job_id, JobStatus.ANALYZING, 15, "Analyzing GitHub repository...")
        brief = await analyze_repository(repo_url, live_url)
        logger.info("Stage completed: analyze", job_id=job_id, duration_sec=round(time.time() - t0, 2))

        # 2. Script Stage
        t0 = time.time()
        await update_job_status(job_id, JobStatus.SCRIPTING, 35, "Synthesizing Apple-style scene plan...")
        plan = generate_scene_plan(job_id, brief, mood=mood, fps=settings.render_fps)
        logger.info("Stage completed: script", job_id=job_id, duration_sec=round(time.time() - t0, 2))

        async with AsyncSessionLocal() as db:
            db.add(Script(job_id=job_id, product_brief=brief.model_dump(), scene_plan=plan.model_dump()))
            await db.commit()

        # 3. Capture Stage
        t0 = time.time()
        await update_job_status(job_id, JobStatus.CAPTURING, 55, "Recording 60fps browser interactions...")
        asset_paths = {}
        for scene in plan.scenes:
            if scene.scene_type in ("DeviceShowcase", "FeatureZoom"):
                captures = await capture_page(live_url, job_storage_dir, scene.scene_id, scene.target_route)
                asset_paths[scene.scene_id] = captures.get("screenshot", "")
                async with AsyncSessionLocal() as db:
                    db.add(Asset(job_id=job_id, asset_type="screenshot", file_path=captures.get("screenshot", "")))
                    await db.commit()
        logger.info("Stage completed: capture", job_id=job_id, duration_sec=round(time.time() - t0, 2))

        # 4. Audio & Beat Quantization
        track = select_track_for_mood(mood)

        # 5. Render Stage
        t0 = time.time()
        await update_job_status(job_id, JobStatus.RENDERING, 75, "Rendering 1080p MP4 launch film...")
        mp4_path = await render_video(job_id, plan, asset_paths, brief.product_name, job_storage_dir)
        logger.info("Stage completed: render", job_id=job_id, duration_sec=round(time.time() - t0, 2))

        # 6. Complete
        file_size = os.path.getsize(mp4_path) if os.path.exists(mp4_path) else 0
        duration_sec = plan.total_duration_frames / settings.render_fps

        async with AsyncSessionLocal() as db:
            db.add(Render(
                job_id=job_id,
                video_url=mp4_path,
                duration_seconds=duration_sec,
                resolution=f"{settings.render_width}x{settings.render_height}",
                file_size_bytes=file_size,
            ))
            await db.commit()

        await update_job_status(job_id, JobStatus.DONE, 100, "Render completed successfully")
        return mp4_path

    except Exception as exc:
        await update_job_status(job_id, JobStatus.FAILED, 0, "Pipeline failed", error=str(exc))
        raise
