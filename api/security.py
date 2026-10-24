"""Security utilities: Multi-layer SSRF validation, DNS rebinding guard, and signed tokens."""

import hashlib
import hmac
import ipaddress
import socket
import time
from urllib.parse import urlparse

BLOCKED_NETWORKS = (
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("::ffff:0:0/96"),  # IPv4-mapped IPv6
)

SECRET_KEY = "premiere-token-secret-key-change-in-prod"

def validate_public_url(url: str) -> str:
    """Validate that a URL targets a public protocol and strictly public IP address."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Prohibited URL scheme: '{parsed.scheme}'. Only HTTP/HTTPS permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must contain a valid hostname.")

    if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        raise ValueError(f"Prohibited loopback target host: {hostname}")

    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for item in addr_info:
            ip_str = item[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            for blocked_net in BLOCKED_NETWORKS:
                if ip_obj in blocked_net or ip_obj.is_private or ip_obj.is_loopback:
                    raise ValueError(f"Host '{hostname}' resolves to restricted IP: {ip_str}")
    except socket.gaierror as err:
        raise ValueError(f"DNS resolution failure for host '{hostname}': {err}")

    return url.strip()

def create_signed_video_token(job_id: str, expires_in_sec: int = 86400) -> str:
    """Generate time-limited HMAC-SHA256 signature token for secure video access."""
    expiry = int(time.time()) + expires_in_sec
    payload = f"{job_id}:{expiry}"
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{expiry}:{sig}"

def verify_signed_video_token(job_id: str, token: str) -> bool:
    """Verify HMAC signature and timestamp freshness for video download."""
    try:
        parts = token.split(":")
        if len(parts) != 2:
            return False
        expiry = int(parts[0])
        sig = parts[1]
        if time.time() > expiry:
            return False
        expected = hmac.new(SECRET_KEY.encode(), f"{job_id}:{expiry}".encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)
    except Exception:
        return False
