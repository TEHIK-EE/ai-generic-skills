---
name: run-tests
description: "Run linting, tests, and coverage checks to verify code is ready to commit. Use whenever code has changed and needs verification — before commits, after fixing a bug, implementing a feature, or when asked to verify the test suite. Also trigger on: 'run tests', 'check if tests pass', 'is linting clean', 'verify coverage', 'are tests green', 'make sure nothing is broken'."
---

# Running Tests

## Safety rules

- Do not commit code until all issues (lint, tests, coverage) are resolved.
- Never use `.skip()`, `@Disabled`, or `pytest.mark.skip` as a workaround without a linked ticket reference.
- Never skip or disable a failing test — diagnose and fix the root cause.
- If a test appears flaky, run it once more; if it still fails, treat it as a real failure.
- Coverage below threshold is a blocker, not a warning — add tests before proceeding.

---

## Step 0 — Discover available commands

Before running anything, check what the project actually exposes — assumed command names often don't exist and will cause false failures.

- **JS/TS:** scan `package.json` `scripts` block for keys like `lint`, `lint:fix`, `test`, `test:unit`, `test:integration`, `test:e2e`, `test:coverage`
- **Java/Kotlin:** check `build.gradle` / `pom.xml` for available task names and plugins (JaCoCo, ktlint, Checkstyle)
- **Python:** check `Makefile`, `pyproject.toml` `[tool.pytest.ini_options]`, or `tox.ini`

Use only commands that exist. If `test:unit` is absent but `test` is present, use that. Skip any step whose command isn't defined.

---

## Step 1 — Linting

Run the linter matching the project's tooling:

```bash
# TypeScript/JavaScript
npm run lint

# Python
ruff check . || flake8 .

# Java/Kotlin
./gradlew ktlintCheck || ./mvnw checkstyle:check
```

If linting fails:
1. Try auto-fix first — many issues can be resolved automatically:
   ```bash
   # TypeScript/JavaScript
   npm run lint:fix   # or: npx eslint --fix .

   # Python
   ruff check --fix .

   # Java/Kotlin
   ./gradlew ktlintFormat
   ```
2. Re-run linting to confirm it's clean.
3. If issues remain after auto-fix, fix them manually before continuing — do not leave lint errors unresolved.

---

## Step 2 — Unit tests + coverage

Run unit tests with coverage enabled in a single pass (avoids running the suite twice):

```bash
# TypeScript/JavaScript — prefer a single coverage-enabled run
npm run test:coverage   # if defined; otherwise:
npm run test:unit -- --coverage

# Python
pytest tests/unit/ --cov=. --cov-report=term-missing

# Java/Kotlin — JaCoCo generates the report alongside the test run
./gradlew test jacocoTestReport   # Maven: ./mvnw test
```

---

## Step 3 — Integration tests

Run integration tests if the project structure includes them:

```bash
# TypeScript/JavaScript
npm run test:integration

# Python
pytest tests/integration/

# Java/Kotlin
./gradlew integrationTest
```

Skip this step if no integration test command or directory exists.

---

## Step 4 — E2E tests (if applicable)

Run E2E tests only when a critical user flow was modified or the project runs E2E on every commit. Skip by default for routine changes — E2E suites are slow and reserved for critical flows.

```bash
# TypeScript/JavaScript
npm run test:e2e   # Playwright / Cypress / similar
```

---

## Step 5 — Review coverage report

Read the coverage output from Step 2 (no need to re-run tests). Verify:

- New code: ≥ **80%** line coverage
- Critical business-logic modules: ≥ **90%**
- Coverage has not dropped compared to `develop`

> ⚠️ Coverage below the required threshold is a blocker. Add tests for uncovered paths before proceeding — do not merge with insufficient coverage.

For Java/Kotlin, open `build/reports/jacoco/test/html/index.html` or read the console summary.

---

## Step 6 — Reporting

Provide a summary:

```
Test results:
- Linting:              ✅ / ❌ [errors]
- Unit tests:           ✅ X passed / ❌ Y failed
- Integration tests:    ✅ / ❌ / ⏭ not applicable
- E2E tests:            ✅ / ❌ / ⏭ skipped
- Coverage:             X% (requirement ≥ 80%)
- Status:               ✅ Ready to commit / ❌ Needs fixes
```

---

## When things fail

Do not commit until all issues are resolved. Distinguish the failure type to respond correctly:

- **Compilation / build error** — nothing else is reliable until this is fixed; address it before re-running.
- **Failing test** — diagnose the root cause and fix the code or the test. Do not skip or disable the test.
- **Apparently flaky test** — run once more; if it still fails, treat it as a real failure and investigate.
- **Coverage below threshold** — add tests for the uncovered paths before proceeding.

> ⚠️ Never use `.skip()`, `@Disabled`, or `pytest.mark.skip` as a workaround without a linked ticket reference.
