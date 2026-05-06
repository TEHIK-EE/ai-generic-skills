---
trigger: always_on
---

# TESTING

## Test pyramid

```
         /‾‾‾‾‾‾‾\
        /   E2E    \        ← few, slow, critical user flows
       /‾‾‾‾‾‾‾‾‾‾‾\
      / Integration  \     ← moderate volume, API + DB layer
     /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
    /    Unit Tests    \    ← many, fast, isolated
   /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
```

## Coverage requirements

* Minimum line coverage for new code: **80%**
* Critical business logic modules: **90%+**
* Coverage report is generated automatically in CI
* Coverage regression compared to `develop` blocks merging the MR

## Naming tests

### TypeScript / JavaScript (Jest/Vitest)
```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should throw ValidationError when email is invalid', () => { ... });
    it('should return created user with hashed password', () => { ... });
  });
});
```

### Java / Kotlin (JUnit 5)
```java
// Pattern: methodName_stateUnderTest_expectedBehavior
@Test
void createUser_withInvalidEmail_throwsValidationException() { ... }

@Test
void createUser_withValidData_returnsUserWithHashedPassword() { ... }
```

### Python (pytest)
```python
def test_create_user_raises_validation_error_for_invalid_email(): ...
def test_create_user_returns_hashed_password_on_success(): ...
```

## Mocking principles

* **Mock only external dependencies:** databases, HTTP APIs, file system, clock
* **Do not mock** your own business logic classes — if you feel the need, the design is wrong
* Use the **Test Double** hierarchy:
  * `Stub` — returns fixed values
  * `Mock` — verifies interactions
  * `Fake` — lightweight in-memory implementation (e.g. H2, Testcontainers)
* Avoid over-specification (too many `verify()` calls)

## Test Data Builder pattern

Use `Builder` or `Factory` patterns to create test data:

```typescript
// Good
const user = UserBuilder.aUser()
  .withEmail('test@example.com')
  .withRole('ADMIN')
  .build();

// Bad — direct constructor in test; causes fragility
const user = new User('1', 'test@example.com', 'hash', 'ADMIN', new Date());
```

## Rules for writing tests

* Each test is **self-contained** — does not depend on the order of other tests
* Use the **AAA pattern:** `Arrange → Act → Assert`
* One test verifies **one behavior** (multiple asserts are OK if they check the same thing)
* Readability of test code matters as much as production code
* Integration tests use **Testcontainers** or in-memory databases — not a real production database
* E2E tests cover only **critical user flows** (e.g. login, core functionality)

## Test data cleanup

* Every integration test must **clean up its own data** (self-contained principle)
* Preferred strategies:
  * **Transaction rollback:** the test runs in a transaction that is rolled back at the end (fastest)
  * **Truncate / delete:** test data is cleaned in `beforeEach` / `afterEach` hooks
  * **Testcontainers:** each test class gets a fresh database container
* ❌ Do not rely on fixed data that assumes a specific database state

## Contract testing

In a microservices architecture (>2 services), use **contract tests** to verify APIs between services:

* The consumer defines expectations for the provider’s API
* The provider validates that its API meets every consumer’s expectations
* Tools: **Pact**, Spring Cloud Contract, Specmatic
* Contract tests run in CI — breaking changes are caught before deploy

## Performance testing

* Critical API endpoints should be **load tested** before production
* Define acceptable thresholds: maximum response time (e.g. p95 < 500ms), throughput (e.g. 100 req/s)
* Tools: k6, Gatling, JMeter, Locust
* Performance tests are run in CI on a regular schedule (e.g. weekly) or before a release

## Prohibitions

* ❌ Tests that depend on time without a time abstraction
* ❌ Tests that issue real HTTP requests to external services
* ❌ `Thread.sleep()` / `setTimeout` in tests without deterministic waiting
* ❌ Shared mutable state between tests
* ❌ Ignoring tests (`@Disabled`, `.skip()`, `@pytest.mark.skip`) without a ticket reference
