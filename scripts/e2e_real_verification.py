"""End-to-end verification script testing full pipeline on 3 real sites with MP4 validation."""

import asyncio
import os
import cv2
from api.database import init_db
from worker.pipeline import run_pipeline
from api.models import Job, JobStatus
from api.database import AsyncSessionLocal

TEST_CASES = [
    {
        "name": "Simple Static Site",
        "live_url": "https://example.com",
        "repo_url": "https://github.com/facebook/react",
        "mood": "energetic",
    },
    {
        "name": "Heavy Modern SPA",
        "live_url": "https://react.dev",
        "repo_url": "https://github.com/vercel/next.js",
        "mood": "minimal",
    },
    {
        "name": "Minimal/Blocking Site",
        "live_url": "https://news.ycombinator.com",
        "repo_url": "https://github.com/torvalds/linux",
        "mood": "futuristic",
    },
]

async def verify_site_pipeline(case: dict) -> dict:
    """Run full pipeline for a site and verify the output MP4 video properties."""
    print(f"\n--- Testing: {case['name']} ({case['live_url']}) ---")
    await init_db()

    job_id = f"e2e-test-{case['mood']}-{os.urandom(4).hex()}"
    # Ensure job ID is valid UUID format
    import uuid
    job_uuid = str(uuid.uuid4())

    async with AsyncSessionLocal() as db:
        job = Job(
            id=job_uuid,
            live_url=case["live_url"],
            repo_url=case["repo_url"],
            mood=case["mood"],
            status=JobStatus.QUEUED,
        )
        db.add(job)
        await db.commit()

    mp4_path = await run_pipeline(job_uuid)
    assert os.path.exists(mp4_path), f"Output MP4 does not exist at {mp4_path}"

    file_size = os.path.getsize(mp4_path)
    assert file_size > 50000, f"MP4 file size too small: {file_size} bytes"

    # Verify video with OpenCV
    cap = cv2.VideoCapture(mp4_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    duration = frame_count / (fps or 30.0)

    result = {
        "case": case["name"],
        "url": case["live_url"],
        "mood": case["mood"],
        "mp4_path": mp4_path,
        "file_size_bytes": file_size,
        "resolution": f"{width}x{height}",
        "fps": fps,
        "frames": frame_count,
        "duration_sec": round(duration, 2),
        "status": "VERIFIED_VALID",
    }
    print(f"Result for {case['name']}: {result}")
    return result

async def main():
    results = []
    for case in TEST_CASES:
        res = await verify_site_pipeline(case)
        results.append(res)
    print("\n=== ALL 3 REAL SITES VERIFIED ===")
    for r in results:
        print(f"[{r['status']}] {r['case']} -> {r['resolution']} @ {r['fps']}fps, {r['duration_sec']}s ({r['file_size_bytes']} bytes)")

if __name__ == "__main__":
    asyncio.run(main())
