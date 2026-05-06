---
trigger: always_on
---

# VERSION CONTROL (GIT)

## Commit messages — Conventional Commits

Every commit must follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
<type>(<scope>): <short description>

[optional body]

[optional footer: BREAKING CHANGE, Closes #123]
```

**Allowed types:**

| Type | Usage |
|------|-------|
| `feat` | New functionality |
| `fix` | Bug fix |
| `docs` | Documentation-only changes |
| `refactor` | Code restructuring without functional change |
| `test` | Adding or modifying tests |
| `ci` | CI/CD configuration |
| `chore` | Dependency updates, build tooling changes |
| `perf` | Performance improvements |
| `style` | Code formatting (whitespace, semicolons, etc.) |

**Example:**
```
feat(reports): add approval deadline calculation

Deadline is calculated based on submission date and report type.
Weekends and public holidays are excluded from working day count.

Closes #42
```

## Branch strategy

```
main          ←── protected, release merges only
develop       ←── integration branch, CI must pass
feature/*     ←── new features (feature/JIRA-123-add-login)
fix/*         ←── bug fixes (fix/JIRA-456-null-pointer)
release/*     ←── release preparation (release/1.2.0)
hotfix/*      ←── critical production fixes
```

* **Branch naming:** `<type>/<ticket-id>-<short-description-kebab-case>`
* All branches branch off `develop` (except `hotfix/`, which branches off `main`)

## Pre-commit checks

Configure automated checks at project level before every commit:

* **Tool:** Husky + lint-staged (Node.js), pre-commit framework (Python), githooks (Java/Kotlin)
* **Minimum checks:**
  * Linter (ESLint, Ruff, Checkstyle)
  * Code formatting (Prettier, Black, ktfmt)
  * Commit message validation (commitlint, Conventional Commits rule)
  * Secret scanning (gitleaks, detect-secrets)
* Pre-commit hooks are **under version control** (e.g. `.husky/`, `.pre-commit-config.yaml`)
* ❌ Skipping hooks (`--no-verify`) is allowed only in exceptional cases and with justification

## Merge Request (MR) requirements

* MR title follows the Conventional Commits format
* Description includes: **What changed**, **Why**, **How to test**
* At least **1 reviewer** approval is mandatory
* All CI checks passed (`lint`, `test`, `build`, `security-scan`)
* Recommended MR size: **max ~400 changed lines** (smaller MRs are easier to review)

## Merge strategy

* **Squash merge** preferred when merging `feature/*` and `fix/*` into `develop` — one clean commit per MR
* **Merge commit** (no-ff) when merging `develop` → `main` — preserves release history
* **Rebase** allowed only on your own feature branch before opening an MR (clean local history)
* ❌ Rebase on `develop` or `main` is forbidden

## Prohibitions (ABSOLUTE)

* ❌ `git push --force` to `main` and `develop` branches
* ❌ Committing secrets (passwords, API keys, certificates) — even temporarily
* ❌ Binary files (>1MB) without Git LFS
* ❌ Committing directly to `main` or `develop` (only via MR)
* ❌ Keeping generated files (build artifacts, `node_modules/`) under version control

## `.gitignore`

The project `.gitignore` must cover:
* IDE-specific files (`.idea/`, `.vscode/`, `*.iml`)
* Operating system files (`.DS_Store`, `Thumbs.db`)
* Dependency directories (`node_modules/`, `vendor/`, `venv/`)
* Build artifacts (`dist/`, `build/`, `target/`, `*.class`)
* Environment configuration (`.env`, `.env.local`)
* Log files (`*.log`)

## Release notes (CHANGELOG.md)

Each release is documented in the project’s **English** `CHANGELOG.md`. Use the [Keep a Changelog](https://keepachangelog.com/) format with [Semantic Versioning](https://semver.org/).

### Version numbering

```
MAJOR.MINOR.PATCH  (e.g. 2.4.1)
│     │     └─── Bug fix (backward compatible)
│     └───────── New functionality (backward compatible)
└─────────────── Breaking change (incompatible)
```

### CHANGELOG.md format

```markdown
# Changelog

## [Unreleased]
### Added
- ...

## [1.3.0] - 2024-03-15
### Added
- Email notification for report approvals (#123)

### Changed
- Updated report submission deadline logic (#145)

### Fixed
- Fixed approval button issue on mobile view (#118)

### Security
- Added SameSite attribute to session cookies (#156)

## [1.2.1] - 2024-02-28
### Fixed
- Fixed VAT calculation rounding error (#112)
```

### Change categories

| Category | Usage |
|----------|-------|
| `Added` | New functionality |
| `Changed` | Changes to existing behavior |
| `Deprecated` | Functionality to be removed in the future |
| `Removed` | Removed functionality |
| `Fixed` | Bug fixes |
| `Security` | Security fixes |

### Rules

* The `[Unreleased]` section always contains changes since the last release
* Each description is **understandable to the user** (not a technical commit message)
* Related issue/ticket number in parentheses: `(#123)`
* A breaking change description clearly states **what breaks** and **how to migrate**
* Releases are also marked with a git tag: `git tag -a v1.3.0 -m "Release 1.3.0"`
