#!/usr/bin/env python3
"""
Normalize archive filenames by stripping leading whitespace from names under archive/.
Examples:
  archive/2026-09-16/ A_forage_agent.py -> archive/2026-09-16/A_forage_agent.py
"""

from pathlib import Path
import os
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = REPO_ROOT / "archive"

def normalize_entry(path: Path):
    original = path
    stripped = path.name.lstrip()
    if stripped == path.name:
        return None

    new_path = path.with_name(stripped)
    if new_path.exists():
        raise FileExistsError(f"Destination already exists: {new_path}")

    path.rename(new_path)
    print(f"RENAMED: {original} -> {new_path}")
    return (original, new_path)

def collect_entries(root: Path):
    entries = []
    for p in root.rglob("*"):
        if p.name and p.name[:1].isspace():
            entries.append(p)
    # process deeper items first so nested directories are renamed after their children
    return sorted(entries, key=lambda p: (len(p.parts), p.as_posix()), reverse=True)

def main():
    if not ARCHIVE_ROOT.exists():
        print(f"No archive directory found at: {ARCHIVE_ROOT}")
        return 0

    changed = []
    for entry in collect_entries(ARCHIVE_ROOT):
        try:
            result = normalize_entry(entry)
            if result:
                changed.append(result)
        except Exception as exc:
            print(f"ERROR: {entry}: {exc}", file=sys.stderr)
            return 1

    if not changed:
        print("No archive filenames needed normalization.")
        return 0

    print(f"\nNormalized {len(changed)} entries under archive/.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
