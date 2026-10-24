"""Worker daemon loop executing queued video rendering jobs."""

import asyncio
import structlog
from sqlalchemy import select
from api.database import AsyncSessionLocal, init_db
from api.models import Job, JobStatus
from worker.pipeline import run_pipeline

logger = structlog.get_logger()

async def process_next_queued_job() -> bool:
    """Fetch and process the oldest queued job in the database."""
    async with AsyncSessionLocal() as db:
        stmt = select(Job).where(Job.status == JobStatus.QUEUED).order_by(Job.created_at.asc()).limit(1)
        res = await db.execute(stmt)
        job = res.scalar_one_or_none()
        if not job:
            return False
        job_id = job.id

    logger.info("Processing job", job_id=job_id)
    try:
        mp4_path = await run_pipeline(job_id)
        logger.info("Job successfully completed", job_id=job_id, output=mp4_path)
    except Exception as exc:
        logger.error("Job execution failed", job_id=job_id, error=str(exc))

    return True

async def worker_loop():
    """Continuous polling loop for worker daemon."""
    await init_db()
    logger.info("ReelForge worker daemon started")

    while True:
        had_work = await process_next_queued_job()
        if not had_work:
            await asyncio.sleep(2.0)

if __name__ == "__main__":
    asyncio.run(worker_loop())
