# 09. Security Architecture: SSRF Protection & Sandboxing

## 1. Threat Model & Attack Vectors

Because Premiere ingests arbitrary user-supplied URLs and spawns headless browsers in internal infrastructure, it faces severe attack vectors if improperly defended:
1. **Server-Side Request Forgery (SSRF)**: Attacker submits `http://169.254.169.254/latest/meta-data/` to harvest cloud credentials, or `http://10.0.0.5:6379` to compromise Redis.
2. **DNS Rebinding**: Attacker supplies a public hostname that initially resolves to a public IP during validation, but shifts to an internal IP ($127.0.0.1$) when Playwright navigates.
3. **Headless Browser Remote Code Execution (RCE)**: Attacker crafts a malicious WebGL/V8 exploit targeting the headless Chromium rendering engine.
4. **Credential Harvesting**: Attacker inspects database logs or memory dumps to extract third-party login credentials provided for auth-gated demonstrations.

---

## 2. Multi-Layer SSRF & DNS Rebinding Defense

```
[ Inbound Target URL ]
          |
          v
  [ Layer 1: Protocol & Scheme Filter ]
  - Must strictly be 'https://' (or 'http://' with explicit port 80)
  - Rejects 'file://', 'gopher://', 'ftp://', 'data://', 'ldap://'
          |
          v
  [ Layer 2: Pre-Flight DNS Resolution Guard ]
  - Resolves all IPv4 and IPv6 A/AAAA records
  - Compares resolved IPs against Disallowed Subnet Table
          |
          v
  [ Layer 3: Playwright Custom Route Proxy / Socket Pinning ]
  - Pins resolved IP at TCP socket level to defeat DNS Rebinding
  - Drops connection immediately if socket attempts egress to private range
```

### Disallowed IP Ranges (CIDR Blocklist)

```python
import ipaddress
import socket
from urllib.parse import urlparse

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback IPv4
    ipaddress.ip_network("10.0.0.0/8"),       # RFC 1918 Private Class A
    ipaddress.ip_network("172.16.0.0/12"),    # RFC 1918 Private Class B
    ipaddress.ip_network("192.168.0.0/16"),   # RFC 1918 Private Class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local / Cloud Metadata
    ipaddress.ip_network("0.0.0.0/8"),        # Broadcast
    ipaddress.ip_network("::1/128"),          # Loopback IPv6
    ipaddress.ip_network("fc00::/7"),         # Unique Local Address (ULA) IPv6
    ipaddress.ip_network("fe80::/10"),        # Link-Local IPv6
]

def validate_url_safe_for_egress(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Prohibited protocol scheme: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid target hostname")

    # Resolve all associated IP addresses
    addr_info = socket.getaddrinfo(hostname, None)
    for item in addr_info:
        ip_str = item[4][0]
        ip_obj = ipaddress.ip_address(ip_str)
        for blocked_net in BLOCKED_NETWORKS:
            if ip_obj in blocked_net:
                raise PermissionError(f"Target host resolves to prohibited network: {ip_str}")
    return True
```

---

## 3. Headless Browser Container Sandboxing

Playwright workers execute in hardened, ephemeral Docker containers with strict security constraints:

```dockerfile
# Rootless, non-privileged execution
USER pwuser
SECURITY_OPTS:
  - --cap-drop=ALL
  - --security-opt=no-new-privileges:true
  - --pids-limit=100
  - --memory=2g
  - --cpus=2.0
  - --read-only-rootfs
```

- **Ephemeral Storage**: `/tmp` mounted as an in-memory `tmpfs` volume with a 512MB quota. All downloaded cache and session cookies vanish upon container exit.
- **Network Isolation**: Capture containers reside on an isolated bridge network that cannot communicate with Redis, PostgreSQL, or adjacent worker nodes. Outbound traffic is forced through an egress-filtering proxy.

---

## 4. Transient Credential Handling Protocol

For auth-gated demonstrations where users supply temporary demo credentials:
1. **Never Persisted**: Credentials are submitted over HTTPS, passed in memory to the capture task queue, and injected directly into form fields via Playwright.
2. **Database Scrubbing**: The `auth_credentials` field in the database is purged or populated only with a redacted hash indicator (`{"has_credentials": true}`).
3. **Log Sanitization**: Pydantic models automatically mask password fields in error reports and OpenTelemetry traces.
4. **Session Purge**: Browser sessions are destroyed immediately after screencast capture completes; no authentication cookies persist across jobs.

---

## 5. Rate Limiting & Abuse Prevention

- **Per-IP Rate Limiting**: 5 video generation requests per hour for anonymous clients, managed via Redis sliding-window counters.
- **Concurrent Job Quotas**: Max 1 active running job per IP/user account.
- **GitHub Token Handling**: User-provided GitHub personal access tokens (for private repos) are encrypted using AES-256-GCM using AWS KMS / HashiCorp Vault envelopes, decrypted strictly in-memory by the Analyzer worker, and zeroized immediately post-AST extraction.
