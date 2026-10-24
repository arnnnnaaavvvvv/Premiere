"""Security and SSRF audit test suite covering IP ranges, schemes, and signed tokens."""

import time
import pytest
from api.security import (
    create_signed_video_token,
    validate_public_url,
    verify_signed_video_token,
)

@pytest.mark.parametrize("malicious_url", [
    "http://127.0.0.1:8000",
    "http://169.254.169.254/latest/meta-data",
    "http://10.0.0.1/admin",
    "http://192.168.1.1/",
    "http://172.16.0.1/",
    "http://localhost:3000",
    "file:///etc/shadow",
    "ftp://example.com/file",
    "gopher://127.0.0.1:6379",
])
def test_ssrf_rejects_disallowed_targets(malicious_url):
    """Ensure SSRF validator strictly rejects private subnets, cloud metadata, and forbidden schemes."""
    with pytest.raises(ValueError):
        validate_public_url(malicious_url)

def test_signed_token_lifecycle():
    """Verify HMAC time-limited signature token generation and expiration."""
    job_id = "test-job-uuid-1234"
    token = create_signed_video_token(job_id, expires_in_sec=60)
    assert verify_signed_video_token(job_id, token) is True

    # Tampered token fails
    assert verify_signed_video_token(job_id, token + "bad") is False
    assert verify_signed_video_token("different-job-id", token) is False

    # Expired token fails
    expired_token = create_signed_video_token(job_id, expires_in_sec=-10)
    assert verify_signed_video_token(job_id, expired_token) is False
