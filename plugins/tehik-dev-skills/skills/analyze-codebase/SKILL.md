---
name: analyze-codebase
description: "Analyze codebase structure, patterns, and relevant code before making any changes. Use this skill before implementing a feature, fixing a bug, or refactoring — it prevents pattern inconsistencies and missed dependencies. Also trigger when asked to 'understand the code', 'explore the project structure', or 'look at how X works' before doing work."
---

# Codebase Analysis

Goal: understand the existing code before making changes. Do not start changing anything until this step is complete.

## Step 0 — AGENTS.md check (mandatory)

1. Check whether `AGENTS.md` exists in the project root directory
2. **If AGENTS.md exists:** read it through — it provides quick context about the project. Continue with Step 1.
3. **If AGENTS.md is missing:** create it using the template in `references/agents-template.md` (bundled with this skill):
   - Fill in all sections with known information
   - For sections that cannot be determined, mark `[clarify]`
   - After creation, continue with Step 1

> `AGENTS.md` is the agent's own working tool — like `README.md`, it must always exist. The agent updates this file whenever it discovers changes to the project structure.

## Step 1 — Project overview

1. Read `README.md` — what this project is, which technologies it uses, how to run it. If `README.md` is absent, note it as a gap and proceed with directory exploration.
2. Check for AI/editor config files (`.cursor/rules/`, `CLAUDE.md`, `.github/copilot-instructions.md`) — these contain project conventions the agent must follow.
3. Explore the project root structure (`ls` or `find`) — identify main directories and modules.
4. Identify the technology stack in use (language, framework, database, queue system).

## Step 2 — Relevant code analysis

Find and read code related to the given task:

1. Identify the relevant module/component/service
2. Understand existing patterns and style (naming, structure, dependencies)
3. Find whether similar functionality already exists (DRY principle)
4. Identify dependencies that the change affects (what uses this module)

## Step 3 — Test analysis

1. Find existing tests for the relevant code
2. Understand the testing strategy (unit / integration / e2e)
3. Identify test frameworks and mocking patterns in use
4. If no tests exist for the relevant module, record this as a risk in the summary

## Step 4 — Summary

Before starting work, prepare a short summary:

```
Analysis result:
- Relevant module: [name and location]
- Existing patterns: [which patterns to follow]
- Affected dependencies: [what might break]
- Testing strategy: [how to test the change]
- Blockers/risks: [what might become difficult]
```
