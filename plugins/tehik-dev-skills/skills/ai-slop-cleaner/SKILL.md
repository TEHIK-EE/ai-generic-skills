---
name: ai-slop-cleaner
description: "Detects and removes low-value AI-generated noise from code and documentation — redundant comments, dead helpers, duplicate blocks, weak naming, over-engineered wrappers, verbose docs. Use when the user asks to clean up messy code, reduce boilerplate, remove AI slop, simplify over-verbose documentation, remove dead code, remove unused helpers, or do a readability/noise-reduction pass. Supports audit-only and safe-fix modes."
---

# AI Slop Cleaner

## Progress checklist

```text
AI Slop Cleanup Progress
- [ ] Phase 1: Confirm scope and mode
- [ ] Phase 2: Scan target paths
- [ ] Phase 3: Classify findings by risk
- [ ] Phase 4: Apply only safe fixes (if mode=safe-fix)
- [ ] Phase 5: Run quality gates
- [ ] Phase 6: Produce final report
```

## Purpose

Reduce low-value generated noise without changing business behavior or API contracts.

This skill is for **targeted cleanup** in explicitly provided repositories/folders.

## When this applies

Use this skill when the user asks to:

- clean "AI slop" from code/docs
- remove repetitive generated boilerplate
- improve naming/readability in obviously mechanical sections
- run an audit-first pass before refactoring

Do not auto-apply this skill for feature development.

## Required inputs

Before starting, confirm:

1. **Target paths** (allowlist; one or more repo/folder paths).
2. **Mode**:
   - `audit-only` (report, no edits)
   - `safe-fix` (low-risk edits allowed)
3. **Scope limits**:
   - optional include/exclude globs
   - whether docs are included
4. **Output preference**:
   - summary only
   - full finding table + patch plan

## Safety rules (must follow)

Never auto-change in `safe-fix` mode:

- authentication/authorization logic
- cryptography/security controls
- DB schema/migrations
- API contracts and public DTOs
- concurrency/transaction logic

Never use destructive git operations.

If unsure whether change is behavior-preserving, classify as `needs-review` instead of editing.

## Workflow/command routing (required)

When code edits are needed, this skill must route through existing primary workflow/command IDs:

- `audit-only`: no code edits, no primary workflow required
- `safe-fix` with strictly behavior-preserving cleanup: use **`/refactor`**
- any cleanup that may affect behavior or is ambiguous: use **`/implement-feature`**

Do not bypass quality gates from the chosen primary workflow/command (`/run-tests`, `/update-docs`, `/conventional-commit`, etc. when required there).

## Phase 1 — Confirm scope and mode

- Use only user-provided target paths.
- If paths are missing, stop and ask.
- Display the progress checklist to the user and update each item as it completes.
- Recommend `audit-only` on a first run in a new repository.
- Confirm scope and risk tolerance before switching to `safe-fix`.
- Prefer multiple small passes over one large cleanup.

## Phase 2 — Scan target paths

Use `rg`/`grep` to locate pattern matches first; only read full file contents when a match warrants deeper inspection.

Look for patterns such as:

**Code:**
- obvious or redundant comments (comment repeats code)
- dead/unused helper wrappers
- duplicated blocks with trivial variations
- low-signal names (`data`, `temp`, `helper`, `doStuff`)
- generated "glue" code that can be simplified safely
- excessive intermediate variables with no semantic value
- over-wrapped single-line delegating functions that add no abstraction value
- gratuitous log/debug statements at every method entry/exit with no diagnostic value

**Docs (when docs are in scope):**
- README filler prose ("This project provides a robust and scalable solution for...")
- JSDoc/JavaDoc that word-for-word restates the method signature
- changelog entries written in passive AI voice with no real information

## Phase 3 — Classify findings

Use categories:

- `safe-fix`: clear, behavior-preserving cleanup
- `needs-review`: ambiguous or architecture-affecting
- `blocked`: forbidden area per safety rules

Assign severity:

- `low`: readability only
- `medium`: maintainability risk
- `high`: could alter behavior if edited carelessly

## Phase 4 — Apply fixes (safe-fix mode only)

Allowed examples:

- delete trivial duplicate comments
- rename obviously poor local identifiers in narrow scope
- remove clearly unused private helpers
- consolidate exact duplicate local utility code

For each applied fix, keep changes minimal and localized.

## Phase 5 — Run quality gates

At minimum run project-appropriate checks:

- lint
- tests relevant to touched modules

If checks fail, include failure details and mark impacted findings as `needs-review`.

## Phase 6 — Final report

Return:

- scoped paths
- mode used
- findings by category/severity
- applied changes (if any)
- remaining `needs-review` items
- verification outcome (lint/tests)

## Finding type reference

Use these values for the `Type` column in the report table:

| Type | Meaning |
|------|---------|
| `comment-noise` | comment restates obvious code |
| `name-quality` | weak identifier naming in local scope |
| `duplication` | exact/near-exact repeated blocks |
| `dead-code` | clearly unused private/internal code |
| `generated-boilerplate` | low-value wrappers and passthroughs |
| `doc-filler` | README/changelog prose with no real information |
| `redundant-javadoc` | JSDoc/JavaDoc that restates the method signature |
| `debug-noise` | gratuitous log/debug statements with no diagnostic value |

## Default response format

```markdown
## AI Slop Cleanup Report

Mode: <audit-only|safe-fix>
Scope: <paths>

### Findings
| ID | Path | Type | Severity | Status | Note |
|----|------|------|----------|--------|------|

### Applied safely
- ...

### Needs review
- ...

### Verification
- Lint: <pass/fail/not-run>
- Tests: <pass/fail/not-run>
```
