---
name: init-project
description: "Use when starting a brand-new software project from scratch — initializing a repo, bootstrapping a service, creating a new microservice, or setting up a monorepo. Trigger on: 'create new project', 'init project', 'scaffold a new service', 'start a new repo', 'bootstrap project', 'initialize repository', 'set up a fresh project', or any request to create a project structure from zero with enterprise standards."
---

# Project Initialization (Scaffolding)

This workflow creates a new software project from scratch, wiring up all enterprise standards (docs, CI/CD, git, linting, containerisation) so the repo is immediately compliant and runnable.

> **Before starting:** Confirm the project's business goal, repository platform, and technology stack — or ask the user if any of these are unclear.

---

## Required inputs

Before starting, confirm (or ask the user):
- **Business goal** — what does this project do and for whom?
- **Repository platform** — GitLab or GitHub? (determines CI/CD template)
- **Technology stack** — language, framework, database, infrastructure
- **Service type** — REST API / BFF / frontend SPA / background worker / library

## Phase 1 — Gather context

Ask the user (or infer from prior conversation):
- **Business goal:** what does this project do and for whom?
- **Repository platform:** GitLab or GitHub? (determines CI/CD template)
- **Technology stack:** language, framework, database, infrastructure
- **Service type:** REST API / BFF / frontend SPA / background worker / library

---

## Phase 2 — Initialise git and scaffold the project

1. Run `git init` in the project root.
2. Run the appropriate non-interactive scaffold command:
   - **Node/TypeScript:** `npm create vite@latest . -- --template react-ts -y` or framework equivalent
   - **Python:** `uv init` or `poetry new .`
   - **Java/Kotlin:** `./gradlew init` or Maven archetype
   - **Other:** use the framework's recommended CLI with non-interactive flags
3. Organise directory structure per Clean Architecture or the framework's best practices.

---

## Phase 3 — Create documentation structure

Read `references/documentation.md` for the full rules and file templates.

**Create directories:**
```
docs/
  architecture/
  api/
  data-model/
  processes/
  adr/
```

**Create files:**

- `README.md` — follow the structure in `references/documentation.md` (§ README.md structure)
- `CHANGELOG.md` — Keep a Changelog format; add a `v0.0.0 — Unreleased` entry
- `AGENTS.md` — use the template in `references/agents-template.md`; fill in all known fields; mark `[clarify]` for unknowns
- `.env.example` — list all required configuration key names; no real secret values
- `docs/adr/ADR-001-tech-stack.md` — document the technology choices made now (language, framework, database) using the ADR format in `references/documentation.md` (§ ADR format)

---

## Phase 4 — Security and gitignore

Create `.gitignore` covering at minimum:
- `.env` and all `.env.*` variants (except `.env.example`)
- Build artifacts (`dist/`, `build/`, `target/`, `__pycache__/`, `*.class`)
- IDE files (`.idea/`, `.vscode/`, `*.iml`)
- Agent temp logs (`/Agent_reports/Tasks/.working/`, `.agent-memory/`)
- OS files (`.DS_Store`, `Thumbs.db`)

Verify that no secrets or tokens appear in any tracked file.

---

## Phase 5 — Containerisation

Create a multi-stage `Dockerfile` and `.dockerignore`. Read `references/ci-cd.md` (§ Docker image conventions) for tagging and image standards:
- Build stage separate from runtime stage
- Prefer distroless/slim base images
- `.dockerignore` must exclude `.env`, test files, and dev dependencies

---

## Phase 6 — Linting, formatting, and pre-commit hooks

Configure linter + formatter and wire up pre-commit hooks so lint/format checks run before every commit:

| Stack | Linter/Formatter | Pre-commit tooling |
|-------|-----------------|-------------------|
| TypeScript/JS | ESLint + Prettier | Husky + lint-staged |
| Python | Ruff | pre-commit framework |
| Java/Kotlin | Checkstyle + Spotless | Maven/Gradle hook |
| Other | language-idiomatic tool | language-idiomatic hook |

---

## Phase 7 — CI/CD pipeline

Read `references/ci-cd.md` for the full pipeline specification and template.

Create the baseline CI/CD file:
- **GitLab:** `.gitlab-ci.yml`
- **GitHub:** `.github/workflows/main.yml`

Required stages in order: `lint → test → build → security-scan → deploy`

Environment hierarchy: `feature/* → develop (auto) → staging (auto) → production (manual approval)`

Adapt registry URLs and deploy scripts to the project. Do not hardcode secrets in the YAML.

---

## Phase 8 — Verify the build

- Run the project's build command — must succeed with zero errors
- Run any generated placeholder tests — must pass
- Run the linter — must report zero errors

Fix any issues before proceeding.

---

## Phase 9 — Initial commit

Run the **`/conventional-commit`** skill:
- Type: `chore`
- Scope: *(omit)*
- Message: `chore: init project structure with enterprise defaults`

---

## Phase 10 — Final report

Present the user with a summary:

```
✅ Project initialised

Structure created:
  docs/architecture/, api/, data-model/, processes/, adr/
  README.md, CHANGELOG.md, AGENTS.md, .env.example
  docs/adr/ADR-001-tech-stack.md
  Dockerfile, .dockerignore, .gitignore
  CI/CD: [.gitlab-ci.yml | .github/workflows/main.yml]
  Linter: [tool] + pre-commit hooks

Run locally:
  [stack-specific start command]

Next steps:
  - Set real environment variables (see .env.example)
  - Configure CI/CD variables in [GitLab | GitHub] settings
  - Complete docs/adr/ADR-001-tech-stack.md with context and alternatives
```
