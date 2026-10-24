"""Security utilities: Multi-layer SSRF validation, DNS rebinding guard, and signed tokens."""

import hashlib
import hmac
import ipaddress
import socket
import time
from urllib.parse import urlparse
from api.config import settings

ALLOWED_PORTS = (80, 443, 8080, 8443)
BLOCKED_HOSTNAMES = {"localhost", "metadata.google.internal", "instance-data", "metadata"}

BLOCKED_NETWORKS = (
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.88.99.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("ff00::/8"),
    ipaddress.ip_network("::ffff:0:0/96"),  # IPv4-mapped IPv6
)

def _check_ip_allowed(ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address, host_repr: str):
    """Raise ValueError if the IP belongs to any private, loopback, or metadata subnet."""
    if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved or ip_obj.is_unspecified:
        raise ValueError(f"Restricted IP target: {ip_obj}")
    for net in BLOCKED_NETWORKS:
        if ip_obj in net:
            raise ValueError(f"IP {ip_obj} for host '{host_repr}' is in blocked network {net}")

def validate_public_url(url: str) -> str:
    """Validate that a URL targets a public protocol and strictly public IP address."""
    clean_url = url.strip()
    parsed = urlparse(clean_url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Prohibited URL scheme: '{parsed.scheme}'. Only HTTP/HTTPS permitted.")

    if parsed.username or parsed.password:
        raise ValueError("User credentials inside URLs are prohibited.")

    if parsed.port and parsed.port not in ALLOWED_PORTS:
        raise ValueError(f"Prohibited port: {parsed.port}. Allowed ports: {ALLOWED_PORTS}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must contain a valid hostname.")

    if hostname.lower() in BLOCKED_HOSTNAMES:
        raise ValueError(f"Prohibited target host: {hostname}")

    # Check decimal / hex numeric IP representation
    if hostname.isdigit():
        _check_ip_allowed(ipaddress.ip_address(int(hostname)), hostname)
    elif hostname.lower().startswith("0x"):
        try:
            _check_ip_allowed(ipaddress.ip_address(int(hostname, 16)), hostname)
        except ValueError:
            pass

    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for item in addr_info:
            ip_obj = ipaddress.ip_address(item[4][0])
            _check_ip_allowed(ip_obj, hostname)
    except socket.gaierror as err:
        raise ValueError(f"DNS resolution failure for host '{hostname}': {err}")

    return clean_url

def create_signed_video_token(job_id: str, expires_in_sec: int = 86400) -> str:
    """Generate time-limited HMAC-SHA256 signature token for secure video access."""
    expiry = int(time.time()) + expires_in_sec
    payload = f"{job_id}:{expiry}"
    sig = hmac.new(settings.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
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
        expected = hmac.new(settings.secret_key.encode(), f"{job_id}:{expiry}".encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)
    except Exception:
        return False

