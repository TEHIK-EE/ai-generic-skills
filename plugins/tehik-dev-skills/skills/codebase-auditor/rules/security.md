---
trigger: always_on
---

# SECURITY

## Secrets management

* **ABSOLUTELY FORBIDDEN** to store passwords, API keys, certificates, or other sensitive information in code, configuration files, or commit history
* Secrets are stored as follows:
  * Local development: `.env` file (always in `.gitignore`)
  * CI/CD: GitLab CI/CD masked variables
  * Production: environment variables, HashiCorp Vault, AWS Secrets Manager, etc.
* Use an `.env.example` file to document all required variables (without actual values)
* If a secret is accidentally committed: **rotate it immediately** — deleting it from git history alone is not enough

## Authentication and authorisation

### Web application authentication — BFF pattern (Backend for Frontend)

> **A JWT token must never be sent to the browser.** Even storing a JWT in an `HttpOnly` cookie is risky — the token lives on the client side and is exposed to theft. Use the **BFF pattern**.

```
┌─────────┐   opaque session cookie   ┌─────────┐   JWT access_token   ┌──────────┐
│ Browser │ ◄─────────────────────────►  │   BFF   │ ──────────────────►  │ Backend  │
└─────────┘                              └─────────┘                       └──────────┘
                                              │
                                    Stores tokens server-side
                                    (Redis / in-memory store)
```

**How it works:**
1. The user authenticates via the BFF (OAuth 2.0 + OIDC Authorization Code Flow + PKCE)
2. The BFF exchanges the authorization code for `access_token` + `refresh_token` **on the server side**
3. Tokens are stored **only on the server** (e.g. in a Redis session store)
4. The browser receives only an **opaque session cookie** (`HttpOnly`, `Secure`, `SameSite=Strict`)
5. When the browser calls the BFF, the BFF exchanges the session cookie for a JWT and forwards it to the backend API

**Cookie requirements:**
```
Set-Cookie: session=<opaque-id>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=3600
```

* `HttpOnly` — JavaScript cannot access the cookie (XSS protection)
* `Secure` — HTTPS only
* `SameSite=Strict` — CSRF protection
* The session is invalidated server-side on logout and on expiry

**Passwords:** **Argon2id** (preferred) or **bcrypt** (cost ≥ 12) — not MD5/SHA1/SHA256

**Principle of least privilege:** a user or service has only the permissions it needs

### Machine-to-machine (M2M) APIs

* Use **OAuth 2.0 Client Credentials Flow** — a JWT `access_token` is acceptable because there is no browser
* RS256 signature (not HS256 with a shared secret)
* Short `access_token` lifetime (max 15 min), refreshed automatically

## Input validation

* Validate **at every layer**: API → business logic → database
* Use schema-based validation (e.g. Zod, Joi, Pydantic, Bean Validation)
* **Always** use parameterized queries for SQL — no string concatenation
* File uploads: validate type, size, and content (not only the file extension)
* When rendering HTML: always escape input (XSS prevention)

## OWASP Top 10 checklist

When adding new functionality, review the relevant items:

| # | Risk | Mitigations |
|---|------|-------------|
| A01 | Broken Access Control | Authorisation on every endpoint; do not trust the client |
| A02 | Cryptographic Failures | TLS 1.2+, strong algorithms; do not roll your own crypto |
| A03 | Injection | Parameterized queries, ORM, validation |
| A04 | Insecure Design | Threat modelling, defence in depth |
| A05 | Security Misconfiguration | Remove hard-coded defaults |
| A06 | Vulnerable Components | `npm audit`, `pip-audit`, Dependabot |
| A07 | Auth Failures | Account lockout, rate limiting, MFA support |
| A08 | Data Integrity Failures | Signed artefacts, SAST/DAST in CI |
| A09 | Logging Failures | Do not log sensitive information; log all authorisation events |
| A10 | SSRF | Whitelist external URLs; block internal addresses |

## Dependency security

* Mandatory in the CI pipeline: `npm audit --audit-level=high` / `pip-audit` / `trivy`, etc.
* Critical-severity vulnerabilities block the build
* Update dependencies regularly (Dependabot / Renovate Bot)

## Rate limiting and brute-force protection

* **Authentication endpoints** (login, password reset): max 5 attempts / 15 min per IP
* Account lockout: after N failed attempts, lock the account temporarily (e.g. 15 min)
* Rate limit response: `429 Too Many Requests` + `Retry-After` header
* Prefer implementation at the API gateway layer (e.g. nginx `limit_req`, Kong, AWS WAF)
* Consider adding a CAPTCHA after N failed attempts

## Log security

* ❌ Do not log: passwords, tokens, credit card data, personal data (GDPR)
* ✅ Log: authentication events, failed attempts, material business events
* Log entries in a structured format (JSON) including: timestamp, level, requestId, userId (not personal data)
* For detailed logging rules, see `observability.md`

## HTTP security headers

Every web application must configure:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

### Content-Security-Policy (CSP)

CSP is the most important XSS mitigation. **Do not use only `default-src 'self'`** — tailor CSP to the application’s needs:

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

* ❌ `script-src 'unsafe-inline' 'unsafe-eval'` — defeats the purpose of CSP
* ✅ Use a nonce-based (`'nonce-abc123'`) or hash-based approach for inline scripts
* Start with the `Content-Security-Policy-Report-Only` header to test without blocking
* Configure `report-uri` / `report-to` for CSP violation reporting
