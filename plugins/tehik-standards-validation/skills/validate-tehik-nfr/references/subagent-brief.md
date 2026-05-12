# Per-section subagent brief (template)

The orchestrator interpolates the placeholders below and passes the result as
the `prompt` to a subagent (one subagent per NFR section, run in parallel).

This brief carries **only per-dispatch context** — the variables that change
per section. The invariant rules live in two other places, both loaded by the
subagent at the start of its run:

- The agent's system prompt
  (`${CLAUDE_PLUGIN_ROOT}/agents/nfr-section-auditor.md`) — verdict
  vocabulary, output format, NFR-specific gotchas.
- The shared rules file
  (`${CLAUDE_PLUGIN_ROOT}/references/auditor-common.md`) — read-only
  contract, confidence ladder, evidence discipline, findings-file mechanic.

If you change a rule that lives in one of those files, do not also restate it
here. The whole point of this split is to have one source of truth per rule.

## How the orchestrator uses this file

1. Read this template.
2. For each section being audited, replace every `{{...}}` placeholder.
3. Spawn a subagent (Agent tool,
   `subagent_type: tehik-standards-validation:nfr-section-auditor`) and
   pass the filled-in template as the prompt. The agent is pinned to
   Sonnet and locked to read-only tools (Read, Grep, Glob, Bash) — do
   not override the subagent type unless you have a specific reason.
4. Wait for all subagents in the batch to return, then aggregate.

## Placeholders

- `{{SECTION_NUMBER}}` — integer section number (e.g. `4`)
- `{{SECTION_TITLE}}` — human title (e.g. `Logging`)
- `{{SECTION_MD_PATH}}` — absolute path to the per-section markdown chunk
- `{{PROJECT_ROOT}}` — absolute path to the project being audited
- `{{APP_TYPE}}` — one of `self_service`, `websites`, `cots`, `unknown`
- `{{APP_TYPE_HUMAN}}` — readable form for the report (e.g. `self-service application`)
- `{{PROJECT_INTEL}}` — pre-flight fact sheet from the orchestrator (10-30 lines)
- `{{FINDINGS_OUTPUT_PATH}}` — absolute path the subagent must write its findings to
- `{{NFR_SOURCE_URL}}` — upstream URL captured from fetch_nfrs.py
- `{{NFR_SOURCE_SHA}}` — sha256 of the upstream document at audit time
- `{{COMMON_RULES_PATH}}` — absolute path to
  `${CLAUDE_PLUGIN_ROOT}/references/auditor-common.md` (resolve
  `${CLAUDE_PLUGIN_ROOT}` at dispatch time so the subagent gets a
  concrete path it can `Read`)

---

## BEGIN PROMPT TEMPLATE

You are auditing section {{SECTION_NUMBER}} ("{{SECTION_TITLE}}") of the TEHIK
non-functional requirements against the software project rooted at
`{{PROJECT_ROOT}}`.

### Read these before you start

1. **Shared auditor rules:** `{{COMMON_RULES_PATH}}` — read-only contract,
   confidence ladder, evidence discipline, findings-file mechanic.
2. **The NFR section to audit:** `{{SECTION_MD_PATH}}` — a Markdown table
   chunk with the upstream preamble. Every NFR row is shaped
   `| **{{SECTION_NUMBER}}.M** | <requirement> | <explanation> | <e-Government CFR> | <Self-service> | <Websites> | <COTS> | <Responsible> | <Tested by> |`.

A `V` in an applicability column means the NFR applies to that application
type; an empty cell means it does not. The project's application type is
**{{APP_TYPE_HUMAN}}** (`{{APP_TYPE}}`).

### Pre-flight project intel

The orchestrator already scanned the project and produced this fact sheet —
use it as ground truth rather than rediscovering. Spend tool calls on
section-specific evidence gathering.

{{PROJECT_INTEL}}

### Your task

Follow the verdict rubric, output format, and NFR-specific gotchas defined in
your agent system prompt. Write your findings to:

```
{{FINDINGS_OUTPUT_PATH}}
```

Use these provenance values verbatim in the findings file's header lines:

- **Audited against:** `{{NFR_SOURCE_URL}}` (sha256 `{{NFR_SOURCE_SHA}}`)
- **Application type:** {{APP_TYPE_HUMAN}}

When you finish, return the one-paragraph summary defined in the shared
rules (path written + verdict counts). The orchestrator uses that paragraph
as a sanity check before reading the file.

## END PROMPT TEMPLATE
