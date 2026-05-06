---
trigger: always_on
---

# API DESIGN

## REST principles

* **Resources as nouns, plural:** `/api/v1/users`, `/api/v1/reports`, `/api/v1/reports/{id}/approvals`
* **Do not use verbs in the URL:** ❌ `/api/getUser`, ❌ `/api/createReport`
* **Hierarchy:** at most **3 levels** deep (`/resources/{id}/sub-resources/{subId}`)
* **Relationship actions:** `POST /api/v1/reports/{id}/submit`, `POST /api/v1/reports/{id}/approve`

## HTTP method semantics

| Method | Semantics | Idempotent | Body |
|--------|-----------|------------|------|
| `GET` | Read, search | ✅ | ❌ |
| `POST` | Create, action | ❌ (see below) | ✅ |
| `PUT` | Full replacement | ✅ | ✅ |
| `PATCH` | Partial update | ❌ (see below) | ✅ |
| `DELETE` | Delete | ✅ | ❌ |

### POST and PATCH idempotency — Idempotency-Key

> **Detailed server logic flow and edge cases:** see `idempotency.md`.

Because `POST` and `PATCH` are not inherently idempotent, a network interruption can cause duplicate operations (e.g., duplicate charges, duplicate submissions). To protect against this:

```
POST /api/v1/reports
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

* The client generates a UUID v4 for each unique operation
* The server stores the `Idempotency-Key` together with the response (e.g., Redis, TTL 24h)
* A repeat request with the same key returns the original response without executing the operation again
* Mandatory for all critical `POST` requests: payments, submissions, order creation

## HTTP status codes

```
200 OK              — Successful GET, PUT, PATCH
201 Created         — Successful POST (add Location header)
204 No Content      — Successful DELETE
400 Bad Request     — Validation error (client fault)
401 Unauthorized    — Authentication missing or invalid
403 Forbidden       — Authenticated but not authorized
404 Not Found       — Resource does not exist
409 Conflict        — Resource already exists / version conflict
422 Unprocessable   — Semantic error (business logic error)
429 Too Many Req.   — Rate limit exceeded
500 Internal Error  — Server error (not client fault)
```

## API versioning

* Version in URL path: `/api/v1/`, `/api/v2/`
* Old versions are deprecated, not removed immediately
* Breaking change → new major version
* Additive change (new fields) → backward compatible, no new version required

## Unified error format (RFC 9457 Problem Details)

> **See also:** `error-handling.md` for specific error classes (AppError, etc.) and the central error handler implementation.

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "The request body contains invalid fields.",
  "instance": "/api/v1/reports/42",
  "errors": [
    { "field": "amount", "message": "Amount must be greater than 0" }
  ]
}
```

* All API errors follow the same structure
* `detail` is human-readable, `type` is a machine-readable URI
* Do not expose stack traces in production

## Pagination, filtering, sorting

```
GET /api/v1/reports?page=1&pageSize=20&sort=createdAt:desc&status=SUBMITTED
```

* `page` (1-based) + `pageSize` (default 20, max 100)
* Response includes metadata:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 143,
    "totalPages": 8
  }
}
```

## Request/response principles

* **Input:** validate all required fields; return **all** validation errors at once (not only the first)
* **Output:** return only the necessary fields — do not return sensitive fields (e.g., password hash, national ID)
* Dates: **ISO 8601** format (`2024-03-15T20:51:23+02:00`)
* Identifiers: **UUID v7** (not incremental integer IDs in a public API) — timestamp-based, sortable, better index performance; UUID v4 only in security contexts (sessions, CSRF)
* Money amounts: **integer (cents)** or `string` — not `float`

## Health check

Every API service must expose:

```
GET /health         → 200 { "status": "UP" }       (liveness)
GET /health/ready   → 200 { "status": "READY" }    (readiness)
```

* **Liveness** (`/health`): is the process running? Kubernetes uses this to decide on restarts.
* **Readiness** (`/health/ready`): can the service serve traffic? (database, cache, external services available)
* The readiness check must be lightweight (ping/connection check, not a full query)
* ❌ Do not return sensitive information in health checks (version is OK, internal structure is not)

## Rate limiting

* Critical endpoints (authentication, registration, password change) **must** be rate-limited
* Response headers:

```
X-RateLimit-Limit: 100          — maximum requests per time window
X-RateLimit-Remaining: 42       — remaining requests
X-RateLimit-Reset: 1710532800   — end of time window, UNIX timestamp
Retry-After: 30                 — (in 429 response) seconds before next attempt
```

* On rate limit exceeded return `429 Too Many Requests` with the `Retry-After` header
* Implement rate limiting at the API gateway / reverse proxy level rather than in the application, except for justified edge cases

## CORS (Cross-Origin Resource Sharing)

* **In production:** explicitly define allowed origins — ❌ not `Access-Control-Allow-Origin: *`
* **Preflight caching:** `Access-Control-Max-Age: 86400` (24h) — reduces the number of OPTIONS requests
* **Credentials:** when cookies are sent, `Access-Control-Allow-Credentials: true` must be set and the origin cannot be `*`
* Define allowed methods and headers minimally (do not open everything up)

```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization, X-Request-Id, Idempotency-Key
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
```

## Timeout and retry (client-side)

* Set an **explicit timeout** on every outbound HTTP call (recommended: 5–30s depending on the service)
* **Retry** only for idempotent operations (`GET`, `PUT`, `DELETE`) — ❌ not `POST` without Idempotency-Key
* Use **exponential backoff**: 1s → 2s → 4s (max 3 attempts)
* Use **jitter** (random delay) to avoid the thundering herd effect

## API documentation

* Every endpoint documented as an **OpenAPI 3.x** specification
* Specification under version control alongside code
* Swagger UI available in development and staging (not in production)
