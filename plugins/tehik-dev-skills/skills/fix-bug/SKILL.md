---
name: fix-bug
description: "Full bug-fix cycle from reproduction to MR-ready state. Use this when the user reports a bug, asks to fix an error/exception/regression, says 'something is broken', references a bug ticket, or asks to investigate unexpected behavior. Also trigger when the user wants to write a hotfix or patch."
---

# Bug fix

Full cycle for fixing a bug. Uses atomic workflows.

> **Before you start:** Understand exactly what bug occurs — what is the expected behavior vs actual behavior? From which data does the bug appear?

---

## Safety rules

- **Confirmation gate:** Git strategy (MR vs auto-merge) must be confirmed in Phase 1 before any code changes are made.
- Make the minimal change that fixes the bug — do not refactor simultaneously.
- For critical production bugs (`hotfix/`), the base branch must be `main`, not `develop`.
- Never force-push or bypass pre-commit hooks.

---

## Phase 1 — Analysis, reproduction + Git strategy

1. Analyze and plan:
   - Run the **`/analyze-codebase`** skill focused on where the bug is:
     - Reproduce the bug — make sure you understand its cause
     - Identify affected code and dependencies
     - Check whether the problem appears in tests too (if a test is missing — that is part of the problem)
   - **Define Git strategy before code changes:**
     - if strategy is already given in context (e.g. from `/process-task-board` config), use it (`mr` or `auto_merge_target`) and do not ask again;
     - otherwise ask the user:
       - **Option A (MR):** make commits on the fix branch and finish in MR-ready state
       - **Option B (auto-merge):** make commits on the fix branch, merge to the agreed target branch (`merge_target_branch`) and switch back to `merge_target_branch`
   - If strategy remains undetermined, **stop** and ask again (do not assume a default).

---

## Phase 2 — Branch creation

2. Run the **`/create-branch`** skill with type `fix`
   - Branch name: `fix/<ticket-id>-<description-kebab-case>`
   - Base: `develop`

---

## Phase 3 — Fix

3. Fix the bug:
   - Make the **minimal** change that fixes the bug — do not refactor at the same time
   - **Required:** add a regression test that confirms the bug does not recur (adapt syntax to the project's test framework)
     ```
     it('should not throw when [condition that caused the bug]', () => {
       // Arrange: exactly the situation that caused the bug
       // Act + Assert: make sure the bug does not occur
     });
     ```

---

## Phase 4 — Test verification

4. Run the **`/run-tests`** skill
   - All tests must pass (including the new regression test)
   - No lint errors
   - ❌ If tests fail: return to Phase 3

---

## Phase 5 — Documentation

5. Run the **`/update-docs`** skill
   - CHANGELOG `Fixed` section:
     ```markdown
     ### Fixed
     - [User-facing description of what was fixed] (#123)
     ```
   - Update README only if behavior changed from the user's perspective

---

## Phase 6 — Commit

6. Run the **`/conventional-commit`** skill
   - Type: `fix`
   - Example: `fix(reports): prevent null pointer on empty submission date`

---

## Phase 7 — Completion per Git strategy

7. Act according to the strategy agreed in Phase 1:

- **If MR strategy:** draft Merge Request description:

```markdown
## Problem
[What bug occurred and when]

## Cause
[Why the bug occurred — technical explanation]

## Solution
[What exactly was changed]

## How to test
1. [Step to reproduce the bug — so the old version shows the error]
2. [Step to verify the fix works]

## Checklist
- [ ] Regression test added
- [ ] All tests passed
- [ ] No lint errors
- [ ] CHANGELOG.md Fixed section updated
- [ ] MR size ≤ ~400 changed lines (split if needed)
```

- **If auto-merge strategy:**
  1. merge active fix branch into agreed target branch (`merge_target_branch`) (without force)
  2. resolve conflicts safely
  3. ensure tests and lint are OK after merge
  4. switch back to `merge_target_branch`

Report for MR:
```
✅ Bug fixed:
- Branch <name> is ready for MR creation
```

Report for auto-merge:
```
✅ Bug fixed:
- Merged to <merge_target_branch>
- Active branch: <merge_target_branch>
```
