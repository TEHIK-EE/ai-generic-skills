# Common auditor rules

Every subagent dispatched by `validate-tehik-nfr` or
`validate-tehik-it-profile` must read this file at the start of its run
and follow the rules below. Skill-specific rules (verdict rubric, output
schema, domain resolution policy) live in the dispatching agent's system
prompt and override nothing in here — the two are complementary.

## Read-only contract

This is a read-only audit of a project under `{{PROJECT_ROOT}}`. You may
**not**:

- Modify any project file (no `Edit`, no `Write`, no `>>`, no patches).
- Run anything with side effects: no commits, no `git checkout` of new
  branches, no `npm install`, no test suites that mutate state, no
  outbound network calls beyond reading the bundled NFR / IT-profile
  document already on disk.
- Touch the project's package manifests, lockfiles, CI configuration,
  or `.git/` directory.

You **may**:

- Read source files (`Read`), search them (`Grep`, `Glob`), and run
  read-only shell commands (`Bash`: `ls`, `cat`, `find`, `wc`,
  `git status`, `git log --oneline`).
- Inspect build manifests (`pom.xml`, `build.gradle(.kts)`,
  `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`,
  `composer.json`, `requirements.txt`, `Pipfile`), CI files
  (`.gitlab-ci.yml`, `.github/workflows/`, `Jenkinsfile`), and
  deployment manifests (`Dockerfile`, `docker-compose.yml`, `helm/`,
  `k8s/`, `compose.yml`). All of these are valid evidence sources.

If you find yourself reaching for any write-side tool, stop — the audit
is broken if it changes the project under audit.

## Confidence ladder

Every verdict you emit must carry exactly one confidence level:

- **HIGH** — direct evidence in the code (a specific `file:line`) leaves
  no doubt.
- **MEDIUM** — strong inference but the evidence is indirect (e.g. the
  dependency is declared but the configuration that activates it is not
  located).
- **LOW** — best-effort guess based on project shape; a human reviewer
  should verify before acting on it.

Pick honestly. A wrong HIGH is worse than a correct MEDIUM, because it
suppresses the reader's instinct to double-check.

## Evidence discipline

For every non-trivial verdict you emit:

- Cite **concrete `file:line` references**, not vague pointers like
  "mentioned in the config" or "seen in tests". The orchestrator's
  aggregation step assumes you wrote real paths.
- If a project has many matches for a pattern (50 logging calls, 30
  imports of the same library), sample **3-5 representative ones** and
  say so explicitly ("sampled 3 of ~30 call sites in `src/api/`"). Do
  not paginate through all of them — the reader cares about presence
  and shape, not enumeration.
- **Never paraphrase the canonical requirement / component text** in
  your output's heading. Copy it verbatim from the document chunk so
  the reader can grep the original document for the exact wording.

## Honesty about INSUFFICIENT_INFO

Audits are most valuable when they surface unknowns rather than papering
over them. If the requirement or component genuinely cannot be verified
from the source tree alone — because it concerns runtime behaviour,
deployment infrastructure, third-party contracts, manual processes, or
physical hardware — say so with `INSUFFICIENT_INFO`. Do not guess. The
orchestrator surfaces these as items the human must verify out-of-band,
which is the correct outcome.

Common categories that almost always end up as `INSUFFICIENT_INFO`:

- Physical infrastructure (HSMs, firewalls, storage hardware, NBD
  support contracts).
- Runtime deployment choices made outside the repo (virtualization
  platform, server OS image actually used in prod, network policy).
- Operational SLAs and contractual matters.
- Manual review processes (security testing, penetration tests, design
  reviews).

## Findings file mechanic

You will be told the absolute path to write your findings to (the
`{{FINDINGS_OUTPUT_PATH}}` placeholder in the dispatch prompt). After
you complete the audit:

1. Write the findings file at exactly that path. Do not write anywhere
   else. The orchestrator's aggregator reads this exact path.
2. Use the output format defined in your agent's system prompt
   verbatim. The aggregator parses by heading levels — drift breaks the
   pipeline.
3. Return a one-paragraph summary to the orchestrator with:
   - The absolute path you wrote to.
   - The number of items audited.
   - The verdict counts in the agent's vocabulary.

Example summary (NFR auditor): "Wrote
`/Users/.../findings/section-04.md`. 17 NFRs audited: 6 PASS, 3 FAIL, 4
PARTIAL, 0 NOT_APPLICABLE, 4 INSUFFICIENT_INFO."

The orchestrator uses this paragraph as a sanity check before reading
the file. A missing or mismatched summary is treated as a subagent
failure.

## Scope discipline

You are one of several parallel subagents. The orchestrator will
aggregate your findings with the others into a single report. Stay
inside your slice:

- Do **not** audit requirements or components that belong to another
  section / layer, even if you spot adjacent issues. Other subagents are
  covering those concurrently and will double-count or conflict if you
  encroach.
- Do **not** restructure or renumber the items in your slice. The IDs
  (e.g. `4.6`, `3.2`) are stable identifiers the final report relies on.
- Do **not** invent new verdict categories. If something doesn't fit
  your agent's vocabulary, the right answer is almost always
  `INSUFFICIENT_INFO` with a `Notes:` line explaining why.
