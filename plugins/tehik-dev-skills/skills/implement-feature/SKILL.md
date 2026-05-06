---
name: implement-feature
description: "Full feature implementation cycle from analysis to MR-ready state. Use this when the user asks to add new functionality, implement a feature, build an endpoint/service/module, or references a feature ticket. Also trigger when the user says 'add X', 'create X feature', 'implement X', or wants to start working on new behavior."
---

# Feature Implementation

Complete cycle for adding new functionality. Uses atomic workflows.

> **Before you start:** Make sure the task is clearly understood—what exactly needs to be implemented? If anything is unclear, ask the user before you begin work.

---

## Safety rules

- **Confirmation gate:** Git strategy (MR vs auto-merge) must be confirmed in Phase 1 before any code changes are made.
- Do not start implementation until the codebase analysis (Phase 1) is complete.
- Never commit without all tests passing.
- Never force-push or bypass pre-commit hooks.

---

## Phase 1 — Analysis + Git strategy

1. Analyze and plan:
   - Run the **`/analyze-codebase`** skill
     - Identify relevant code, patterns, and dependencies
     - Summarize the findings
   - **Define the Git strategy before making code changes:**
     - if the strategy is already provided in context (e.g. from `/process-task-board` config), use it (`mr` or `auto_merge_target`) and do not ask again;
     - otherwise ask the user:
       - **Option A (MR):** make commits on the feature branch and finish in an MR-ready state
       - **Option B (auto-merge):** make commits on the feature branch, merge into the agreed target branch (`merge_target_branch`), and switch back to `merge_target_branch`
   - If the strategy remains undetermined, **stop** and ask again (do not assume a default).

---

## Phase 2 — Branch creation

2. Run the **`/create-branch`** skill with type `feature`
   - Branch name: `feature/<ticket-id>-<description-kebab-case>`
   - Base: per project convention (default: `develop`)

---

## Phase 3 — Implementation

3. Implement the functionality following the rules:
   - **Architecture:** SOLID, Clean Architecture — keep business logic separate from infrastructure
   - **API:** REST resources as nouns, correct HTTP methods, RFC 9457 error formats
   - **Database:** migration files when the schema changes, UUID v7 for primary keys, audit fields
   - **Security:** BFF pattern for authentication, validate inputs at all layers
   - **KISS/YAGNI:** do not build "just in case" functionality

---

## Phase 4 — Tests

4. Write tests (before running `run-tests`):
   - Unit tests for all new functions/methods
   - Integration tests for the API layer (if an endpoint was added)
   - Coverage targets: ≥ **80%** overall, ≥ **90%** for critical modules
   - Use the AAA pattern: `Arrange → Act → Assert`
   - Use the Test Data Builder pattern instead of calling constructors directly

---

## Phase 5 — Documentation

5. Run the **`/update-docs`** skill
   - CHANGELOG `Added` section
   - README if behavior changed
   - OpenAPI specification if the API changed
   - Architecture diagrams if the structure changed

---

## Phase 6 — Test verification

6. Run the **`/run-tests`** skill
   - All tests must pass
   - Coverage ≥ 80% overall, ≥ 90% for critical modules
   - No lint errors
   - ❌ If tests fail: go back to Phase 3/4

---

## Phase 7 — Commit

7. Run the **`/conventional-commit`** skill
   - Type: `feat`
   - Example: `feat(reports): add approval deadline calculation`

---

## Phase 8 — Completion according to Git strategy

8. Follow the strategy agreed in Phase 1:

- **If using the MR strategy:** draft a Merge Request description:

```markdown
## What changed
[Brief description — what functionality was added]

## Why
[Business rationale — what problem this solves]

## How to test
1. [Step 1]
2. [Step 2]

## Checklist
- [ ] Tests passed and coverage ≥ 80% overall, ≥ 90% for critical modules
- [ ] No lint errors
- [ ] CHANGELOG.md `Added` section updated
- [ ] README.md updated (if behavior changed)
- [ ] OpenAPI specification updated (if API changed)
- [ ] Security: inputs validated at all layers
- [ ] Database: migration file present and idempotent (if schema changed)
- [ ] MR size ≤ ~400 changed lines (split into multiple MRs if needed)
```

- **If using the auto-merge strategy:**
  1. merge the active feature branch into the agreed target branch (`merge_target_branch`) (without force)
  2. resolve conflicts safely
  3. ensure tests and lint are clean after the merge
  4. switch back to `merge_target_branch`

Report for MR:
```
✅ Feature implemented:
- Branch <name> is ready for MR creation
```

Report for auto-merge:
```
✅ Feature implemented:
- Merged to <merge_target_branch>
- Active branch: <merge_target_branch>
```
