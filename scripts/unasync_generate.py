#!/usr/bin/env python3
"""Generate intra42._sync from intra42._async via unasync.

Usage:
    uv run python scripts/unasync_generate.py            # regenerate in place
    uv run python scripts/unasync_generate.py --check    # fail if regenerating would change anything
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
import tempfile
from pathlib import Path

import unasync

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "intra42"
ASYNC_DIR = SRC / "_async"
SYNC_DIR = SRC / "_sync"

GENERATED_HEADER = (
    '"""GENERATED FILE — DO NOT EDIT BY HAND.\n\n'
    "Generated from the corresponding module under intra42._async by\n"
    "scripts/unasync_generate.py (via the `unasync` library). Edit the async\n"
    "source and re-run that script instead.\n"
    '"""\n\n'
)

RULE = unasync.Rule(
    fromdir=str(ASYNC_DIR),
    todir=str(SYNC_DIR),
    additional_replacements={
        "AsyncClient": "Client",
        "AsyncResource": "Resource",
        "AsyncUsersResource": "UsersResource",
        "AsyncCampusesResource": "CampusesResource",
        "AsyncQuerySet": "QuerySet",
        "aensure_token": "ensure_token",
        "aacquire": "acquire",
        "aclose": "close",
        "__aenter__": "__enter__",
        "__aexit__": "__exit__",
        "__aiter__": "__iter__",
        "__anext__": "__next__",
    },
)


def _find_async_files() -> list[str]:
    return [str(p) for p in ASYNC_DIR.rglob("*.py")]


def _prepend_header(path: Path) -> None:
    text = path.read_text()
    if not text.startswith('"""GENERATED FILE'):
        path.write_text(GENERATED_HEADER + text)


def generate() -> None:
    unasync.unasync_files(_find_async_files(), [RULE])
    for path in SYNC_DIR.rglob("*.py"):
        if path.name == "__init__.py" and path.stat().st_size == 0:
            continue
        _prepend_header(path)


def check() -> bool:
    """Regenerate into a temp dir and diff against the committed _sync/."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_sync = Path(tmp) / "_sync"
        rule = unasync.Rule(
            fromdir=str(ASYNC_DIR),
            todir=str(tmp_sync),
            additional_replacements=RULE.additional_replacements,
        )
        unasync.unasync_files(_find_async_files(), [rule])
        for path in tmp_sync.rglob("*.py"):
            if path.name == "__init__.py" and path.stat().st_size == 0:
                continue
            _prepend_header(path)

        comparison = filecmp.dircmp(str(tmp_sync), str(SYNC_DIR))
        diffs = _collect_diffs(comparison)
        if diffs:
            print("intra42._sync is out of date with intra42._async:", file=sys.stderr)
            for d in diffs:
                print(f"  {d}", file=sys.stderr)
            print("Run: uv run python scripts/unasync_generate.py", file=sys.stderr)
            return False
        return True


def _collect_diffs(comparison: filecmp.dircmp, prefix: str = "") -> list[str]:
    diffs = []
    for name in comparison.diff_files + comparison.left_only + comparison.right_only:
        diffs.append(f"{prefix}{name}")
    for sub_dir, sub_comparison in comparison.subdirs.items():
        diffs.extend(_collect_diffs(sub_comparison, prefix=f"{prefix}{sub_dir}/"))
    return diffs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        return 0 if check() else 1

    if SYNC_DIR.exists():
        shutil.rmtree(SYNC_DIR)
    generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
