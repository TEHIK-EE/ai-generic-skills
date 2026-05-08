#!/usr/bin/env python3
"""
Fetch the TEHIK NFR document, with cache + bundled-snapshot fallback.

Resolution order:
  1. If --refresh OR cache is missing/older than --max-age-hours: try live download.
  2. Otherwise use the cached copy at ~/.cache/tehik-nfrs/nfrs.md.
  3. If both fail, fall back to the snapshot bundled at references/nfr-source.md.

Prints a single JSON object to stdout describing what was loaded so the
orchestrator can record provenance in the audit report:

  {
    "path": "/abs/path/to/nfrs.md",
    "url": "https://raw.githubusercontent.com/...",
    "source": "live" | "cached" | "bundled",
    "fetched_at": "2026-05-08T10:23:14Z",
    "sha256": "abcd...",
    "size_bytes": 12345,
    "fallback_reason": null | "..."
  }

Exits non-zero only if even the bundled fallback is unreadable.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

UPSTREAM_URL = (
    "https://raw.githubusercontent.com/TEHIK-EE/mitte-funktsionaalsed-nouded/"
    "refs/heads/main/mittefunktsionaalsed-nouded.en.md"
)
DEFAULT_CACHE_DIR = pathlib.Path(
    os.environ.get("TEHIK_NFR_CACHE_DIR")
    or pathlib.Path.home() / ".cache" / "tehik-nfrs"
)
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
BUNDLED_SNAPSHOT = SCRIPT_DIR.parent / "references" / "nfr-source.md"


def sha256_of(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cache_age_hours(cache_file: pathlib.Path) -> float | None:
    if not cache_file.exists():
        return None
    mtime = dt.datetime.fromtimestamp(cache_file.stat().st_mtime, dt.timezone.utc)
    return (dt.datetime.now(dt.timezone.utc) - mtime).total_seconds() / 3600


def try_download(url: str, dest: pathlib.Path, timeout_s: int) -> tuple[bool, str | None]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "tehik-standards-validation/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = resp.read()
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(dest)
        return True, None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, f"{type(e).__name__}: {e}"


def emit(payload: dict) -> None:
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cache-dir", type=pathlib.Path, default=DEFAULT_CACHE_DIR)
    p.add_argument("--refresh", action="store_true", help="Force live download, ignore cache age")
    p.add_argument("--offline", action="store_true", help="Never attempt live download")
    p.add_argument("--max-age-hours", type=float, default=24.0, help="Use cache if younger than this; otherwise try live")
    p.add_argument("--timeout", type=int, default=15, help="HTTP timeout seconds")
    p.add_argument("--url", default=UPSTREAM_URL)
    args = p.parse_args()

    cache_file = args.cache_dir / "nfrs.md"
    age = cache_age_hours(cache_file)
    cache_is_fresh = age is not None and age <= args.max_age_hours

    fallback_reason: str | None = None
    source: str | None = None
    chosen: pathlib.Path | None = None

    should_try_live = not args.offline and (args.refresh or not cache_is_fresh)
    if should_try_live:
        ok, err = try_download(args.url, cache_file, args.timeout)
        if ok:
            source, chosen = "live", cache_file
        else:
            fallback_reason = f"live download failed ({err})"

    if chosen is None and cache_file.exists():
        source, chosen = "cached", cache_file
        if fallback_reason is None and args.offline:
            fallback_reason = "offline mode requested"

    if chosen is None and BUNDLED_SNAPSHOT.exists():
        source, chosen = "bundled", BUNDLED_SNAPSHOT
        if fallback_reason is None:
            fallback_reason = "no cache available; using bundled snapshot"

    if chosen is None:
        emit({
            "error": "no NFR source available (live download failed, no cache, no bundled snapshot)",
            "url": args.url,
        })
        return 2

    emit({
        "path": str(chosen.resolve()),
        "url": args.url,
        "source": source,
        "fetched_at": utc_now_iso(),
        "sha256": sha256_of(chosen),
        "size_bytes": chosen.stat().st_size,
        "fallback_reason": fallback_reason,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
