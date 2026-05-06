---
name: refactor
description: >-
  Safe, test-protected refactoring cycle for restructuring code without changing behavior.
  Use this skill whenever the user asks to: extract a method/class/service, rename symbols,
  remove duplication (DRY), apply dependency injection, move files/modules, reorganize code
  structure, or generally says "refactor", "clean up", or "restructure" existing code.
  Also trigger when the user wants to apply patterns like Extract Method, Pull Up/Push Down,
  or Separate Concerns — even if they don't use the word "refactor".
---

# Code Refactoring

A safe refactoring cycle that ensures behavior does not change.

> **Important:** refactoring changes **structure**, not **behavior**. If behavior changes, that is a feat/fix, not a refactor.

---

## Safety rules

- **Confirmation gate:** Git strategy (MR vs auto-merge) must be confirmed in Phase 2 before any code changes are made.
- Tests must pass both before and after refactoring (Phases 3 and 6). A failing test after refactoring indicates a regression, not a faulty test.
- Refactoring must not change behavior. If behavior changes are needed, stop and create a separate feat/fix task.
- Never force-push or bypass pre-commit hooks.

---

## Phase 1 — Scope clarification (skip if already clear from context)

Before analyzing anything, confirm:
- What code should be refactored? (file / module / function name)
- What structural problem are we solving? (e.g. method too long, class doing too much, duplication)
- Are there any constraints? (e.g. keep public API stable, no dependency changes)

---

## Phase 2 — Analysis + Git strategy

- Run the **`/analyze-codebase`** skill focused on the code to refactor:
  - Identify affected modules, classes, and functions
  - Map dependencies — what uses this code?
  - Note existing tests
- **Define the Git strategy before changing code:**
  - If a strategy was already provided in context (e.g. from `/process-task-board` config), use it (`mr` or `auto_merge_target`) and do not ask again
  - Otherwise ask the user:
    - **Option A (MR):** commit on the branch and finish in MR-ready state
    - **Option B (auto-merge):** commit on the branch, merge into the agreed target branch (`merge_target_branch`), and switch back to `merge_target_branch`
- If the strategy is still undetermined, **stop** and ask again (do not assume a default).

---

## Phase 3 — Test check before changes

Run the **`/run-tests`** skill — ensure all tests pass **before** refactoring.

- If the code being refactored has low test coverage: **write tests before refactoring**
  - Focus on the public API and key behaviors of the code being changed
  - A practical guide: if you can't write a test that would catch a behavior change, you don't have enough coverage yet
- This is your safety net — without tests you cannot prove that behavior did not change

---

## Phase 4 — Branch creation

Run the **`/create-branch`** skill with type `feature` (there is no separate branch type for refactoring):
- Branch name: `feature/<ticket-id>-refactor-<description-kebab-case>`

---

## Phase 5 — Refactoring

Apply changes:
- **One change at a time:** e.g. move the file first, then rename, then adjust structure
- **Compile/lint after each step** — surface issues early
- Common refactorings:
  * Extract Method
  * Extract Class
  * Pull Up / Push Down
  * Rename
  * Remove duplicate code (DRY)
  * Add dependency inversion (Dependency Injection)

---

## Phase 6 — Test check after changes

Run the **`/run-tests`** skill:
- **All existing tests must pass** — this proves behavior did not change
- If a test fails: that is a regression, not a faulty test — fix the refactoring
- Update tests **only** if you changed the public API (e.g. a method was renamed)
- ❌ Do not delete a failing test — it is your safety net

---

## Phase 7 — Documentation

Run the **`/update-docs`** skill:
- CHANGELOG: `Changed` section (only if the change is user-visible)
- Architecture diagrams (if structure changed)
- AGENTS.md (if project structure changed)

---

## Phase 8 — Commit

Run the **`/conventional-commit`** skill:
- Type: `refactor`
- Example: `refactor(reports): extract deadline calculation into separate service`

---

## Phase 9 — Completion according to Git strategy

Follow the strategy agreed in Phase 2:

- **If MR strategy:** leave the branch MR-ready.
- **If auto-merge strategy:**
  1. Merge the active branch into the agreed target branch (`merge_target_branch`) (without force)
  2. Resolve conflicts safely
  3. Ensure tests/lint are clean after the merge
  4. switch back to `merge_target_branch`

Report for MR:
```
✅ Refactoring complete:
- All tests passed
- Branch <name> is ready for MR creation
```

Report for auto-merge:
```
✅ Refactoring complete:
- All tests passed
- Merged to <merge_target_branch>
- Active branch: <merge_target_branch>
```
