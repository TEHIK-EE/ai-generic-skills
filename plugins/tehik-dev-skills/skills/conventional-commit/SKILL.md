---
name: conventional-commit
description: "Create a conventional git commit. Use this whenever the user says 'commit', 'stage and commit', 'make a commit', 'push my changes', or implies they are done with a task and want to save their work. Also trigger when the user asks to write a commit message or wants to understand how to format one."
---

# Conventional Commit

> **Before you start:** Run `git status` to review what has changed. Do not stage or commit anything until you have reviewed the diff and selected the correct type.

Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard.

## Step 1 — Review changes

1. See what has changed:
```bash
git status
git diff --stat
git diff --staged
```

Read the actual diff content — `--stat` shows only file names, but understanding *what* changed is essential for writing a meaningful message body.

## Step 2 — Choose commit type

2. Pick an appropriate type:

| Type | Use |
|------|-----|
| `feat` | New functionality |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Restructuring without functional change |
| `test` | Adding or changing tests |
| `ci` | CI/CD configuration |
| `chore` | Dependency updates, build tooling |
| `perf` | Performance improvement |
| `style` | Code formatting |
| `revert` | Reverting a previous commit |

## Step 3 — Scope and message

3. Compose the message. Scope is optional — include it when it adds clarity (e.g. a module, service, or component name); omit it for cross-cutting changes.

**Format:**
```
<type>[(<scope>)]: <short description>

[optional body — explain WHY, not HOW]

[footer: BREAKING CHANGE: ... / Closes #123]
```

**Breaking change shorthand** — `!` after the type (or type+scope) signals a breaking change and is equivalent to a `BREAKING CHANGE:` footer entry:
```
feat!: remove deprecated /api/v1 endpoint
feat(api)!: change response payload shape
```

**Rules:**
- Subject: max **72 characters**, starts with a lowercase letter, no trailing period
- Body: explains **why** the change was made, not how
- Breaking change: use `!` shorthand and/or add `BREAKING CHANGE:` in the footer with migration notes

**Example:**
```
feat(reports): add approval deadline calculation

Deadline is now calculated from submission date based on report type.
Weekends and public holidays are excluded from working day count.

Closes #42
```

## Step 4 — Stage and commit

4. Stage modified files and create the commit:

```bash
# Preferred: add specific files (safer)
git add <file1> <file2> ...

# Alternative: when all changes are intended
git add .
```

> ⚠️ Before using `git add .`, check `git status` so you do not stage unwanted files (e.g. `.env`, temporary files, build artifacts).

```bash
git commit -m "<type>(<scope>): <short description>"
```

For a longer commit message, use a heredoc:
```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <short description>

[body — explain WHY]

[footer: Closes #123]
EOF
)"
```

> If a pre-commit hook fails, the commit did **not** happen. Fix the issue, re-stage, and create a **new** commit — do not amend, as that would modify the previous commit instead.

## Step 5 — Verification

5. Verify the commit was created correctly:
```bash
git log --oneline -3
```

Report:
```
✅ Commit created:
- Message: <type>(<scope>): <short description>
```
