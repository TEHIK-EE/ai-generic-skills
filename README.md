# TEHIK AI Generic Skills

A Claude Code Plugin Marketplace containing reusable AI skills for software development workflows at TEHIK.

## Overview

This repository provides three plugins for Claude Code:

- **tehik-dev-skills** — Core development lifecycle skills: feature implementation, bug fixing, refactoring, commits, migrations, releases, dependency management, and codebase quality.
- **tehik-task-board** — Folder-based task board skills for turning business briefs into atomic tasks, processing queues, and running validation workflows.
- **tehik-standards-validation** — Validate a project against TEHIK's published standards (NFRs, IT Profile). Each skill fans out across parallel subagents to keep context manageable and produces a Markdown audit report.

Skills are invoked automatically by Claude Code when your request matches a skill's trigger conditions, or explicitly via `/skill-name`.

## Installation

### Via Claude Code Marketplace

In Claude Code, run:

```text
/plugin marketplace add TEHIK-EE/ai-generic-skills
```

This registers the marketplace so you can browse its plugins. Then install the ones you want (or use the following commands):

```text
/plugin install tehik-dev-skills@tehik-dev-skills
/plugin install tehik-task-board@tehik-dev-skills
/plugin install tehik-standards-validation@tehik-dev-skills
```

### Manual Installation

Clone the repository and install each plugin individually:

```bash
git clone git@github.com:TEHIK-EE/ai-generic-skills.git
```

Then in Claude Code:

```text
/plugin add ./plugins/tehik-dev-skills
/plugin add ./plugins/tehik-task-board
/plugin add ./plugins/tehik-standards-validation
```

To install only one plugin, run only the corresponding `/plugin add` command.

### Updating

Auto-update is disabled by default for third-party marketplaces. To enable it, open `/plugin` → Marketplaces tab and toggle auto-update for this marketplace. When enabled, Claude Code checks for updates at startup and prompts you to run `/reload-plugins` when skills change.

To update manually at any time:

```text
/plugin marketplace update tehik-dev-skills
```

Then run `/reload-plugins` to apply the changes.

## Skills

### tehik-dev-skills

| Skill | Description |
| --- | --- |
| `implement-feature` | Full feature implementation cycle from codebase analysis to MR-ready state. |
| `fix-bug` | Full bug-fix cycle from reproduction to MR-ready state, including root cause analysis. |
| `refactor` | Safe, test-protected refactoring cycle for restructuring code without changing behavior. |
| `run-tests` | Run linting, tests, and coverage checks to verify code is ready to commit. |
| `conventional-commit` | Stage changes and create a properly formatted conventional git commit. |
| `create-branch` | Create a correctly named git branch following the project branch strategy. |
| `create-migration` | Create idempotent, backward-compatible database migration scripts (Flyway, Liquibase, Alembic, Prisma). |
| `release` | Complete release cycle: branch, CHANGELOG, version bump, tests, MRs, and tag. |
| `update-dependencies` | Audit and safely update npm, pip, or Gradle/Maven dependencies. |
| `update-docs` | Update project documentation (README, CHANGELOG, API docs) after code changes. |
| `codebase-auditor` | Deterministic compliance audit against the project's own architecture and quality rules. |
| `ai-slop-cleaner` | Detect and remove low-value AI-generated noise: redundant comments, dead helpers, verbose wrappers. |
| `analyze-codebase` | Analyze codebase structure, patterns, and dependencies before making changes. |
| `init-project` | Bootstrap a new software project from scratch with enterprise-grade standards. |
| `validate-external-proposal` | Technical and business validation of external partner proposals, vendor offers, or architecture documents. |

### tehik-task-board

| Skill | Description |
| --- | --- |
| `business-brief-to-tasks` | Turn a business brief or raw assignment into atomic tasks in a folder, including an EPIC and sub-tasks. |
| `process-task-board` | Process a folder-based task queue — complete tasks and move them to the output folder with artifact directories. |
| `task-board-runner` | Run folder-based task queues (`To-Do` → `To-Validate` → `Done`) with routing and second-pass validation. |
| `validate-task-board` | Second-pass review: move `To-Validate` tasks to `Done` or back to `To-Do` with clarifying notes. |

### tehik-standards-validation

| Skill | Description |
| --- | --- |
| `validate-tehik-nfr` | Validate a project against TEHIK's non-functional requirements. Fans out NFR sections across parallel subagents and produces a per-requirement Markdown audit report. |
| `validate-tehik-it-profile` | Validate a project's technology stack against the TEHIK IT Profile (preferred / acceptable / forbidden tech). Fans out per technology layer and produces a per-component Markdown audit report. |
