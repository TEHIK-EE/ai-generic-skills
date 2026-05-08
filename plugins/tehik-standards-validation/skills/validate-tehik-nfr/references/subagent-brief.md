# Per-section subagent brief (template)

The orchestrator interpolates the placeholders below and passes the result as the
`prompt` to a subagent (one subagent per NFR section, run in parallel). The
subagent must follow this brief verbatim — its output is consumed mechanically
by the orchestrator's aggregation step.

## How the orchestrator uses this file

1. Read this template.
2. For each section being audited, replace every `{{...}}` placeholder.
3. Spawn a subagent (Agent tool, `subagent_type: general-purpose`) and pass
   the filled-in template as the prompt. Use the `Explore` subagent type
   instead if the section is dominated by code-discovery work.
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

---

## BEGIN PROMPT TEMPLATE

You are auditing section {{SECTION_NUMBER}} ("{{SECTION_TITLE}}") of the TEHIK
non-functional requirements against a real software project. You are one of
several parallel subagents; the orchestrator will aggregate your findings into a
single report. Other sections are being audited concurrently — do not try to
cover them, even if you spot adjacent issues.

### What you must do

1. Read the NFR section at `{{SECTION_MD_PATH}}`. It is a Markdown table chunk
   with the upstream preamble for context. Every NFR row is shaped
   `| **{{SECTION_NUMBER}}.M** | <requirement> | <explanation> | <e-Government CFR> |
   <Self-service> | <Websites> | <COTS> | <Responsible> | <Tested by> |` — a
   `V` in an applicability column means the NFR applies to that application
   type, an empty cell means it does not.

2. For each NFR row, decide a verdict against the project rooted at
   `{{PROJECT_ROOT}}`. The application type is **{{APP_TYPE_HUMAN}}**
   (`{{APP_TYPE}}`). NFRs that do not list a `V` for this app type are
   `NOT_APPLICABLE` — do not waste tool calls investigating them. If
   `{{APP_TYPE}}` is `unknown`, audit every NFR that has at least one `V`.

3. Use Read / Grep / Glob / Bash (read-only) to gather evidence. The
   pre-flight project intel below is reliable; build on it rather than
   re-discovering the same facts.

4. Write your findings to `{{FINDINGS_OUTPUT_PATH}}` using the exact format
   in the "Output format" section below. Then return a one-paragraph summary
   mentioning the path and the rough verdict counts.

### Pre-flight project intel

{{PROJECT_INTEL}}

### Verdict choices and when to use each

- **PASS** — concrete evidence in the project shows the requirement is met.
- **FAIL** — concrete evidence shows the requirement is violated.
- **PARTIAL** — some aspects are met, others aren't, OR the requirement is
  met in some parts of the codebase but not consistently.
- **NOT_APPLICABLE** — the NFR's applicability column for `{{APP_TYPE}}` is
  blank, OR the requirement references a feature this project does not have
  (e.g. "if using LDAP" when the project does not use LDAP). State the
  applicability reason briefly.
- **INSUFFICIENT_INFO** — the requirement cannot be verified from the source
  tree alone (it talks about production deployment, runtime behaviour, third
  parties, contractual agreements, manual processes). Be honest about this
  rather than guessing — the orchestrator surfaces these as items the human
  must verify out-of-band.

For every non-PASS verdict, include an actionable recommendation. "Switch the
appender to `LogstashEncoder` in `src/main/resources/logback-spring.xml`" beats
"Configure JSON logging."

### Confidence

- **HIGH** — direct evidence in the code (specific file/line) leaves no doubt.
- **MEDIUM** — strong inference but the evidence is indirect (e.g. dependency
  present but configuration not located).
- **LOW** — best-effort guess based on project shape; reviewer should verify.

### Output format

Write a Markdown file at `{{FINDINGS_OUTPUT_PATH}}` with the exact structure
below. The aggregator parses it by heading levels, so do not deviate.

```
## Section {{SECTION_NUMBER}}: {{SECTION_TITLE}}

**Audited against:** {{NFR_SOURCE_URL}} (sha256 `{{NFR_SOURCE_SHA}}`)
**Application type:** {{APP_TYPE_HUMAN}}
**Verdict counts:** PASS=… FAIL=… PARTIAL=… NOT_APPLICABLE=… INSUFFICIENT_INFO=…

### NFR {{SECTION_NUMBER}}.1 — <one-line summary of the requirement>

- **Status:** PASS | FAIL | PARTIAL | NOT_APPLICABLE | INSUFFICIENT_INFO
- **Confidence:** HIGH | MEDIUM | LOW
- **Evidence:**
  - `path/to/file.ext:LINE` — short note on what was found
  - (more evidence lines as needed; omit the bullet list entirely if NOT_APPLICABLE)
- **Recommendation:** <only when status is not PASS; otherwise omit this line>
- **Notes:** <optional, only if a caveat is worth surfacing>

### NFR {{SECTION_NUMBER}}.2 — …

(same shape, one block per NFR in section order)
```

### Constraints and gotchas

- Do not modify any project files. This is a read-only audit.
- Do not run anything that has side effects (no network calls except
  package-manifest lookups already in the project, no commits, no tests that
  mutate state). `git status`, `ls`, `grep`, `cat` are fine.
- Do not paraphrase the requirement text in the heading. The one-line summary
  is for human scanning; the verdict applies to the original requirement
  language exactly as written upstream.
- Be honest about INSUFFICIENT_INFO. Audits are most valuable when they
  surface unknowns rather than papering over them.
- Keep evidence references concrete: `file:line`, not vague "mentioned in the
  config." If a project has 50 logging calls and you can't reasonably enumerate
  them all, sample 3-5 representative ones and say so.

### What to return to the orchestrator

A short paragraph: the path you wrote to, total NFRs you audited, and the
verdict counts (e.g. "Wrote findings/section-04.md. 17 NFRs audited: 6 PASS,
3 FAIL, 4 PARTIAL, 0 NOT_APPLICABLE, 4 INSUFFICIENT_INFO"). The orchestrator
uses this paragraph as a sanity check before reading the file.

## END PROMPT TEMPLATE
