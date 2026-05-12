# Final report template

The orchestrator concatenates this template with subagent findings to produce
the user-facing audit report. Replace `{{...}}` placeholders during assembly.

---

# TEHIK NFR audit — {{PROJECT_NAME}}

**Date:** {{AUDIT_DATE}}
**Project root:** `{{PROJECT_ROOT}}`
**Application type:** {{APP_TYPE_HUMAN}} (`{{APP_TYPE}}`)
**NFR document:** [{{NFR_SOURCE_URL}}]({{NFR_SOURCE_URL}})
**NFR document fingerprint:** sha256 `{{NFR_SOURCE_SHA}}`
**NFR provenance:** {{NFR_PROVENANCE}} (`live` = freshly downloaded, `cached` =
local cache, `bundled` = snapshot shipped with the skill)
{{#NFR_FALLBACK_REASON}}**Fallback note:** {{NFR_FALLBACK_REASON}}{{/NFR_FALLBACK_REASON}}

## Executive summary

{{TOTAL_NFRS}} requirements across 12 sections. Section 1 is intentionally
**out of scope** for this skill (see below); the audit covers sections 2-12.

| Verdict | Count | % of audited |
|---------|------:|-------------:|
| PASS | {{COUNT_PASS}} | {{PCT_PASS}} |
| FAIL | {{COUNT_FAIL}} | {{PCT_FAIL}} |
| PARTIAL | {{COUNT_PARTIAL}} | {{PCT_PARTIAL}} |
| NOT_APPLICABLE | {{COUNT_NA}} | {{PCT_NA}} |
| INSUFFICIENT_INFO | {{COUNT_UNKNOWN}} | {{PCT_UNKNOWN}} |

{{TOP_FAILURES_BLURB}}

## Section 1: Compliance with general standards (out of scope)

This skill **does not audit section 1**. Those requirements depend on
external standards (X-Road, OWASP ASVS, WCAG 2.2, IT Profile of the Ministry
of Social Affairs, e-Government CFR, RIA cryptographic guidance, EMTAK
classification, ADS address service, Veera design system, RFC 5322, etc.)
and require dedicated tooling, human review, or third-party testing that is
out of reach of a static repository audit.

The requirements that fall under section 1 — and that you must verify
out-of-band — are listed below.

{{SECTION_1_NFR_LIST}}

## Section findings

`{{SECTION_FINDINGS_BLOCKS}}` is the single biggest part of the report — it
must contain **one block per audited NFR**, copied directly from each
subagent's `findings/section-NN.md`. No fragment-file references, no
"detailed evidence: see file X" links. The reader opens this report and
sees everything.

For each audited section (2 through 12), emit:

```
## Section <N>: <title>

**Verdict counts:** PASS=… FAIL=… PARTIAL=… NOT_APPLICABLE=… INSUFFICIENT_INFO=…

<optional: a 1-3 sentence narrative summary highlighting the section's
top failures or surprises — useful for skim readers, but never a
substitute for the per-NFR list below>

### NFR <N>.1 — <one-line summary of the requirement>
- **Status:** PASS | FAIL | PARTIAL | NOT_APPLICABLE | INSUFFICIENT_INFO
- **Confidence:** HIGH | MEDIUM | LOW
- **Evidence:**
  - `path/to/file.ext:LINE` — short note on what was found
  - (more bullets as needed; omit the bullet list entirely if NOT_APPLICABLE)
- **Recommendation:** <only when status is not PASS>
- **Notes:** <optional, only if a caveat is worth surfacing>

### NFR <N>.2 — …

(repeat for every NFR row in section <N>, in order, with no gaps)
```

Replace `{{SECTION_FINDINGS_BLOCKS}}` with all eleven section blocks
concatenated in order (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Do not
skip NFRs, do not paraphrase them away, do not link out to fragment
files. The completeness check in Step 8 of the SKILL counts NFR
headings; missing ones will cause the run to be flagged incomplete.

## Critical issues (rolled up)

The items below are the FAIL verdicts pulled out of every section, ordered
by section number. Each entry references the matching `### NFR <N>.<n>`
block above (which lives in the same document).

{{CRITICAL_ISSUES_LIST}}

## Items needing human verification (INSUFFICIENT_INFO)

These NFRs cannot be confirmed from source code alone. Treat them as a
checklist for the test phase, deployment review, or contract verification.

{{UNKNOWN_ITEMS_LIST}}

## Recommendations

{{RECOMMENDATIONS_LIST}}

## Methodology

- The skill split the upstream NFR document by section and ran one subagent
  per audited section in parallel. Each subagent saw only its section plus a
  short pre-flight fact sheet about this project, so context size remained
  manageable regardless of project size.
- The application type was determined as `{{APP_TYPE}}` ({{APP_TYPE_SOURCE}}).
  NFRs that did not list this application type as in-scope were marked
  `NOT_APPLICABLE` automatically.
- Verdicts are: `PASS`, `FAIL`, `PARTIAL`, `NOT_APPLICABLE`,
  `INSUFFICIENT_INFO`. The latter is reserved for requirements that cannot be
  verified from the source tree (production behaviour, manual processes,
  contractual agreements, third-party operations).
- Confidence levels are `HIGH` (direct evidence), `MEDIUM` (strong inference),
  `LOW` (best-effort guess; reviewer should verify).

## Provenance

| Field | Value |
|-------|-------|
| Skill | `tehik-standards-validation` / `validate-tehik-nfr` |
| Skill version | {{SKILL_VERSION}} |
| Audit started at | {{AUDIT_STARTED}} |
| Audit completed at | {{AUDIT_COMPLETED}} |
| Subagents dispatched | {{SUBAGENT_COUNT}} (sections 2-12) |
| Total NFRs evaluated | {{COUNT_AUDITED}} |
| NFR document URL | {{NFR_SOURCE_URL}} |
| NFR document sha256 | `{{NFR_SOURCE_SHA}}` |
| NFR document provenance | {{NFR_PROVENANCE}} |
