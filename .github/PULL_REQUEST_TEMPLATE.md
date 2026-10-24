## Description
<!-- Provide a concise description of the changes and the architectural rationale. -->

## Security Checklist (Mandatory)
Every pull request must pass this "Secure by Default" verification:

### 1. New Endpoints & Input Handling
- [ ] Schema-level validation applied (Pydantic / TypeScript types)
- [ ] Allowlist-based validation used instead of blocklists
- [ ] Strict length, format, and type constraints enforced
- [ ] Route parameters validated with strict regex patterns (e.g. UUID)
- [ ] Error messages do not leak stack traces or internal secrets

### 2. External Calls & SSRF Protection
- [ ] Outgoing network requests use `validate_public_url()`
- [ ] Loopback (`127.0.0.0/8`), private subnets, and cloud metadata (`169.254.169.254`) blocked
- [ ] DNS rebinding and redirects re-validated before fetching
- [ ] Timeouts and response size caps configured on all HTTP/subprocess calls

### 3. Authentication & Access Control
- [ ] Object-level authorization enforced (no unauthorized resource access)
- [ ] Signed tokens used for binary media downloads with expiry
- [ ] No unauthenticated static file directories exposed

### 4. Secrets & Credentials
- [ ] No plaintext secrets or passwords in code, logs, or database records
- [ ] Passwords scrubbed immediately after transient use
- [ ] Environment variables verified at startup

### 5. Headless Browser (Playwright) Security
- [ ] Page content treated as untrusted and hostile
- [ ] Context configured with `permissions=[]` and `accept_downloads=False`
- [ ] Host filesystem access disabled (`--disable-local-file-access`)
- [ ] Hard memory cap configured (`--js-flags=--max-old-space-size=512`)

### 6. Dependencies & Supply Chain
- [ ] New packages audited via `pip-audit` / `npm audit`
- [ ] Exact dependency versions pinned in lockfiles
