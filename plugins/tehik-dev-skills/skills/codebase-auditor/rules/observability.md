---
trigger: always_on
---

# OBSERVABILITY

Three pillars: **logs**, **metrics**, **tracing**. Every production application must cover at least logs and metrics.

## Logging

### Structured logging

* Logs are in **JSON format** — not unstructured plain-text lines
* Field names follow the **[Elastic Common Schema (ECS)](https://www.elastic.co/guide/en/ecs/current/index.html)** convention — ensures a consistent structure across services and native Elastic/Kibana support
* ECS-compatible logs also work with OpenTelemetry Semantic Conventions (schemas converge)
* Use a language-specific ECS formatter: `ecs-logging-java`, `ecs-logging-nodejs`, `ecs-logging-python`

**Minimal ECS-compatible log entry:**

```json
{
  "@timestamp": "2024-03-15T14:30:00.123Z",
  "log.level": "ERROR",
  "message": "Failed to process report submission",
  "service.name": "report-api",
  "trace.id": "abc-550e8400-e29b-41d4",
  "user.id": "usr-a716-446655440000",
  "error.type": "ValidationError",
  "error.message": "Amount must be greater than 0",
  "event.action": "report-submission",
  "event.outcome": "failure"
}
```

### Log levels

| Level | Usage | Enabled in production by default |
|-------|-------|----------------------------------|
| `ERROR` | Unexpected error — requires attention (server error, database connection lost) | ✅ |
| `WARN` | Expected error — client error, business rule violation, slow request | ✅ |
| `INFO` | Important business event — user signed in, report submitted, deployment completed | ✅ |
| `DEBUG` | Detailed technical information — request payloads, intermediate results | ❌ (development only) |
| `TRACE` | Finest-grained — input/output per function | ❌ (debugging only) |

### Correlation ID (Request ID / Trace ID)

* Every incoming HTTP request receives a **unique identifier**
* In ECS: `trace.id` (consistent across the entire request path) + `transaction.id` (single operation)
* The identifier is added to **every log entry** in that request’s context
* Propagate downstream via headers (`X-Request-Id` or `traceparent` per the W3C standard)
* Return `X-Request-Id` in the response header to the client (support can use it to locate the issue)

```
Browser → BFF (trace.id: abc-123) → Backend API (X-Request-Id: abc-123) → Database
              ↓ log: abc-123              ↓ log: abc-123
```

### What to log

* ✅ Authentication events (sign-in, sign-out, failed attempt)
* ✅ Authorization denials (403)
* ✅ Important business events (resource created, submitted, approved)
* ✅ Calls to external services (URL, method, response time, status)
* ✅ Slow requests (> configured threshold)
* ✅ Application startup and shutdown (startup, graceful shutdown)

### What NOT to log

* ❌ Passwords, tokens, API keys
* ❌ Personal data (national ID, bank account, health data) — GDPR
* ❌ Credit card numbers (PCI DSS)
* ❌ Full HTTP bodies (may contain sensitive information) — log metadata only

> See also `security.md` → Log security.

## Metrics

### Mandatory metrics (RED method)

Every API service must expose:

| Metric | Description | Example |
|--------|-------------|---------|
| **Rate** | Number of requests per unit of time | `http_requests_total{method, path, status}` |
| **Errors** | Proportion of errors | `http_errors_total{method, path, status}` |
| **Duration** | Request duration | `http_request_duration_seconds{method, path}` (histogram) |

### Business metrics

* Counter of important business events (e.g. number of submitted reports, number of approvals)
* Queue length / backlog (when using messaging)
* External service response time and success rate

### Metrics format

* Preferred: **OpenTelemetry** (OTLP) or **Prometheus** format
* Endpoint: `/metrics` (Prometheus scrape) — ❌ not publicly exposed in production

## Tracing (Distributed Tracing)

### When mandatory

* Microservices architecture (>2 services)
* When a single user request traverses multiple systems

### Principles

* Use the **OpenTelemetry SDK** (language-specific instrumentation)
* Each request creates a **trace** with **spans** for each significant operation
* Trace ID is propagated between services (`traceparent` header, W3C Trace Context)

```
Trace: abc-123
├── Span: BFF /api/v1/reports (120ms)
│   ├── Span: Auth check (5ms)
│   └── Span: Backend API call (110ms)
│       ├── Span: DB query: findReport (15ms)
│       └── Span: DB query: insertApproval (8ms)
```

## Alerting (notifications)

### Mandatory alerts

* **Increase in 5xx errors** — when the error rate exceeds the threshold (e.g. >1% over 5 minutes)
* **Increase in response time** — when p95 latency exceeds the SLA (e.g. >2s)
* **Health check failure** — health endpoint does not respond
* **Disk / memory utilization** — >85% usage

### Alerting principles

* Every alert must be **actionable** — when you get an alert, you must know what to check
* Do not create alerts that are ignored (alert fatigue)
* Alert channels: Slack/Teams + PagerDuty/Opsgenie for critical incidents

## Health check

Every service must expose:

```
GET /health         → 200 { "status": "UP" }     (liveness — whether the process is running)
GET /health/ready   → 200 { "status": "READY" }  (readiness — whether it can serve traffic)
```

* **Liveness:** does the application respond? (Kubernetes restart trigger)
* **Readiness:** are the database, cache, and external services reachable? (Kubernetes traffic removal)
* Readiness checks **must not** be expensive operations (ping, not a full query)
* ❌ Do not return sensitive information in health checks (versions are OK, internal structure is not)
