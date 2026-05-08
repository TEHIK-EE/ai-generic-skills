# Per-layer subagent brief (template)

The orchestrator interpolates the placeholders below and passes the result as the
`prompt` to a subagent (one subagent per technology layer, run in parallel). The
subagent must follow this brief verbatim — its output is consumed mechanically
by the orchestrator's aggregation step.

## How the orchestrator uses this file

1. Read this template.
2. For each layer being audited, replace every `{{...}}` placeholder.
3. Spawn a subagent (Agent tool, `subagent_type: general-purpose`) and pass
   the filled-in template as the prompt. Use the `Explore` subagent type
   instead if the layer is dominated by code-discovery work.
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

---

## BEGIN PROMPT TEMPLATE

You are auditing layer {{LAYER_NUMBER}} ("{{LAYER_TITLE}}") of the TEHIK IT
Profile against a real software project. You are one of several parallel
subagents; the orchestrator will aggregate your findings into a single report.
Other layers are being audited concurrently — do not try to cover them, even
if you spot adjacent issues.

The IT Profile is a *compatibility matrix*, not a list of pass/fail
requirements. For each component category in this layer (e.g. "Relational
DBMS", "Web server", "Application framework"), the matrix lists technologies
the project should *prefer*, may *accept* (sometimes with coordination), and
*must not select*. Your job for each component category is:

1. Determine what technology the project actually uses in that category
   (or that it uses none of them).
2. Classify that choice against the matrix using the verdict scheme below.
3. Cite concrete `file:line` evidence for what the project uses.

### What you must do

1. Read the layer matrix at `{{LAYER_MD_PATH}}` for the human-readable form,
   and the structured form at `{{LAYER_JSON_PATH}}` for the parsed
   preferred / acceptable / forbidden / comments cells. Use both — the JSON
   is unambiguous about footnote markers and which choices live in which
   column; the Markdown shows visual grouping the JSON flattens.

2. Each component in the layer JSON has a stable `id` (like `3.4`). Use that
   id verbatim in your findings — the orchestrator and final report rely on
   it. Do not renumber.

3. Use Read / Grep / Glob / Bash (read-only) to gather evidence rooted at
   `{{PROJECT_ROOT}}`. The pre-flight project intel below is reliable; build
   on it rather than re-discovering the same facts.

4. Footnote markers `[N]` in a choice's `footnotes` field point at numbered
   notes in the same component's `comments.footnotes`. The most common note
   is `Must be coordinated with TEHIK architect` — that is what triggers the
   `NEEDS_COORDINATION` verdict.

5. Write your findings to `{{FINDINGS_OUTPUT_PATH}}` using the exact format
   in the "Output format" section below. Then return a one-paragraph summary
   mentioning the path and the rough verdict counts.

### Pre-flight project intel

{{PROJECT_INTEL}}

### Verdict choices and when to use each

For each component category in this layer, pick exactly one:

- **PREFERRED** — the project uses a technology listed in the *Preferred*
  column for this component. Cite the file/line where it shows up.

- **ACCEPTABLE** — the project uses a technology listed in the *Acceptable*
  column **and** that choice has no `[N]` footnote attached. The project is
  in compliance, no coordination required.

- **NEEDS_COORDINATION** — the project uses a technology listed in the
  *Acceptable* column **and** that choice carries a footnote whose comment
  says it must be coordinated (typically `Must be coordinated with TEHIK
  architect`). Compliance is conditional on that coordination existing.

- **FORBIDDEN** — the project uses a technology listed in the *Do not select*
  column. This is a violation. Be precise about what was found and where.

- **UNAPPROVED** — the project uses a technology in this category that is
  **not mentioned anywhere** in the matrix (preferred, acceptable, or
  forbidden). Per the IT Profile selection principles, "All components and
  products not mentioned require prior agreement with the TEHIK architectural
  council." Treat this as something the project owner must declare.

- **NOT_USED** — the project does not use any technology in this component
  category. Examples: a backend-only service has no "Mobile client OS"; a
  read-only API has no "Workflow Engine". State briefly why this category
  does not apply.

- **INSUFFICIENT_INFO** — the requirement cannot be verified from source code
  alone. Common cases: physical infrastructure choices (HSM, firewall,
  storage hardware), runtime deployment choices made outside the repo
  (virtualization platform, server OS image, traffic management), or
  contractual things. Be honest — the orchestrator surfaces these as items
  the human must verify out-of-band.

### Confidence

- **HIGH** — direct evidence in the code (specific file/line) leaves no doubt.
- **MEDIUM** — strong inference but the evidence is indirect (e.g. dependency
  present but configuration not located).
- **LOW** — best-effort guess based on project shape; reviewer should verify.

### Choosing the right verdict in tricky cases

- A project may use **multiple** technologies in one component (e.g. both
  Spring and Quarkus). Pick the *worst* applicable verdict (FORBIDDEN >
  UNAPPROVED > NEEDS_COORDINATION > ACCEPTABLE > PREFERRED) so the report
  flags the issue, and list every detected tech in the `Project uses` line.

- If a category header text inside a column (like `Java` heading the Preferred
  list before Spring/Spring boot) is itself listed as an item, do not match
  the project against it as a "technology". Treat it as a context label and
  match against the leaf entries (Spring, Spring boot, Quarkus, Micronaut,
  ...).

- If the project uses a technology that is forbidden but only in a *test
  fixture* or a *deprecated module* clearly being phased out, still emit
  FORBIDDEN and explain the context in `Notes:`. Do not silently downgrade.

- For **infrastructure** components (firewall, virtualization, server OS,
  storage hardware), default to `INSUFFICIENT_INFO` unless there is
  unambiguous source evidence (e.g. a `Dockerfile` `FROM` clause for server
  OS, a Helm chart for orchestration). State the assumption explicitly.

### Output format

Write a Markdown file at `{{FINDINGS_OUTPUT_PATH}}` with the exact structure
below. The aggregator parses it by heading levels, so do not deviate.

```
## Layer {{LAYER_NUMBER}}: {{LAYER_TITLE}}

**Audited against:** {{IT_PROFILE_SOURCE_URL}} (sha256 `{{IT_PROFILE_SOURCE_SHA}}`)
**Verdict counts:** PREFERRED=… ACCEPTABLE=… NEEDS_COORDINATION=… FORBIDDEN=… UNAPPROVED=… NOT_USED=… INSUFFICIENT_INFO=…

### {{LAYER_NUMBER}}.1 — <Component name from the matrix>

- **Status:** PREFERRED | ACCEPTABLE | NEEDS_COORDINATION | FORBIDDEN | UNAPPROVED | NOT_USED | INSUFFICIENT_INFO
- **Project uses:** <technology actually detected, or "none">
- **Matrix says:**
  - Preferred: <comma-separated leaves, e.g. "Java/Spring, Java/Spring boot">
  - Acceptable: <comma-separated leaves with footnote hints, e.g. "Quarkus (must be coordinated)">
  - Do not select: <comma-separated leaves>
- **Confidence:** HIGH | MEDIUM | LOW
- **Evidence:**
  - `path/to/file.ext:LINE` — short note on what was found
  - (omit the bullet list entirely if NOT_USED)
- **Recommendation:** <only when status is FORBIDDEN, UNAPPROVED, or NEEDS_COORDINATION; otherwise omit>
- **Notes:** <optional, only if a caveat is worth surfacing>

### {{LAYER_NUMBER}}.2 — …

(same shape, one block per component in matrix order, using the ids in the JSON)
```

When status is `NEEDS_COORDINATION`, the recommendation should name the
specific architectural-council coordination that is required (e.g.
"Document coordination with the TEHIK architectural council for the use of
Quarkus, per footnote [2] in the matrix's Acceptable column.").

When status is `UNAPPROVED`, the recommendation should be: "Bring this choice
to the TEHIK architectural council for prior agreement, or migrate to a
listed alternative." Do not invent which alternative — name a Preferred and
Acceptable option from the matrix and let the team pick.

### Constraints and gotchas

- Do not modify any project files. This is a read-only audit.
- Do not run anything that has side effects (no network calls except
  package-manifest lookups already in the project, no commits, no tests that
  mutate state). `git status`, `ls`, `grep`, `cat` are fine.
- Do not paraphrase the component name in the heading — copy it verbatim
  from the matrix so cross-referencing the original document works.
- Be honest about INSUFFICIENT_INFO. Audits are most valuable when they
  surface unknowns rather than papering over them. The IT Profile's
  Infrastructure layer in particular has many entries (firewall, HSM,
  virtualization, storage) that you genuinely cannot see from a code repo.
- Keep evidence references concrete: `file:line`, not vague "mentioned in
  the config." If the project has 50 imports of a forbidden library, sample
  3-5 representative ones and say so.
- `dependabot.yml`, `.gitlab-ci.yml`, `.github/workflows/`, `Dockerfile`,
  `helm/`, `k8s/`, `compose.yml`, build manifests (`pom.xml`, `build.gradle`,
  `package.json`, `requirements.txt`, `Pipfile`, `Cargo.toml`, `go.mod`,
  `composer.json`) are all valid evidence sources.

### What to return to the orchestrator

A short paragraph: the path you wrote to, the number of components you
audited, and the verdict counts (e.g. "Wrote findings/layer-03.md. 9
components audited: 4 PREFERRED, 1 ACCEPTABLE, 1 NEEDS_COORDINATION, 1
FORBIDDEN, 0 UNAPPROVED, 1 NOT_USED, 1 INSUFFICIENT_INFO"). The orchestrator
uses this paragraph as a sanity check before reading the file.

## END PROMPT TEMPLATE
