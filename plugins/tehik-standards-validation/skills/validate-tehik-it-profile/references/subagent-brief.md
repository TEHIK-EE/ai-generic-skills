# Per-layer subagent brief (template)

The orchestrator interpolates the placeholders below and passes the result as
the `prompt` to a subagent (one subagent per technology layer, run in
parallel).

This brief carries **only per-dispatch context** — the variables that change
per layer. The invariant rules live in two other places, both loaded by the
subagent at the start of its run:

- The agent's system prompt
  (`${CLAUDE_PLUGIN_ROOT}/agents/it-profile-layer-auditor.md`) — verdict
  vocabulary, output format, IT-Profile-specific resolution rules.
- The shared rules file
  (`${CLAUDE_PLUGIN_ROOT}/references/auditor-common.md`) — read-only
  contract, confidence ladder, evidence discipline, findings-file mechanic.

If you change a rule that lives in one of those files, do not also restate it
here. The whole point of this split is to have one source of truth per rule.

## How the orchestrator uses this file

1. Read this template.
2. For each layer being audited, replace every `{{...}}` placeholder.
3. Spawn a subagent (Agent tool,
   `subagent_type: tehik-standards-validation:it-profile-layer-auditor`)
   and pass the filled-in template as the prompt. The agent is pinned to
   Sonnet and locked to read-only tools (Read, Grep, Glob, Bash) — do not
   override the subagent type unless you have a specific reason.
4. Wait for all subagents in the batch to return, then aggregate.

## Placeholders

- `{{LAYER_NUMBER}}` — integer layer number (e.g. `3`)
- `{{LAYER_TITLE}}` — human title (e.g. `Application Layer`)
- `{{LAYER_MD_PATH}}` — absolute path to the per-layer markdown chunk
- `{{LAYER_JSON_PATH}}` — absolute path to the structured JSON for this layer
- `{{PROJECT_ROOT}}` — absolute path to the project being audited
- `{{PROJECT_INTEL}}` — pre-flight fact sheet from the orchestrator (10-30 lines)
- `{{FINDINGS_OUTPUT_PATH}}` — absolute path the subagent must write its findings to
- `{{IT_PROFILE_SOURCE_URL}}` — upstream URL captured from fetch_it_profile.py
- `{{IT_PROFILE_SOURCE_SHA}}` — sha256 of the upstream document at audit time
- `{{COMMON_RULES_PATH}}` — absolute path to
  `${CLAUDE_PLUGIN_ROOT}/references/auditor-common.md` (resolve
  `${CLAUDE_PLUGIN_ROOT}` at dispatch time so the subagent gets a
  concrete path it can `Read`)

---

## BEGIN PROMPT TEMPLATE

You are auditing layer {{LAYER_NUMBER}} ("{{LAYER_TITLE}}") of the TEHIK IT
Profile against the software project rooted at `{{PROJECT_ROOT}}`.

### Read these before you start

1. **Shared auditor rules:** `{{COMMON_RULES_PATH}}` — read-only contract,
   confidence ladder, evidence discipline, findings-file mechanic.
2. **The layer matrix to audit:**
   - Markdown chunk: `{{LAYER_MD_PATH}}` (human-readable, shows visual
     grouping).
   - Structured JSON: `{{LAYER_JSON_PATH}}` (parsed preferred /
     acceptable / forbidden cells, footnote markers, stable component
     `id`s).

Use both views. The JSON is authoritative for which choices live in which
column and which footnotes attach to which entries; the Markdown shows
context the JSON flattens. Footnote markers `[N]` in a choice's `footnotes`
field point at numbered notes in the same component's `comments.footnotes`
— the most common note is `Must be coordinated with TEHIK architect`, which
triggers the `NEEDS_COORDINATION` verdict.

### Pre-flight project intel

The orchestrator already scanned the project and produced this fact sheet —
use it as ground truth rather than rediscovering. Spend tool calls on
layer-specific evidence gathering.

{{PROJECT_INTEL}}

### Your task

Follow the verdict rubric, output format, and IT-Profile-specific
resolution rules defined in your agent system prompt. Use the stable
component `id`s from the JSON verbatim in your output — do not renumber.
Write your findings to:

```
{{FINDINGS_OUTPUT_PATH}}
```

Use these provenance values verbatim in the findings file's header lines:

- **Audited against:** `{{IT_PROFILE_SOURCE_URL}}` (sha256 `{{IT_PROFILE_SOURCE_SHA}}`)

When you finish, return the one-paragraph summary defined in the shared
rules (path written + verdict counts). The orchestrator uses that paragraph
as a sanity check before reading the file.

## END PROMPT TEMPLATE
