#!/usr/bin/env python3
"""
Split the TEHIK NFR Markdown document into per-section files.

The upstream document (mittefunktsionaalsed-nouded.en.md) is a single ~140-row
Markdown table grouped into 12 sections. This script chunks it so each section
can be handed to its own subagent without the others bloating context.

For every section it writes:
  out/section-NN-<slug>.md     - readable Markdown chunk fed to the subagent.
                                  Includes the upstream preamble + table header
                                  + the section's rows verbatim.
  out/section-NN-<slug>.json   - structured records (id, requirement text,
                                  explanation, applicability flags, etc.) for
                                  programmatic filtering by the orchestrator.

It also writes:
  out/manifest.json            - index of every section with NFR counts and
                                  applicability stats, plus document metadata
                                  (URL, sha256, fetched_at) carried in.

The script does *not* care which sections are in/out of scope - section 1 is
treated like any other. Skipping section 1 is the orchestrator's job.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

SECTION_HEADER_RE = re.compile(r"^(\d+)\.\s+(.+?)$")
NFR_ID_RE = re.compile(r"^(\d+)\.(\d+)$")


def slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "section"


def split_pipes(line: str) -> list[str] | None:
    """Split a Markdown table row into cells. Returns None if not a table row."""
    if not line.startswith("|"):
        return None
    parts = line.split("|")
    if len(parts) < 3:
        return None
    return [p.strip() for p in parts[1:-1]]


def is_separator_row(cells: list[str]) -> bool:
    return all(c == "" or set(c) <= {"-", ":"} for c in cells) and any("-" in c for c in cells)


def strip_bold(text: str) -> str:
    return text.strip().removeprefix("**").removesuffix("**").strip()


def detect_section_header(cells: list[str]) -> tuple[int, str] | None:
    if not cells:
        return None
    first = strip_bold(cells[0])
    rest_empty = all(c == "" for c in cells[1:])
    if not rest_empty:
        return None
    m = SECTION_HEADER_RE.match(first)
    if not m:
        return None
    return int(m.group(1)), strip_bold(m.group(2))


def detect_nfr_id(cells: list[str]) -> str | None:
    if not cells:
        return None
    first = strip_bold(cells[0])
    return first if NFR_ID_RE.match(first) else None


def applies(cell: str) -> bool:
    return cell.strip().upper() == "V"


def parse(md_text: str) -> tuple[list[str], list[str], list[dict]]:
    """Return (preamble_lines, header_lines, sections).

    preamble_lines: verbatim lines from the intro before the NFR table starts
    header_lines: the column-header + separator rows of the NFR table
    sections: list of {number, title, header_line, nfr_lines: [...], nfrs: [{...}]}
    """
    lines = md_text.splitlines()

    nfr_table_start: int | None = None
    for i, line in enumerate(lines):
        cells = split_pipes(line)
        if cells is None:
            continue
        if any("Requirement no." in c for c in cells):
            nfr_table_start = i
            break
    if nfr_table_start is None:
        raise ValueError("Could not locate the NFR table header row (looked for 'Requirement no.')")

    preamble = lines[:nfr_table_start]
    header_line = lines[nfr_table_start]
    if nfr_table_start + 1 >= len(lines):
        raise ValueError("Header row has no following separator row")
    sep_line = lines[nfr_table_start + 1]
    sep_cells = split_pipes(sep_line)
    if sep_cells is None or not is_separator_row(sep_cells):
        raise ValueError(f"Expected separator row after header at line {nfr_table_start + 2}")

    header_cells = split_pipes(header_line) or []

    def col_index(label_substring: str) -> int | None:
        for idx, cell in enumerate(header_cells):
            if label_substring.lower() in strip_bold(cell).lower():
                return idx
        return None

    col_req = col_index("requirement content")
    col_expl = col_index("explanations")
    col_egov = col_index("e-government cfr")
    col_self = col_index("self-service")
    col_web = col_index("websites")
    col_cots = col_index("cots")
    col_resp = col_index("person responsible")
    col_test = col_index("testing is carried out")

    sections: list[dict] = []
    current: dict | None = None
    for i in range(nfr_table_start + 2, len(lines)):
        line = lines[i]
        cells = split_pipes(line)
        if cells is None:
            continue
        if is_separator_row(cells):
            continue

        section_match = detect_section_header(cells)
        if section_match:
            number, title = section_match
            current = {
                "number": number,
                "title": title,
                "header_line": line,
                "nfr_lines": [],
                "nfrs": [],
            }
            sections.append(current)
            continue

        nfr_id = detect_nfr_id(cells)
        if nfr_id is None or current is None:
            continue

        def get(idx: int | None) -> str:
            if idx is None or idx >= len(cells):
                return ""
            return cells[idx]

        record = {
            "id": nfr_id,
            "raw_row": line,
            "requirement": get(col_req),
            "explanation": get(col_expl),
            "egov_cfr": get(col_egov),
            "applies_to": {
                "self_service": applies(get(col_self)),
                "websites": applies(get(col_web)),
                "cots": applies(get(col_cots)),
            },
            "responsible": get(col_resp),
            "tested_by": get(col_test),
        }
        current["nfr_lines"].append(line)
        current["nfrs"].append(record)

    return preamble, [header_line, sep_line], sections


def render_section_md(
    section: dict,
    preamble: list[str],
    header_lines: list[str],
    source_meta: dict,
) -> str:
    out: list[str] = []
    out.append(f"# TEHIK NFR section {section['number']}: {section['title']}\n")
    out.append("> Generated by split_sections.py for a subagent. Contains only this section's rows.\n")
    out.append(f"> Source: {source_meta.get('url', 'unknown')}\n")
    if source_meta.get("sha256"):
        out.append(f"> Source sha256: {source_meta['sha256']}\n")
    if source_meta.get("fetched_at"):
        out.append(f"> Fetched: {source_meta['fetched_at']}\n")
    if source_meta.get("source"):
        out.append(f"> Provenance: {source_meta['source']}\n")
    out.append("")
    out.append("## Document preamble (verbatim from upstream)\n")
    out.extend(preamble)
    out.append("")
    out.append(f"## Section {section['number']}: {section['title']}\n")
    out.extend(header_lines)
    out.append(section["header_line"])
    out.extend(section["nfr_lines"])
    out.append("")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("nfr_path", type=pathlib.Path, help="Path to the NFR markdown (output of fetch_nfrs.py)")
    p.add_argument("--out", type=pathlib.Path, required=True, help="Output directory")
    p.add_argument("--source-meta", type=pathlib.Path, help="Optional path to fetch_nfrs.py JSON output for provenance")
    args = p.parse_args()

    md_text = args.nfr_path.read_text(encoding="utf-8")
    preamble, header_lines, sections = parse(md_text)

    if not sections:
        print("ERROR: parsed 0 sections - upstream document may have changed structure", file=sys.stderr)
        return 2

    source_meta: dict = {}
    if args.source_meta and args.source_meta.exists():
        try:
            source_meta = json.loads(args.source_meta.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"WARN: could not parse source-meta JSON: {e}", file=sys.stderr)

    args.out.mkdir(parents=True, exist_ok=True)

    manifest = {
        "source": source_meta,
        "section_count": len(sections),
        "total_nfrs": sum(len(s["nfrs"]) for s in sections),
        "sections": [],
    }

    for s in sections:
        slug = slugify(s["title"])
        base = f"section-{s['number']:02d}-{slug}"
        md_path = args.out / f"{base}.md"
        json_path = args.out / f"{base}.json"

        md_path.write_text(render_section_md(s, preamble, header_lines, source_meta), encoding="utf-8")
        json_path.write_text(
            json.dumps(
                {
                    "section_number": s["number"],
                    "section_title": s["title"],
                    "nfrs": s["nfrs"],
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        applic = {"self_service": 0, "websites": 0, "cots": 0}
        for n in s["nfrs"]:
            for k, v in n["applies_to"].items():
                applic[k] += int(v)

        manifest["sections"].append({
            "number": s["number"],
            "title": s["title"],
            "slug": slug,
            "md_path": str(md_path.resolve()),
            "json_path": str(json_path.resolve()),
            "nfr_count": len(s["nfrs"]),
            "applicable_counts": applic,
        })

    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    json.dump(manifest, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
