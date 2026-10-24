"""Security utilities: Server-Side Request Forgery (SSRF) validation."""

import ipaddress
import socket
from urllib.parse import urlparse

# Subnets strictly blocked from automated scraping or navigation
BLOCKED_NETWORKS = (
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private Class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private Class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private Class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local / Metadata
    ipaddress.ip_network("0.0.0.0/8"),        # Broadcast
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 ULA
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
)

def validate_public_url(url: str) -> str:
    """Validate that a URL strictly targets a safe public host and protocol."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Prohibited URL scheme: {parsed.scheme}. Only HTTP/HTTPS permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must contain a valid hostname.")

    # Prevent localhost aliases directly
    if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        raise ValueError(f"Prohibited loopback target host: {hostname}")

    try:
        # Resolve hostname to IPv4/IPv6 addresses
        addr_info = socket.getaddrinfo(hostname, None)
        for item in addr_info:
            ip_str = item[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            for blocked_net in BLOCKED_NETWORKS:
                if ip_obj in blocked_net:
                    raise ValueError(f"Target host resolves to restricted private address: {ip_str}")
    except socket.gaierror as err:
        raise ValueError(f"Failed to resolve hostname '{hostname}': {err}")

    return url.strip()
