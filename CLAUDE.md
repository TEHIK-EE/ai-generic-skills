# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is **not application code**. It is a **Claude Code plugin marketplace** that ships two plugins of reusable skills:

- `plugins/tehik-dev-skills` — software development lifecycle skills (`implement-feature`, `fix-bug`, `refactor`, `run-tests`, `conventional-commit`, `create-branch`, `create-migration`, `release`, `update-dependencies`, `update-docs`, `codebase-auditor`, `ai-slop-cleaner`, `analyze-codebase`, `init-project`, `validate-external-proposal`).
- `plugins/tehik-task-board` — folder-based task-queue pipeline skills (`business-brief-to-tasks`, `process-task-board`, `task-board-runner`, `validate-task-board`).

There is no source code, no build system, no test runner, and no lint config. The deliverable is Markdown (`SKILL.md`) and JSON (`plugin.json`, `marketplace.json`).

## Manifest contract (load-bearing)

Three files wire everything together. If you add, rename, or move a plugin/skill, all three layers must stay consistent:

1. **`.claude-plugin/marketplace.json`** at the repo root — registers each plugin's `name`, `source` path, and `description`. The `name` here is what users type after `@` in `/plugin install <plugin>@<marketplace>`.
2. **`plugins/<plugin>/.claude-plugin/plugin.json`** — declares the plugin's `name`, `version`, `description`, and `keywords`. The `name` must match the entry in `marketplace.json`.
3. **`plugins/<plugin>/skills/<skill>/SKILL.md`** — every skill is a directory whose name is the skill's slug (used as `/skill-name`) and whose `SKILL.md` carries the contract.

## SKILL.md format

Every `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: skill-slug
description: "Trigger sentence(s). Claude reads this to decide when to auto-invoke the skill — phrasing matters."
---
```

The `description` is **not documentation** — it is the activation heuristic. Match the existing tone: lead with a one-sentence "what it does", then list user phrases that should trigger it ("Use when the user says ..."). When editing a skill's behavior, update the `description` if its trigger surface changes.

The Markdown body that follows uses a recurring shape across this repo: a short *When this applies* / *When NOT to use* section, then numbered phases or steps, often with explicit "Safety rules" and "Confirmation gate" callouts. Keep that shape when editing — other skills cross-reference these phase numbers.

## Cross-skill orchestration (read this before editing any dev skill)

Dev skills call each other by slash-name and assume specific phase outputs. Common chains:

- `implement-feature` → `analyze-codebase`, `create-branch`, `run-tests`, `update-docs`, `conventional-commit`
- `fix-bug` and `refactor` → same dependency set
- `task-board-runner` → `process-task-board` → `implement-feature` / `fix-bug` / `refactor` (full nested flow, per `task-board-runner` rule 4)
- `business-brief-to-tasks` produces files that `process-task-board` consumes

Implication: changing a skill's contract (its phase names, expected inputs, or completion state) can break callers. Grep for the skill slug before renaming or restructuring it.

## Codebase-auditor rule-loading priority

`plugins/tehik-dev-skills/skills/codebase-auditor/` ships a `rules/` directory that defines the audit policy (api, common, database, error-handling, idempotency, observability, security, testing, git, ci-cd, documentation). The skill itself loads rules from the **first** of these sources that exists in the *target* project (not this repo):

1. `rules/` in the project being audited
2. `.agent/rules/`
3. `.cursor/rules/` (`.mdc` files)
4. `~/.claude/CLAUDE.md`

When editing the bundled `rules/*.md` files, remember they are the **fallback content shipped to users** — they are not the rules audited against this repo itself.

## Auxiliary directories inside skills

- `skills/<skill>/references/` — reusable templates referenced from the SKILL body (e.g. `init-project/references/agents-template.md`, `documentation.md`, `ci-cd.md`).
- `skills/<skill>/rules/` — only `codebase-auditor` uses this convention; treat the contents as content the skill *delivers*, not rules that govern this repo.

## Validating changes (the closest thing to "tests")

There is no automated test suite. After edits, verify manually:

```bash
# Ensure all manifests are valid JSON
find . -name '*.json' -not -path './.git/*' -exec python3 -m json.tool {} \; >/dev/null

# Confirm every plugin listed in the marketplace exists on disk and has a plugin.json
python3 -c "import json,os;m=json.load(open('.claude-plugin/marketplace.json'));[print('OK',p['name']) if os.path.exists(os.path.join(p['source'],'.claude-plugin','plugin.json')) else print('MISSING',p['name']) for p in m['plugins']]"

# Confirm every skill directory has a SKILL.md with frontmatter
for f in plugins/*/skills/*/SKILL.md; do head -1 "$f" | grep -q '^---$' || echo "MISSING FRONTMATTER: $f"; done
```

## Local install for dogfooding

```text
/plugin add ./plugins/tehik-dev-skills
/plugin add ./plugins/tehik-task-board
```

After editing any `SKILL.md` or `plugin.json`, run `/reload-plugins` in Claude Code to pick up the changes — they are not hot-reloaded.

## Commit convention

This repo eats its own dog food: commits follow the [Conventional Commits](https://www.conventionalcommits.org/) spec defined by the `conventional-commit` skill (`feat`, `fix`, `docs`, `refactor`, `chore`, etc.). Subjects are imperative, lowercase, no period, ≤72 chars. Documentation-only changes use `docs:`; skill behavior changes use `feat:` or `fix:` with the skill name as the scope when useful (e.g. `feat(implement-feature): ...`).
