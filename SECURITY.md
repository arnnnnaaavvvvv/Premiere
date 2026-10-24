# Premiere Security Policy & Threat Model

Premiere processes untrusted internet URLs, clone specifications, and executes headless browser capture pipelines. This document details our threat model, defensive architecture, and vulnerability reporting process.

---

## 1. STRIDE Threat Model

| STRIDE Category | Threat Description | Attack Vector in Premiere | Engineered Countermeasure |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker impersonates legitimate job owner or video requester. | Guessing job IDs to download customer video renders. | HMAC-SHA256 time-limited signed video download tokens (`verify_signed_video_token`). |
| **Tampering** | Injected payloads in repo README, package.json, or live DOM. | Prompt injection into LLM; CSS/JS route poisoning. | Delimiter isolation (`<untrusted_repo_content>`), system prompt security rules, and strict regex route sanitization. |
| **Repudiation** | Malicious requests without audit trail or origin tracking. | Denying malicious URL or DoS job dispatch. | Structured JSON telemetry logs (`structlog`) recording client IP, request latency, and job states without PII. |
| **Information Disclosure** | Leakage of cloud metadata, host files, or database credentials. | SSRF targeting `169.254.169.254`, `127.0.0.1`, or unmounted static paths. | Multi-tier SSRF validation on schema and Playwright route level; storage directory unmounted from public HTTP. |
| **Denial of Service** | Resource exhaustion via infinite loops, huge repos, or memory bombs. | Submitting 100 concurrent jobs; malicious V8 JS heap attacks. | Bounded sliding-window IP rate limiting, 15s page navigation timeout, 120s FFmpeg timeout, `--js-flags=--max-old-space-size=512`. |
| **Elevation of Privilege** | Container escape from Playwright Chromium or worker process. | Compromised Chromium sandbox accessing host filesystem. | Chromium running with `--disable-local-file-access`, non-root user `appuser` (UID 1000) in Docker containers. |

---

## 2. Security Guarantees & Non-Negotiable Rules

1. **Strict SSRF Immunity**: Every URL submitted or redirected is evaluated against private IPv4, IPv6, loopback, carrier-grade NAT, and cloud metadata subnets before navigation.
2. **Untrusted LLM Ingestion**: All repository files (README, package.json) are treated as active hostile inputs and enclosed in XML boundary tags with explicit system directives.
3. **Ephemeral User Credentials**: Plaintext passwords are never saved to SQLite/PostgreSQL tables.
4. **Isolated Static Storage**: Raw media captures and intermediate assets are strictly inaccessible from public HTTP endpoints. Video delivery requires valid HMAC signatures.

---

## 3. Reporting a Vulnerability

If you discover a security vulnerability in Premiere:
1. Do **not** disclose it publicly or file a public GitHub issue.
2. Email full reproduction steps and exploit scenario to `security@premiere.dev`.
3. The security team will acknowledge receipt within 24 hours and issue a patch within 72 hours.
