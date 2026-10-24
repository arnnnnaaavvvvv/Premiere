"""Exhaustive red-team security regression test suite covering Checklist A-L."""

import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from api.database import AsyncSessionLocal, init_db
from api.main import app
from api.models import Job, Render
from api.schemas import CreateJobRequest
from api.security import create_signed_video_token, validate_public_url, verify_signed_video_token

@pytest.mark.parametrize("malicious_url", [
    "http://127.0.0.1:8000",
    "http://169.254.169.254/latest/meta-data",
    "http://metadata.google.internal/computeMetadata/v1/",
    "http://10.0.0.1/admin",
    "http://192.168.1.1/",
    "http://172.16.0.1/",
    "http://100.64.0.1/",
    "http://localhost:3000",
    "file:///etc/shadow",
    "ftp://example.com/file",
    "gopher://127.0.0.1:6379",
    "http://2130706433/",       # Decimal encoding for 127.0.0.1
    "http://0x7f000001/",       # Hex encoding for 127.0.0.1
    "http://example.com:22/",   # Disallowed port (SSH)
    "http://example.com:6379/", # Disallowed port (Redis)
    "http://admin:secret@example.com/", # Embedded credentials
])
def test_ssrf_and_url_hardening(malicious_url):
    """Ensure multi-layer SSRF filter rejects alternative IPs, ports, and metadata endpoints."""
    with pytest.raises(ValueError):
        validate_public_url(malicious_url)

def test_repo_url_spoofing_prevented():
    """Verify repo_url cannot bypass github.com check using subdomains or paths."""
    with pytest.raises(ValueError):
        CreateJobRequest(live_url="https://example.com", repo_url="https://github.com.evil.com/repo")
    with pytest.raises(ValueError):
        CreateJobRequest(live_url="https://example.com", repo_url="https://evil.com/?github.com")

def test_signed_token_lifecycle():
    """Verify HMAC time-limited signature token generation, freshness, and anti-tamper."""
    job_id = "11111111-2222-3333-4444-555555555555"
    token = create_signed_video_token(job_id, expires_in_sec=60)
    assert verify_signed_video_token(job_id, token) is True
    assert verify_signed_video_token(job_id, token + "bad") is False
    assert verify_signed_video_token("99999999-9999-9999-9999-999999999999", token) is False
    expired_token = create_signed_video_token(job_id, expires_in_sec=-10)
    assert verify_signed_video_token(job_id, expired_token) is False

def test_video_download_auth_enforcement_and_storage_isolation():
    """Verify unsigned requests are rejected with 403 and /storage is unmounted."""
    async def _run():
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            job_id = "11111111-2222-3333-4444-555555555555"

            # 1. Access without token must be blocked (403 Forbidden)
            res_no_token = await client.get(f"/api/v1/jobs/{job_id}/video")
            assert res_no_token.status_code == 403

            # 2. Access with invalid token must be blocked (403 Forbidden)
            res_bad_token = await client.get(f"/api/v1/jobs/{job_id}/video?token=invalid:token")
            assert res_bad_token.status_code == 403

            # 3. Direct static access to /storage must be 404 (unmounted)
            res_storage = await client.get(f"/storage/{job_id}/final.mp4")
            assert res_storage.status_code == 404

            # 4. Security headers must be present on all responses
            health_res = await client.get("/health")
            assert health_res.headers.get("x-frame-options") == "DENY"
            assert health_res.headers.get("x-content-type-options") == "nosniff"
            assert "strict-origin" in health_res.headers.get("referrer-policy", "")

    asyncio.run(_run())

def test_password_scrubbing_on_job_creation():
    """Verify user passwords are never stored in plaintext inside the database."""
    async def _run():
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "live_url": "https://example.com",
                "repo_url": "https://github.com/facebook/react",
                "credentials": {
                    "login_url": "https://example.com/login",
                    "username": "testuser",
                    "password": "SUPER_SECRET_PASSWORD_123!",
                },
            }
            res = await client.post("/api/v1/jobs", json=payload)
            assert res.status_code == 201
            job_id = res.json()["id"]

            async with AsyncSessionLocal() as db:
                job = await db.get(Job, job_id)
                assert job is not None
                if job.credentials_json:
                    assert "password" not in job.credentials_json
                    assert "SUPER_SECRET_PASSWORD_123!" not in str(job.credentials_json)

    asyncio.run(_run())
