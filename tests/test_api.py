"""Integration tests for FastAPI endpoints and security validation."""

import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from api.database import init_db
from api.main import app
from api.security import validate_public_url

def test_ssrf_protection_blocks_loopback_and_private():
    """Verify SSRF filter raises error on private or loopback targets."""
    with pytest.raises(ValueError):
        validate_public_url("http://localhost:3000")

    with pytest.raises(ValueError):
        validate_public_url("http://127.0.0.1:8080")

    with pytest.raises(ValueError, match="Prohibited URL scheme"):
        validate_public_url("file:///etc/passwd")


def test_ssrf_protection_allows_valid_domain():
    """Verify SSRF filter permits legitimate public URLs."""
    valid_url = "https://github.com/torvalds/linux"
    res = validate_public_url(valid_url)
    assert res == valid_url

def test_create_and_get_job():
    """Test job submission and status lookup endpoints."""
    async def _run():
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/health")
            assert res.status_code == 200
            assert res.json()["status"] == "ok"

            payload = {
                "live_url": "https://example.com",
                "repo_url": "https://github.com/owner/sample-repo",
                "mood": "energetic",
                "music": "default",
                "narration": False,
            }
            create_res = await client.post("/api/v1/jobs", json=payload)
            assert create_res.status_code == 201
            data = create_res.json()
            assert "id" in data
            assert data["status"] == "queued"
            job_id = data["id"]

            get_res = await client.get(f"/api/v1/jobs/{job_id}")
            assert get_res.status_code == 200
            job_data = get_res.json()
            assert job_data["id"] == job_id
            assert job_data["live_url"] == "https://example.com"

    asyncio.run(_run())
