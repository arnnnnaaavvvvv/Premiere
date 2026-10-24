"""Exhaustive QA Invariant, Fuzz, and Pipeline Execution Test Suite."""

import asyncio
import os
import re
import pytest
from hypothesis import given, strategies as st
from api.database import AsyncSessionLocal, init_db
from api.models import Asset, Job, JobStatus, Render, Script
from api.schemas import CreateJobRequest
from worker.analyze import build_deterministic_brief, parse_github_owner_repo
from worker.audio import calculate_beat_timestamps, select_track_for_mood
from worker.pipeline import run_pipeline
from worker.render import draw_safe_text, render_video
from worker.script import enforce_apple_copy_rules, generate_scene_plan

def test_scene_plan_duration_invariants():
    """Invariant: Scene durations must sum exactly to total_duration_frames."""
    brief = build_deterministic_brief("https://github.com/test/repo", "https://test.dev", {})
    for fps in (24, 30, 60):
        plan = generate_scene_plan("test-job-uuid", brief, mood="energetic", fps=fps)
        summed = sum(s.duration_frames for s in plan.scenes)
        assert plan.total_duration_frames == summed
        assert len(plan.scenes) == 6
        assert plan.fps == fps

def test_audio_track_catalog_and_mood_invariants():
    """Invariant: Every mood preset must resolve to a valid existing .wav audio file."""
    base_audio = os.path.join(os.path.dirname(__file__), "..", "worker", "audio")
    for mood in ("energetic", "minimal", "futuristic"):
        track = select_track_for_mood(mood)
        assert track["mood"].lower() == mood
        assert track["bpm"] > 0
        audio_file = os.path.join(base_audio, track["filename"])
        assert os.path.exists(audio_file), f"Missing audio stem for mood {mood}: {audio_file}"

@given(st.text(min_size=0, max_size=500))
def test_fuzz_apple_copy_rules(text):
    """Property test: enforce_apple_copy_rules must never crash and never exceed max words."""
    res = enforce_apple_copy_rules(text, max_words=6)
    assert len(res.split()) <= 6
    assert res == res.upper()

@given(st.text(min_size=1, max_size=200))
def test_fuzz_draw_safe_text_no_crash(text):
    """Property test: draw_safe_text handles arbitrary Unicode/emoji text without exception."""
    from PIL import Image, ImageDraw
    from worker.render import BEBAS_FONT_PATH
    img = Image.new("RGB", (1920, 1080), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_safe_text(draw, text, y=500, max_w=1680, base_size=120, font_path=BEBAS_FONT_PATH)

def test_malformed_github_url_rejections():
    """Fuzz/edge case: Invalid repository formats must fail gracefully."""
    invalid_urls = [
        "https://github.com",
        "https://github.com/",
        "https://github.com/single",
        "https://notgithub.com/owner/repo",
        "ftp://github.com/owner/repo",
        "https://github.com/owner/repo/pulls/12",
    ]
    for url in invalid_urls:
        with pytest.raises(ValueError):
            parse_github_owner_repo(url)

def test_pipeline_retry_idempotency():
    """Invariant: Retrying a pipeline run must clean old records and never raise IntegrityError."""
    async def _run():
        import uuid
        test_job_id = str(uuid.uuid4())
        await init_db()
        async with AsyncSessionLocal() as db:
            job = Job(
                id=test_job_id,
                live_url="https://example.com",
                repo_url="https://github.com/facebook/react",
                mood="energetic",
                status=JobStatus.QUEUED,
            )
            db.add(job)
            await db.commit()

        # Run 1
        path1 = await run_pipeline(test_job_id)
        assert os.path.exists(path1)

        # Reset status to QUEUED and run again (simulating worker retry)
        async with AsyncSessionLocal() as db:
            j = await db.get(Job, test_job_id)
            j.status = JobStatus.QUEUED
            await db.commit()

        # Run 2 (Must succeed without duplicate key error)
        path2 = await run_pipeline(test_job_id)
        assert os.path.exists(path2)

    asyncio.run(_run())
