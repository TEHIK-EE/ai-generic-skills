---
trigger: always_on
---

# ERROR HANDLING

## General principles

* **Fail fast:** validate inputs and preconditions as early as possible. If data is invalid, stop immediately — do not proceed with partial or inconsistent data.
* **Do not swallow exceptions:** an empty `catch` block is **strictly forbidden**. Every exception must be logged, transformed into a more appropriate form, or rethrown.
* **Exceptions are for exceptional situations:** do not use exceptions for control flow (e.g. "user not found" in business logic is an expected outcome, not an exceptional one).
* **Do not return `null` to signal errors:** use dedicated types (`Optional`, `Result`, `Either`) or exceptions. Using `null` for "not found" hides problems.

## Custom error classes

Use a project-specific hierarchy of error classes that distinguishes **client errors** from **server errors**:

```
AppError (base class)
├── ValidationError       (400 — input validation)
├── AuthenticationError   (401 — authentication failure)
├── AuthorizationError    (403 — insufficient permissions)
├── NotFoundError         (404 — resource does not exist)
├── ConflictError         (409 — duplicate, version conflict)
├── BusinessRuleError     (422 — business rule violation)
└── InternalError         (500 — unexpected server error)
```

Each error class includes:
* `message` — human-readable description
* `code` / `type` — machine-readable identifier (e.g. `VALIDATION_ERROR`)
* `details` — supplementary information (field name, constraint description)

### TypeScript example

```typescript
export abstract class AppError extends Error {
  abstract readonly statusCode: number;
  abstract readonly code: string;

  constructor(message: string, public readonly details?: Record<string, unknown>) {
    super(message);
    this.name = this.constructor.name;
  }
}

export class ValidationError extends AppError {
  readonly statusCode = 400;
  readonly code = 'VALIDATION_ERROR';
}

export class NotFoundError extends AppError {
  readonly statusCode = 404;
  readonly code = 'NOT_FOUND';
}
```

### Java example

```java
public abstract class AppException extends RuntimeException {
    private final String code;
    private final int statusCode;

    protected AppException(String message, String code, int statusCode) {
        super(message);
        this.code = code;
        this.statusCode = statusCode;
    }

    // getters
}

public class ValidationException extends AppException {
    public ValidationException(String message) {
        super(message, "VALIDATION_ERROR", 400);
    }
}
```

## Global error handler (API)

> **See also:** `api.md` for API responses and the RFC 9457 Problem Details standard.

Every API application must include a **central error handler** that:

1. Catches all unhandled exceptions
2. Maps them to HTTP responses in a consistent format (see `api.md` → RFC 9457)
3. Logs the error at an appropriate level (`WARN` for client errors, `ERROR` for server errors)
4. **Does not expose** stack traces, internal class names, or database error messages in production

```typescript
// Express.js example
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof AppError) {
    logger.warn({ err, requestId: req.id }, err.message);
    return res.status(err.statusCode).json({
      type: `https://api.example.com/errors/${err.code.toLowerCase()}`,
      title: err.name,
      status: err.statusCode,
      detail: err.message,
      instance: req.originalUrl,
    });
  }

  logger.error({ err, requestId: req.id }, 'Unhandled error');
  return res.status(500).json({
    type: 'https://api.example.com/errors/internal-error',
    title: 'Internal Server Error',
    status: 500,
    detail: 'An unexpected error occurred.',
    instance: req.originalUrl,
  });
});
```

## Transaction error handling

* Database transaction error → **rollback the entire transaction**, not only the last step
* Optimistic locking conflict → inform the user; do not retry silently
* Idempotency-Key duplicate request → return the original response (see `api.md`)

## External service errors

* **Timeout:** set an explicit timeout on every outbound call (e.g. 5s)
* **Retry:** use exponential backoff (base 1s, max 3 attempts) only for idempotent operations
* **Circuit breaker:** for a service with sustained failures, stop calling it temporarily (see `observability.md` for metrics)
* **Fallback:** define what happens when an external dependency is unavailable — can the user get a partial response, or should an error be returned?

## Prohibitions

* ❌ Empty `catch` block (silent error swallowing)
* ❌ `catch (Exception e) { return null; }` — hides the root cause
* ❌ Returning a stack trace in an API response in production
* ❌ Logging and rethrowing (`log` + `throw`) — the error is logged twice
* ❌ Driving business logic with exceptions (`try { findUser(); } catch { createUser(); }`)
