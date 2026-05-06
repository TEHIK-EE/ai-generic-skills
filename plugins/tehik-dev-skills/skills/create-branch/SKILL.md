---
name: create-branch
description: >
  Create a correctly named git branch following the project branch strategy.
  Use this whenever the user says 'create a branch', 'make a branch', 'I need a new branch',
  'start working on [ticket]', 'let me work on [feature/bug]', or wants to begin
  a feature, bug fix, hotfix, or release branch.
---

# Creating a Branch

> **Gate:** Step 1 checks for uncommitted changes. If any exist, this skill stops and asks how to proceed before creating a branch.

## Step 1 — Prerequisites

1. Check working tree cleanliness:
```bash
git status
```
If there are uncommitted changes, stop and ask the user what to do.

## Step 2 — Pulling the correct base branch

2. Checkout and pull the correct base branch depending on branch type:

- `feature/*`, `fix/*`, `release/*` → base is `develop`
- `hotfix/*` → base is `main`

```bash
git checkout <develop|main>
git pull origin <develop|main>
```

## Step 3 — Choosing the branch name

3. Determine the branch type and name according to the convention:

| Type | Convention | Example |
|------|------------|---------|
| New feature | `feature/<ticket-id>-<description>` | `feature/JIRA-42-add-approval-deadline` |
| Bug fix | `fix/<ticket-id>-<description>` | `fix/JIRA-118-button-null-pointer` |
| Critical production fix | `hotfix/<ticket-id>-<description>` | `hotfix/JIRA-200-payment-duplicate` |
| Release preparation | `release/<version>` | `release/1.4.0` |

The description must be **kebab-case**, in English, at most 5 words.

If there is no ticket ID (e.g. chore or exploratory work), omit it: `<type>/<description>`.

## Step 4 — Creating the branch

4. Create the branch:
```bash
git checkout -b <branch-name>
```

## Step 5 — Verification

5. Verify that you are on the correct branch:
```bash
git branch --show-current
```

## Step 6 — Push to remote (optional)

6. If the user wants to register the branch on the remote immediately:
```bash
git push -u origin <branch-name>
```

Report:
```
✅ Branch created:
- Branch: <branch-name>
- You are now on this branch
```
