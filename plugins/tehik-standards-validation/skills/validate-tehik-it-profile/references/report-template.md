# Final report template

This template has two clearly-marked zones, separated by HTML comment
markers:

1. **Rendered report skeleton** — the Markdown between
   `<!-- begin rendered report -->` and `<!-- end rendered report -->`.
   This is the *only* part that should appear in the final audit file.
   Replace every `{{PLACEHOLDER}}` and copy the rest verbatim. Strip the
   `<!-- begin rendered report -->` and `<!-- end rendered report -->`
   marker comments themselves before writing.
2. **Orchestrator instructions** — everything after
   `<!-- end rendered report -->`. These notes describe how to expand each
   `{{PLACEHOLDER}}`. They are guidance for the orchestrator only and
   **must not** appear in the rendered report.

If you ever find yourself unsure whether a passage belongs in the report
or not: passages inside the rendered zone always render; passages outside
it never do.

---

<!-- begin rendered report -->

# TEHIK IT Profile audit — {{PROJECT_NAME}}

**Date:** {{AUDIT_DATE}}
**Project root:** `{{PROJECT_ROOT}}`
**IT Profile document:** [{{IT_PROFILE_SOURCE_URL}}]({{IT_PROFILE_SOURCE_URL}})
**IT Profile version:** {{IT_PROFILE_VERSION}}
**IT Profile fingerprint:** sha256 `{{IT_PROFILE_SOURCE_SHA}}`
**IT Profile provenance:** {{IT_PROFILE_PROVENANCE}} (`live` = freshly downloaded,
`cached` = local cache, `bundled` = snapshot shipped with the skill)
{{#IT_PROFILE_FALLBACK_REASON}}**Fallback note:** {{IT_PROFILE_FALLBACK_REASON}}{{/IT_PROFILE_FALLBACK_REASON}}

## Executive summary

The TEHIK IT Profile is a tech-stack compatibility matrix: every component
category (web server, relational DBMS, programming language, etc.) lists
*Preferred*, *Acceptable*, and *Do not select* technologies. This audit walks
the matrix layer by layer and classifies the project's actual choices into
the seven verdicts below.

{{TOTAL_COMPONENTS}} component categories across {{LAYER_COUNT}} layers were
audited. The IT Profile's *Servers* hardware standard and the
*Technical-requirement selection principles* are intentionally **out of
scope** for a static repository audit (see below).

| Verdict | Count | % of audited | Meaning |
|---------|------:|-------------:|---------|
| PREFERRED | {{COUNT_PREFERRED}} | {{PCT_PREFERRED}} | Project uses a Preferred-column choice |
| ACCEPTABLE | {{COUNT_ACCEPTABLE}} | {{PCT_ACCEPTABLE}} | Project uses an Acceptable-column choice (no footnote) |
| NEEDS_COORDINATION | {{COUNT_NEEDS_COORDINATION}} | {{PCT_NEEDS_COORDINATION}} | Acceptable, but the matrix flags it as needing TEHIK architect coordination |
| FORBIDDEN | {{COUNT_FORBIDDEN}} | {{PCT_FORBIDDEN}} | Project uses a Do-not-select choice — violation |
| UNAPPROVED | {{COUNT_UNAPPROVED}} | {{PCT_UNAPPROVED}} | Project uses something not in the matrix at all — needs prior agreement |
| NOT_USED | {{COUNT_NOT_USED}} | {{PCT_NOT_USED}} | No component of this category in the project |
| INSUFFICIENT_INFO | {{COUNT_INSUFFICIENT_INFO}} | {{PCT_INSUFFICIENT_INFO}} | Cannot tell from source (deploy-time / contractual / hardware) |

{{TOP_FAILURES_BLURB}}

## Out of scope: Servers — Hardware standard

This skill **does not audit hardware standards**. Those requirements are
about physical servers — chassis redundancy, hot-swappable disks, remote
management interfaces, maintenance contracts — and cannot be verified from
source code. Treat the items below as a checklist for the procurement /
operations team.

{{SERVERS_OUT_OF_SCOPE_LIST}}

## Out of scope: IT Profile selection principles

The IT Profile opens with five general selection principles. They apply to
the project as a whole, not to any one component, and cannot be objectively
PASS/FAIL-graded from a static audit. Listed here so the reader knows they
exist and were not silently ignored.

{{SELECTION_PRINCIPLES_LIST}}

## Out of scope: General governance

The IT Profile's "General" section lists policy-level governance points
(centralized procurement, architectural council approvals, annual review).
These are not project-level checks; they describe how the IT Profile itself
is maintained.

{{GENERAL_GOVERNANCE_LIST}}

## Layer findings

The blocks below cover every audited component category, one H3 heading per
component, in matrix order. Each block carries the project's detected
technology, the matrix's *Preferred* / *Acceptable* / *Do not select*
choices, file:line evidence from the project, and — when the verdict is
not PREFERRED — a recommendation. All evidence is inlined; this report
contains no "see fragment file" links.

{{LAYER_FINDINGS_BLOCKS}}

## Critical issues (rolled up)

The items below are the FORBIDDEN and UNAPPROVED verdicts pulled out of
every layer, ordered by component id. Each entry references the matching
`### <N>.<n>` block above (which lives in the same document). Address these
first — they are direct IT Profile violations.

{{CRITICAL_ISSUES_LIST}}

## Coordination required

The components below are using *Acceptable* choices that the IT Profile
flags as requiring coordination with the TEHIK architectural council. The
choice itself is allowed, but the team must have explicit architect approval
on file.

{{NEEDS_COORDINATION_LIST}}

## Items needing human verification (INSUFFICIENT_INFO)

These component categories cannot be confirmed from source code alone.
Treat them as a checklist for the deployment review, infrastructure audit,
or contract verification.

{{UNKNOWN_ITEMS_LIST}}

## Recommendations

{{RECOMMENDATIONS_LIST}}

## Methodology

- The skill split the upstream IT Profile matrix by technology layer and ran
  one subagent per layer in parallel. Each subagent saw only its layer's
  rows plus a short pre-flight fact sheet about this project, so context
  size remained manageable regardless of project size.
- Verdicts are: `PREFERRED`, `ACCEPTABLE`, `NEEDS_COORDINATION`, `FORBIDDEN`,
  `UNAPPROVED`, `NOT_USED`, `INSUFFICIENT_INFO`. The taxonomy preserves the
  matrix's distinctions between "the matrix prefers this", "the matrix
  accepts this with coordination", and "the matrix forbids this".
- An `UNAPPROVED` verdict means the project uses a technology not listed in
  the matrix at all. Per the IT Profile selection principles, "All
  components and products not mentioned require prior agreement with the
  TEHIK architectural council."
- Confidence levels are `HIGH` (direct evidence), `MEDIUM` (strong
  inference), `LOW` (best-effort guess; reviewer should verify).
- Sections of the IT Profile that cannot be statically audited (Servers
  hardware standard, top-level selection principles, governance points)
  are listed under "Out of scope" rather than scored.

## Provenance

| Field | Value |
|-------|-------|
| Skill | `tehik-standards-validation` / `validate-tehik-it-profile` |
| Skill version | {{SKILL_VERSION}} |
| Audit started at | {{AUDIT_STARTED}} |
| Audit completed at | {{AUDIT_COMPLETED}} |
| Subagents dispatched | {{SUBAGENT_COUNT}} (one per layer) |
| Total components evaluated | {{COUNT_AUDITED}} |
| IT Profile document URL | {{IT_PROFILE_SOURCE_URL}} |
| IT Profile document version | {{IT_PROFILE_VERSION}} |
| IT Profile document sha256 | `{{IT_PROFILE_SOURCE_SHA}}` |
| IT Profile document provenance | {{IT_PROFILE_PROVENANCE}} |

<!-- end rendered report -->

---

# Orchestrator instructions (do not include in the rendered report)

The notes below describe how to expand each `{{PLACEHOLDER}}` in the
rendered skeleton above. Read the placeholder you are filling, then copy
the resolved value into its slot. Discard everything in this section
before writing the final report file.

## {{LAYER_FINDINGS_BLOCKS}}

Concatenate, in layer order (1, 2, 3, …), one block per audited layer
copied verbatim from `findings/layer-NN.md`. Each layer block has the
shape below:

```
## Layer <N>: <Layer title>

**Verdict counts:** PREFERRED=… ACCEPTABLE=… NEEDS_COORDINATION=… FORBIDDEN=… UNAPPROVED=… NOT_USED=… INSUFFICIENT_INFO=…

<optional 1-3 sentence narrative summary highlighting the layer's top
violations or surprises — useful for skim readers, but never a
substitute for the per-component list below>

### <N>.1 — <Component name from the matrix>
- **Status:** PREFERRED | ACCEPTABLE | NEEDS_COORDINATION | FORBIDDEN | UNAPPROVED | NOT_USED | INSUFFICIENT_INFO
- **Project uses:** <detected technology, or "none">
- **Matrix says:**
  - Preferred: <comma-separated leaves>
  - Acceptable: <comma-separated leaves with footnote hints>
  - Do not select: <comma-separated leaves>
- **Confidence:** HIGH | MEDIUM | LOW
- **Evidence:**
  - `path/to/file.ext:LINE` — short note on what was found
  - (omit the bullet list entirely if NOT_USED)
- **Recommendation:** <only when status is FORBIDDEN, UNAPPROVED, or NEEDS_COORDINATION>
- **Notes:** <optional, only if a caveat is worth surfacing>

### <N>.2 — …
(repeat for every component row in layer <N>, in matrix order, with no
gaps)
```

Do not skip components, do not paraphrase them away, do not link out to
fragment files. The completeness check in Step 7 of SKILL.md counts
component headings — missing ones flag the run as incomplete.

## {{CRITICAL_ISSUES_LIST}}

Roll up every FORBIDDEN and UNAPPROVED verdict, ordered by component id.
Each entry should reference its `### <N>.<n>` block above by id and title.
Pick the format that reads best for the count:

- ≤ 5 issues → bullet list, one bullet per issue with a 1-2 sentence
  summary.
- ≥ 6 issues → a `| ID | Title | Verdict | One-line summary |` table,
  pipe-separated.

If there are zero critical issues, write the literal sentence "No
FORBIDDEN or UNAPPROVED verdicts were found."

## {{NEEDS_COORDINATION_LIST}}

Roll up every NEEDS_COORDINATION verdict in the same shape as
`{{CRITICAL_ISSUES_LIST}}`, but include the matrix footnote text so the
reader sees *why* coordination is required (e.g. "footnote [1] — must be
coordinated with TEHIK architect"). If there are zero, write "No
coordination items."

## {{UNKNOWN_ITEMS_LIST}}

Roll up every INSUFFICIENT_INFO verdict in the same shape. The
"What to check" column should describe the verification surface
(operations team, contract review, fleet inventory, platform repo, etc.)
— not just restate that the item is unknown. If there are zero, write
"No INSUFFICIENT_INFO items."

## {{RECOMMENDATIONS_LIST}}

Group by layer, in component-id order. Pull one recommendation per
non-PREFERRED component (the recommendation already lives in the
per-component block; this section is a layer-grouped index of them).

**Do not assert specific verdict counts in narrative prose** (e.g. "the
eight INSUFFICIENT_INFO items", "the three coordination items"). The
Executive summary table already carries exact counts; restating them in
narrative is brittle and tends to drift between revisions. Write "the
platform INSUFFICIENT_INFO items", "the items under Layer 5", or
"the coordination items above" instead. If a count is genuinely needed
for emphasis, double-check it against the verdict table immediately
before writing.

## {{TOP_FAILURES_BLURB}}

A 2-4 sentence executive narrative under the verdict table that
highlights the architectural shape of the findings (e.g. "The audit
surfaced violations clustering around a single legacy Oracle spine"
rather than "There are 6 FORBIDDEN verdicts"). Same no-counts rule
applies — talk about themes, not numbers.

## {{SKILL_VERSION}}

Read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and copy the
`version` field verbatim (typically `1.0.0` or similar). If the file is
unreadable for any reason, write the literal value `unknown` — never
omit the row, since downstream consumers compare reports across runs and
expect the row to exist.

## Out-of-scope list placeholders

- **{{SERVERS_OUT_OF_SCOPE_LIST}}** — render every item in
  `manifest.json` → `out_of_scope.servers` as a `- ` bullet, in order.
- **{{SELECTION_PRINCIPLES_LIST}}** — same shape, from
  `out_of_scope.selection_principles`.
- **{{GENERAL_GOVERNANCE_LIST}}** — same shape, from
  `out_of_scope.general`.

## Verdict count placeholders

- **{{TOTAL_COMPONENTS}}** — `manifest.json` → `total_components`.
- **{{LAYER_COUNT}}** — number of audited layers (typically the same as
  `manifest.json` → `layer_count`, but may be smaller for partial runs).
- **{{COUNT_PREFERRED}} / COUNT_ACCEPTABLE / COUNT_NEEDS_COORDINATION /
  COUNT_FORBIDDEN / COUNT_UNAPPROVED / COUNT_NOT_USED /
  COUNT_INSUFFICIENT_INFO** — sums across all audited layers.
- **{{PCT_*}}** — corresponding percentage, formatted to one decimal
  place (e.g. `37.3%`). All seven PCT values must add up to 100 ± 0.1.
- **{{COUNT_AUDITED}}** — sum of `component_count` across the dispatched
  layers (i.e. the seven verdict counts above add up to this).

## Header / metadata placeholders

- **{{PROJECT_NAME}}** — taken from the project's package manifest
  (`name` in `package.json`, `artifactId` in `pom.xml`, `name` in
  `Cargo.toml`, etc.); if no manifest exists, fall back to the basename
  of `{{PROJECT_ROOT}}`.
- **{{PROJECT_ROOT}}** — absolute path of the audited project, taken
  from the orchestrator's working state.
- **{{AUDIT_DATE}}** — ISO date (`YYYY-MM-DD`) when the orchestrator
  started the run.
- **{{AUDIT_STARTED}} / {{AUDIT_COMPLETED}}** — ISO 8601 UTC timestamps
  (`YYYY-MM-DDTHH:MM:SSZ`).
- **{{SUBAGENT_COUNT}}** — number of layer subagents the orchestrator
  actually dispatched (1 ≤ value ≤ {{LAYER_COUNT}}).
- **{{IT_PROFILE_SOURCE_URL}} / {{IT_PROFILE_VERSION}} /
  {{IT_PROFILE_SOURCE_SHA}} / {{IT_PROFILE_PROVENANCE}} /
  {{IT_PROFILE_FALLBACK_REASON}}** — copy verbatim from the
  `fetch_it_profile.py` JSON output. The fallback-reason line is
  conditional: emit the `**Fallback note:** ...` line only if
  `fallback_reason` is non-null in the fetch JSON.
