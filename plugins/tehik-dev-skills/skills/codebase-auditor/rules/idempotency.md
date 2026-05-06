---
trigger: always_on
---

# IDEMPOTENCY

## What is idempotency?
An idempotent operation is one that can be executed multiple times without changing the outcome (server state and side effects) after the first successful completion. This is critical when building reliable, fault-tolerant distributed systems (for example, when dealing with network outages and `retries`).

## Idempotency of HTTP Methods
- **Naturally idempotent:** `GET`, `PUT`, `DELETE`, `HEAD`, `OPTIONS`
- **Non-idempotent:** `POST`, `PATCH`

> **Note!** All critical `POST` and `PATCH` operations (or potentially unsafe `PUT` operations) **must implement the Idempotency-Key pattern**. Particular care is required for payments, data submissions, and triggers that change system state.

## Idempotency-Key Pattern

When a client sends a non-idempotent request (e.g. `POST /api/v1/payments`), it must include a unique ID in the header:
```http
POST /api/v1/payments
Idempotency-Key: 8a5d3f20-1b4e-4e78-9e5d-1f6cc9e0b1d3
```

### Server-side logic flow:
1. **Header check:** Is `Idempotency-Key` present? If not and the endpoint requires it, return `400 Bad Request`.
2. **Locking:** Lock the given key to prevent parallel requests (e.g. Redis `SETNX` or a database unique index / advisory lock with status `IN_PROGRESS`).
3. **Request state check:** State is recorded in the idempotency store (e.g. Redis, database):
   - **If the key exists and status is `COMPLETED`:** Immediately return the same HTTP status code and JSON response stored on the first attempt. **Do not run business logic again.**
   - **If the key exists and status is `IN_PROGRESS`:** Return `409 Conflict` (or, under favorable conditions, wait/block until processing finishes).
   - **If there is no key:** Proceed to step 4.
4. **Processing and storage:**
   - Execute business logic (preferably inside an atomic database transaction).
   - After a successful transaction, store a copy of the response (HTTP status, body) and set status to `COMPLETED`. Set an expiration (TTL, e.g. 24h).
   - Return the response to the original client.

## Database-Level Idempotency

1. **Unique indexes (unique constraints):**
   - Protect the system even if the API-layer `Idempotency-Key` mechanism fails (defense in depth).
   - Example: A user submits a report where `report_submission(report_id, user_id)` must be unique when each report can have only one submission.

2. **Idempotent migrations (DDL/DML):**
   - All SQL migrations (e.g. Flyway, Alembic) must be safe to run twice without failing (in most engines `IF NOT EXISTS` or conditional checks in the script). Read more: `database.md` → **Migrations**.

3. **Optimistic locking:**
   - For updates (`PUT`, `PATCH`), use a version column (`version` / `updated_at`).
   - `UPDATE table SET values, version = 2 WHERE id = 1 AND version = 1;`
   - If `affected_rows == 0`, an intervening update occurred or the row did not exist.

## Error Handling and Edge Cases
* **Transient errors (5xx class, network issues):** Do **not** save `COMPLETED` status. The client's `retry` must reach business logic again.
* **Validation errors (4xx):** Should a problematic request's `Idempotency-Key` be stored? Prefer leaving it unstored so the client can fix the error and retry with the same key; **beware** of flooding the system with identical requests (or store the exceptional result with a fixed TTL).
* **Reusing Idempotency-Key with a new request body:** If the client retries with the same key but a new / different payload (e.g. POST body changed), return `400 Bad Request` (key and body mismatch). This is easy to enforce by comparing the request `hash` with the original.

## Client Obligations
* The client must generate a key with sufficient entropy (preferably **UUID v4**).
* On retry (**Retry**), the client must use the **exact same** `Idempotency-Key` value on the new attempt.
* After the operation is first initialized, the payload must not be changed for the same key again.
