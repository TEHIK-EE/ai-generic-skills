#!/usr/bin/env python3
"""
Split the TEHIK IT Profile Markdown document into per-layer files.

The upstream document (IT-profiil.en.md) is one large 5-column compatibility
matrix grouped into technology layers (Client, Presentation, Application,
Persistence, Infrastructure, Other Aspects). Trying to evaluate every layer
in one context window blows up; this script chunks the matrix so each layer
can be handed to its own subagent.

For every layer it writes:
  out/layer-NN-<slug>.md   - readable Markdown chunk fed to the subagent.
                              Includes the upstream preamble + table header
                              + the layer's component rows verbatim.
  out/layer-NN-<slug>.json - structured records (component name, preferred /
                              acceptable / forbidden choices, footnote
                              definitions, comments) for programmatic use.

It also writes:
  out/manifest.json        - index of every layer with component counts plus
                              an out_of_scope block (Servers hardware standard
                              and the technical-requirement selection
                              principles), and document provenance carried in.

The script does not decide what is in or out of scope - the orchestrator
acknowledges out_of_scope content in the final report; this script only
extracts it.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys


HEADER_CELL_PATTERN = re.compile(r"\*\*\s*Component\s*\*\*", re.IGNORECASE)
SERVERS_HEADING = re.compile(r"^##\s+Servers\b", re.IGNORECASE)
GENERAL_HEADING = re.compile(r"^##\s+General\b", re.IGNORECASE)
TECH_REQ_HEADING = re.compile(r"^##\s+Technical requirements", re.IGNORECASE)
APPLIES_HEADING = re.compile(r"^##\s+Applies to building", re.IGNORECASE)
NUMBERED_TOP = re.compile(r"^\s*(\d+)\.\s+(.*)$")
NUMBERED_NESTED = re.compile(r"^\s{4,}(\d+)\.\s+(.*)$")
TRAILING_TABLE_PIPES = re.compile(r"\s*\|\s*(?:\|\s*)+$")
FOOTNOTE_REF = re.compile(r"\[(\d+)\]")
FOOTNOTE_DEF_START = re.compile(r"^\s*\[(\d+)\]\s*(.*)$")


def slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "layer"


def split_pipes(line: str) -> list[str] | None:
    """Split a Markdown table row into trimmed cells. None if not a table row."""
    if not line.startswith("|"):
        return None
    parts = line.split("|")
    if len(parts) < 3:
        return None
    return [p.strip() for p in parts[1:-1]]


def is_separator_row(cells: list[str]) -> bool:
    return all(c == "" or set(c) <= {"-", ":"} for c in cells) and any("-" in c for c in cells)


def is_empty_row(cells: list[str]) -> bool:
    return all(c == "" for c in cells)


def strip_bold(text: str) -> str:
    s = text.strip()
    while s.startswith("**") and s.endswith("**") and len(s) >= 4:
        s = s[2:-2].strip()
    return s


def is_layer_separator(cells: list[str]) -> bool:
    """A layer row has bold-only content in col 0 and empty everywhere else."""
    if not cells:
        return False
    first_raw = cells[0].strip()
    rest_empty = all(c == "" for c in cells[1:])
    if not rest_empty:
        return False
    return first_raw.startswith("**") and first_raw.endswith("**") and len(first_raw) >= 4


def unescape_brackets(text: str) -> str:
    """Markdown source uses \\[1\\] to keep footnote markers literal. Unescape."""
    return text.replace("\\[", "[").replace("\\]", "]")


def parse_choice_cell(cell: str) -> dict:
    """
    Parse a Preferred / Acceptable / Do-not-select cell.

    Returns:
      {
        "raw": "<verbatim cell content with <br> intact>",
        "items": [{"text": "Spring", "footnotes": [1]}, ...]
      }
    """
    raw = cell.strip()
    if not raw:
        return {"raw": "", "items": []}
    cleaned = unescape_brackets(raw)
    parts = re.split(r"<br\s*/?>", cleaned, flags=re.IGNORECASE)
    items: list[dict] = []
    for part in parts:
        s = part.strip()
        if not s:
            continue
        s = re.sub(r"^[-*]\s+", "", s)
        if not s:
            continue
        footnotes = [int(m.group(1)) for m in FOOTNOTE_REF.finditer(s)]
        text = FOOTNOTE_REF.sub("", s).strip()
        if not text:
            continue
        items.append({"text": text, "footnotes": footnotes})
    return {"raw": raw, "items": items}


def parse_comments_cell(cell: str) -> dict:
    """
    Parse the Comments cell into footnote definitions and any general note.

    Returns:
      {
        "raw": "<verbatim>",
        "footnotes": {1: "Must be coordinated with TEHIK architect", 2: "..."},
        "general": "free text not tied to a numbered footnote, or empty"
      }
    """
    raw = cell.strip()
    if not raw:
        return {"raw": "", "footnotes": {}, "general": ""}
    cleaned = unescape_brackets(raw)
    parts = [p.strip() for p in re.split(r"<br\s*/?>", cleaned, flags=re.IGNORECASE)]
    footnotes: dict[int, list[str]] = {}
    general_buf: list[str] = []
    cur: int | None = None
    for part in parts:
        if not part:
            continue
        m = FOOTNOTE_DEF_START.match(part)
        if m:
            cur = int(m.group(1))
            footnotes.setdefault(cur, [])
            tail = m.group(2).strip()
            if tail:
                footnotes[cur].append(tail)
        else:
            if cur is not None:
                footnotes[cur].append(part)
            else:
                general_buf.append(part)
    return {
        "raw": raw,
        "footnotes": {k: " ".join(v).strip() for k, v in footnotes.items()},
        "general": " ".join(general_buf).strip(),
    }


def find_table_header(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        cells = split_pipes(line)
        if cells is None:
            continue
        if any(HEADER_CELL_PATTERN.search(c) for c in cells):
            return i
    raise ValueError("Could not locate the matrix table header (looked for a cell containing 'Component')")


def index_for(headers: list[str], substring: str) -> int | None:
    target = substring.lower()
    for idx, cell in enumerate(headers):
        if target in strip_bold(cell).lower():
            return idx
    return None


def collect_numbered_items(lines: list[str], start_idx: int) -> tuple[list[dict], int]:
    """
    From start_idx, collect a numbered list (1. ..., 2. ...) and any nested
    items (   1. ..., indented). Stop when a non-list-looking line appears.
    Returns (items, next_idx).
    """
    items: list[dict] = []
    i = start_idx
    while i < len(lines):
        raw = lines[i]
        if raw.strip() == "":
            i += 1
            continue
        if raw.lstrip().startswith("#"):
            break
        if raw.lstrip().startswith("|"):
            break
        m_top = NUMBERED_TOP.match(raw)
        m_nested = NUMBERED_NESTED.match(raw)
        if m_top and not m_nested:
            text = m_top.group(2).strip()
            text = TRAILING_TABLE_PIPES.sub("", text).strip()
            items.append({"text": text, "children": []})
        elif m_nested and items:
            text = m_nested.group(2).strip()
            text = TRAILING_TABLE_PIPES.sub("", text).strip()
            items[-1]["children"].append(text)
        else:
            # tolerate stray lines (e.g. continuation prose) by appending to
            # the most recent item if any, otherwise drop
            stripped = raw.strip()
            stripped = TRAILING_TABLE_PIPES.sub("", stripped).strip()
            if items and stripped:
                if items[-1]["children"]:
                    items[-1]["children"][-1] += " " + stripped
                else:
                    items[-1]["text"] += " " + stripped
            elif stripped:
                # no anchor, ignore quietly
                pass
        i += 1
    return items, i


def parse(md_text: str) -> dict:
    lines = md_text.splitlines()
    title = ""
    version = ""
    for line in lines[:10]:
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        m = re.match(r"^\*\*\s*Version:\s*(.+?)\s*\*\*\s*$", line)
        if m:
            version = m.group(1).strip()

    general: list[dict] = []
    selection_principles: list[dict] = []
    servers: list[dict] = []
    preamble_lines: list[str] = []

    for i, line in enumerate(lines):
        if GENERAL_HEADING.match(line):
            general, _ = collect_numbered_items(lines, i + 1)
        elif TECH_REQ_HEADING.match(line):
            # The first numbered item is "The principles of selection..." with
            # nested children that are the actual five principles. Flatten so
            # the report just shows the principles list.
            items, _ = collect_numbered_items(lines, i + 1)
            if items and items[0].get("children"):
                selection_principles = [{"text": c, "children": []} for c in items[0]["children"]]
            else:
                selection_principles = items
        elif SERVERS_HEADING.match(line):
            items, _ = collect_numbered_items(lines, i + 1)
            # Same flattening trick: the doc nests the items under "Hardware standard"
            if items and items[0].get("children"):
                servers = [{"text": c, "children": []} for c in items[0]["children"]]
            else:
                servers = items
        elif APPLIES_HEADING.match(line):
            preamble_lines = lines[: i + 1]

    if not preamble_lines:
        # Fall back: everything before the table header
        try:
            header_idx = find_table_header(lines)
            preamble_lines = lines[:header_idx]
        except ValueError:
            preamble_lines = lines[:30]

    header_idx = find_table_header(lines)
    header_cells = split_pipes(lines[header_idx]) or []
    sep_idx = header_idx + 1
    if sep_idx >= len(lines) or not is_separator_row(split_pipes(lines[sep_idx]) or []):
        # Some pandoc tables have header on a non-standard row; tolerate.
        sep_idx = header_idx
    header_lines = [lines[header_idx]]
    if sep_idx != header_idx:
        header_lines.append(lines[sep_idx])

    col_pref = index_for(header_cells, "preferred")
    col_acc = index_for(header_cells, "acceptable")
    col_forb = index_for(header_cells, "do not select")
    col_comm = index_for(header_cells, "comments")
    if any(c is None for c in (col_pref, col_acc, col_forb, col_comm)):
        raise ValueError(
            f"Matrix header missing one of the expected columns: "
            f"preferred={col_pref} acceptable={col_acc} do_not_select={col_forb} comments={col_comm}"
        )

    layers: list[dict] = []
    current: dict | None = None
    layer_seq = 0
    for i in range(sep_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() == "":
            continue
        if line.lstrip().startswith("#"):
            break  # left the table
        cells = split_pipes(line)
        if cells is None:
            break
        if is_separator_row(cells) or is_empty_row(cells):
            continue
        if is_layer_separator(cells):
            layer_seq += 1
            current = {
                "number": layer_seq,
                "title": strip_bold(cells[0]),
                "header_line": line,
                "component_lines": [],
                "components": [],
            }
            layers.append(current)
            continue
        # Component row
        if current is None:
            # Encountered a row before any layer separator. Create an
            # implicit "Unnamed Layer" so we don't drop content silently.
            layer_seq += 1
            current = {
                "number": layer_seq,
                "title": "Unnamed Layer",
                "header_line": "",
                "component_lines": [],
                "components": [],
            }
            layers.append(current)

        name = strip_bold(cells[0])
        if not name:
            continue
        component = {
            "id": f"{current['number']}.{len(current['components']) + 1}",
            "name": name,
            "preferred": parse_choice_cell(cells[col_pref] if col_pref is not None and col_pref < len(cells) else ""),
            "acceptable": parse_choice_cell(cells[col_acc] if col_acc is not None and col_acc < len(cells) else ""),
            "forbidden": parse_choice_cell(cells[col_forb] if col_forb is not None and col_forb < len(cells) else ""),
            "comments": parse_comments_cell(cells[col_comm] if col_comm is not None and col_comm < len(cells) else ""),
            "raw_row": line,
        }
        current["component_lines"].append(line)
        current["components"].append(component)

    return {
        "title": title,
        "version": version,
        "preamble_lines": preamble_lines,
        "header_lines": header_lines,
        "layers": layers,
        "out_of_scope": {
            "general": general,
            "selection_principles": selection_principles,
            "servers": servers,
        },
    }


def render_layer_md(layer: dict, preamble: list[str], header_lines: list[str], source_meta: dict) -> str:
    out: list[str] = []
    out.append(f"# TEHIK IT Profile layer {layer['number']}: {layer['title']}\n")
    out.append("> Generated by split_layers.py for a subagent. Contains only this layer's rows.\n")
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
    out.append(f"## Layer {layer['number']}: {layer['title']}\n")
    out.extend(header_lines)
    if layer.get("header_line"):
        out.append(layer["header_line"])
    out.extend(layer["component_lines"])
    out.append("")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("doc_path", type=pathlib.Path, help="Path to the IT profile markdown (output of fetch_it_profile.py)")
    p.add_argument("--out", type=pathlib.Path, required=True, help="Output directory")
    p.add_argument("--source-meta", type=pathlib.Path, help="Optional path to fetch_it_profile.py JSON output for provenance")
    args = p.parse_args()

    md_text = args.doc_path.read_text(encoding="utf-8")
    parsed = parse(md_text)

    if not parsed["layers"]:
        print("ERROR: parsed 0 layers - upstream document may have changed structure", file=sys.stderr)
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
        "title": parsed["title"],
        "version": parsed["version"],
        "layer_count": len(parsed["layers"]),
        "total_components": sum(len(layer["components"]) for layer in parsed["layers"]),
        "layers": [],
        "out_of_scope": parsed["out_of_scope"],
    }

    for layer in parsed["layers"]:
        slug = slugify(layer["title"])
        base = f"layer-{layer['number']:02d}-{slug}"
        md_path = args.out / f"{base}.md"
        json_path = args.out / f"{base}.json"

        md_path.write_text(render_layer_md(layer, parsed["preamble_lines"], parsed["header_lines"], source_meta), encoding="utf-8")
        json_path.write_text(
            json.dumps(
                {
                    "layer_number": layer["number"],
                    "layer_title": layer["title"],
                    "components": layer["components"],
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        manifest["layers"].append({
            "number": layer["number"],
            "title": layer["title"],
            "slug": slug,
            "md_path": str(md_path.resolve()),
            "json_path": str(json_path.resolve()),
            "component_count": len(layer["components"]),
            "component_ids": [c["id"] for c in layer["components"]],
        })

    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    json.dump(manifest, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
