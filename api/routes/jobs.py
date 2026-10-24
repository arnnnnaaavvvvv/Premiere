"""Job routes: creation, status polling, and signed video streaming endpoints."""

import os
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from api.config import settings
from api.database import get_db
from api.models import Job, JobStatus, Render
from api.schemas import CreateJobRequest, JobResponse
from api.security import create_signed_video_token, verify_signed_video_token
from worker.pipeline import run_pipeline

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: CreateJobRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Accept and validate a new video generation request."""
    new_job = Job(
        live_url=payload.live_url,
        repo_url=payload.repo_url,
        mood=payload.mood,
        music=payload.music,
        narration=payload.narration,
        credentials_json=payload.credentials.model_dump() if payload.credentials else None,
        status=JobStatus.QUEUED,
        progress=0,
        current_stage="Queued for processing",
    )
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # Dispatch to background task worker
    background_tasks.add_task(run_pipeline, new_job.id)

    return JobResponse(
        id=new_job.id,
        live_url=new_job.live_url,
        repo_url=new_job.repo_url,
        mood=new_job.mood,
        music=new_job.music,
        narration=new_job.narration,
        status=new_job.status,
        progress=new_job.progress,
        current_stage=new_job.current_stage,
        error_message=new_job.error_message,
        created_at=new_job.created_at,
        updated_at=new_job.updated_at,
        video_url=None,
    )

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch real-time progress and signed video URL of a job."""
    stmt = select(Job).options(selectinload(Job.render)).where(Job.id == job_id)
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    video_url = None
    if job.render and job.render.video_url:
        token = create_signed_video_token(job.id)
        video_url = f"{settings.public_base_url}/api/v1/jobs/{job.id}/video?token={token}"

    return JobResponse(
        id=job.id,
        live_url=job.live_url,
        repo_url=job.repo_url,
        mood=job.mood,
        music=job.music,
        narration=job.narration,
        status=job.status,
        progress=job.progress,
        current_stage=job.current_stage,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
        video_url=video_url,
    )

@router.get("/{job_id}/video")
async def get_job_video(
    job_id: str,
    token: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Stream or download the final rendered MP4 video with signature verification."""
    if token and not verify_signed_video_token(job_id, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired video download token")

    stmt = select(Render).where(Render.job_id == job_id)
    res = await db.execute(stmt)
    render = res.scalar_one_or_none()

    if not render or not render.video_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rendered video not available yet")

    if not os.path.exists(render.video_url):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video file missing on disk")

    return FileResponse(
        path=render.video_url,
        media_type="video/mp4",
        filename=f"launch-{job_id[:8]}.mp4",
    )
