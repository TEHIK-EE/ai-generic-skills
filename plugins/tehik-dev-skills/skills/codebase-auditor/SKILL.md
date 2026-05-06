---
name: codebase-auditor
description: "Performs a deterministic compliance audit of the current workspace against the project's own architecture and quality rules. Use this whenever you want to verify code quality — before a release, major merge, or PR review, when onboarding to a new codebase, when asked to 'audit the code', 'check compliance', 'review code quality', or 'validate standards'. Even if the user says 'just take a quick look', trigger this skill — a structured audit always beats an ad-hoc check."
---

# Codebase Audit

## When this applies

Use this skill when:
- Asked to "audit the code", "check compliance", "review code quality", or "validate standards"
- Before a release, major merge, or PR review
- During onboarding to an unfamiliar codebase
- When the user says "just take a quick look" — a structured audit beats an ad-hoc check

Do NOT use this skill for:
- Spot-checking a single file or function (read and assess directly)
- Reviewing your own just-written code (use the review sub-skill of your workflow instead)
- Auditing external proposals or vendor documents (use `/validate-external-proposal`)

## Grounding Documents (Sources of Truth)

Before starting the audit you MUST load rules from one of the canonical sources below (in priority order):

1. Project `rules/` directory (`*.md` files)
2. Project `.agent/rules/` directory (`*.md` files)
3. Cursor export directory `.cursor/rules/` (`*.mdc` files; load their contents as rules)
4. Global file `~/.claude/CLAUDE.md`

Pick the first source that exists and contains rules. If the source is a directory, load **all** rule files in it (not a fixed list).  
If no source is found: **stop the audit and report an error** (list the paths checked).

## Goal

Produce a repeatable, evidence-based audit report that verifies the codebase against the project's own architecture and quality rule set.

# Execution Protocol

## Phase 1 — Inventory

1. Inspect the project structure at a high level (list the repository root)
2. Identify:
   - Programming language and framework in use
   - Database technology (required for `database.md` rule checks)
   - Test framework (required for `testing.md` checks)
   - CI/CD configuration file (e.g. `.gitlab-ci.yml`)
   - Documentation locations (`docs/`, `README.md`, `CHANGELOG.md`)

## Phase 2 — Scanning

3. Scan the codebase systematically by the categories listed below
4. For each finding record: **file path + line** (evidence) OR **absence** (evidence)

## Phase 3 — Audit

5. Compare findings against the grounding documents' requirements
6. Use only binary statuses: `[PASS]`, `[FAIL]`, `[N/A]`
   - `[PASS]`: requirement met — you **must** cite concrete evidence
   - `[FAIL]`: requirement not met — describe what is missing or wrong
   - `[N/A]`: requirement does not apply in this project / technology context

## Phase 4 — Report

7. Generate the report in the format described below

## Determinism Constraints

- **Direct quotes:** every finding MUST reference a specific rule source and rule (e.g. `security.md → BFF pattern` or `GEMINI.md → Source: rules/security.md`)
- **Binary status:** use only `[PASS]`, `[FAIL]`, `[N/A]`
- **Evidence before judgment:** every `[PASS]` must include a concrete file path or line of code
- **No hand-waving:** do not suggest generic "best practices" — only concrete requirements from the rule files
- **Category coverage:** every category ID listed below must appear in the output; if the rule source does not cover it, mark `[N/A]`

# Audit categories

## Code conventions (common.md)
- **CONV-01:** Names describe WHAT (not WHAT FOR/context) — no caller-context leakage in function/class names
- **CONV-02:** Comments explain WHY, not HOW — no comments that merely repeat the code
- **CONV-03:** All code, comments, and repo deliverables in English (unless project explicitly permits another language)
- **CONV-04:** SOLID and DRY applied — no unnecessary duplication, business logic separated from infrastructure

## Security (security.md)
- **SEC-01:** BFF pattern — JWT must not live in the browser
- **SEC-02:** Secrets — `.env.example` present, `.env` in gitignore
- **SEC-03:** Input validation at all layers
- **SEC-04:** HTTP security headers present — HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, CSP
- **SEC-05:** Password hashing (Argon2id / bcrypt cost ≥ 12)
- **SEC-06:** Rate limiting on auth/login/password-reset endpoints (max 5 attempts / 15 min)
- **SEC-07:** Dependency audit present in CI pipeline (`npm audit` / `pip-audit` / `trivy` or equivalent)

## Testing (testing.md)
- **TEST-01:** Unit tests present
- **TEST-02:** Coverage ≥ 80% (see coverage report or configuration)
- **TEST-03:** Test naming follows convention
- **TEST-04:** External dependencies are mocked
- **TEST-05:** No `Thread.sleep()` / `setTimeout` in tests
- **TEST-06:** Integration tests clean up own data (transaction rollback or beforeEach/afterEach hooks — no reliance on fixed DB state)

## API (api.md)
- **API-01:** Resources as plural nouns
- **API-02:** Uniform error format (RFC 9457 structure)
- **API-03:** API versioning in URL (`/api/v1/`)
- **API-04:** Idempotency-Key on critical POSTs (payments, submissions, order creation)
- **API-05:** OpenAPI specification present under `docs/api/`
- **API-06:** CORS allows only explicit origins in production (no `Access-Control-Allow-Origin: *`)

## Database (database.md)
- **DB-01:** Migration files present and under version control
- **DB-02:** Migrations idempotent (IF NOT EXISTS)
- **DB-03:** Primary keys use UUID v7
- **DB-04:** Audit fields (`created_at`, `created_by`, `updated_at`, `updated_by`) present
- **DB-05:** No `SELECT *` in queries
- **DB-06:** Critical tables have unique constraints as defense-in-depth idempotency (not only API-layer key check)
- **DB-07:** Optimistic locking (`version` column) on entities subject to concurrent updates

## CI/CD (ci-cd.md)
- **CI-01:** Pipeline stages in correct order (lint → test → build → scan → deploy)
- **CI-02:** Secrets in CI/CD variables, not in YAML
- **CI-03:** `latest` tag not used for production deploy

## Documentation (documentation.md)
- **DOC-01:** `README.md` present and contains required sections
- **DOC-02:** `CHANGELOG.md` present and follows Keep a Changelog format
- **DOC-03:** `docs/` folders present (`architecture/`, `api/`)
- **DOC-04:** `.env.example` present

## Version control (git.md)
- **GIT-01:** `.gitignore` covers IDE files, `node_modules/`, build artifacts, `.env`
- **GIT-02:** Commit messages follow Conventional Commits format (see git log)
- **GIT-03:** Pre-commit hooks configured (Husky, pre-commit framework, etc.)

## Error handling (error-handling.md)
- **ERR-01:** Custom error classes present (AppError hierarchy, etc.)
- **ERR-02:** Global error handler present (central API error handler)
- **ERR-03:** No empty catch blocks (search: empty catch)
- **ERR-04:** Stack traces not exposed in API responses in production

## Observability (observability.md)
- **OBS-01:** Structured logging (JSON format)
- **OBS-02:** Correlation/Request ID implemented
- **OBS-03:** Health check endpoints present (`/health`, `/health/ready`)
- **OBS-04:** Sensitive data not logged (passwords, tokens, PII)

# Output Format

## Codebase compliance audit

| ID | Rule | Status | Evidence from project | Rules file |
|:---|:-------|:--------|:----------------|:-----------|
| CONV-01 | Names describe WHAT, not context | [PASS/FAIL/N/A] | `src/services/UserService.ts:12` | common.md |
| SEC-01 | BFF pattern — JWT not in the browser | [PASS/FAIL/N/A] | `src/middleware/auth.ts:42` | security.md |
| ... | ... | ... | ... | ... |

### Summary

- **Passing:** [count] / [total]
- **Violations:** [count]
- **Critical violations:** [list — security and database FAILs]
- **Recommendations:** [at most 3 most important fixes, directly from the rule files]
