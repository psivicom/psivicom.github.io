#!/usr/bin/env python3
"""
tools/fix_timestamps.py
PSIVI.COM NASA Open Science Timestamp Fix Kit
Rewrites Last updated: lines to RFC3339 Zulu + adds frontmatter created/updated

Usage: python tools/fix_timestamps.py
"""

import re
from pathlib import Path
from datetime import datetime, timezone
import sys

ROOT = Path(__file__).parent.parent
PATTERN_BARE_DATE = re.compile(r'(Last updated:\s*)(\d{4}-\d{2}-\d{2})(?!T)')
PATTERN_ISO_NO_Z = re.compile(r'(Last updated:\s*)(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?![.Z])')
PATTERN_CREATED = re.compile(r'^created:\s*.*$', re.MULTILINE)
PATTERN_UPDATED = re.compile(r'^updated:\s*.*$', re.MULTILINE)

NOW_Z = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
NOW_DATE_Z = datetime.now(timezone.utc).strftime('%Y-%m-%dT00:00:00Z')

def fix_file(path: Path) -> bool:
    text = path.read_text(encoding='utf-8', errors='ignore')
    orig = text
    changed = False

    # 1. Fix Last updated: YYYY-MM-DD -> YYYY-MM-DDTHH:MM:SSZ
    def repl_bare(m):
        date = m.group(2)
        return f"{m.group(1)}{date}T00:00:00Z"

    new_text, n1 = PATTERN_BARE_DATE.subn(repl_bare, text)
    if n1:
        print(f"  Fixed {n1} bare date(s) in {path}")
        text = new_text
        changed = True

    def repl_no_z(m):
        iso = m.group(2)
        return f"{m.group(1)}{iso}Z"

    new_text, n2 = PATTERN_ISO_NO_Z.subn(repl_no_z, text)
    if n2:
        print(f"  Fixed {n2} non-Z dates(s) in {path}")
        text = new_text
        changed = True

    # 2. Add frontmatter if markdown and has ---
    if path.suffix == '.md' and text.startswith('---'):
        # Check for created/updated inside first frontmatter block
        end = text.find('\n---', 3)
        if end != -1:
            fm = text[:end]
            rest = text[end:]
            if 'created:' not in fm:
                fm = fm.replace('---\n', f'---\ncreated: {NOW_DATE_Z}\n', 1)
                changed = True
            if 'updated:' not in fm:
                fm += f"\nupdated: {NOW_Z}"
                changed = True
            else:
                # update updated field
                new_fm, n = PATTERN_UPDATED.subn(f'updated: {NOW_Z}', fm)
                if n:
                    fm = new_fm
                    changed = True
            text = fm + rest
    elif path.suffix == '.md' and not text.startswith('---'):
        # Prepend minimal frontmatter if missing and file is not README
        if path.name not in ('README.md', 'teamai.md', 'CHANGELOG.md'):
            front = f"---\ncreated: {NOW_DATE_Z}\nupdated: {NOW_Z}\nauthor: lpaudette\n---\n\n"
            text = front + text
            changed = True

    if changed and text != orig:
        path.write_text(text, encoding='utf-8')
        return True
    return False

def main():
    print(f"[{NOW_Z}] PSIVI NASA Timestamp Fix Kit running...")
    targets = list(ROOT.rglob('*.md')) + list(ROOT.rglob('*.f')) + list(ROOT.rglob('*.forth'))
    fixed = 0
    for p in targets:
        if '.git' in str(p):
            continue
        if p.is_file():
            if fix_file(p):
                fixed += 1

    # Explicitly check README
    readme = ROOT / 'README.md'
    if readme.exists():
        content = readme.read_text(encoding='utf-8', errors='ignore')
        if 'Last updated: 2026-05-11' in content and 'Last updated: 2026-05-11T00:00:00Z' not in content:
            print(f"  [!] README.md still has bare date - fixing now")
            fix_file(readme)
            fixed += 1

    print(f"Done. Fixed {fixed} files.")
    print(f"Next: git commit -m '{NOW_Z} - fix - NASA timestamp compliance'")

if __name__ == '__main__':
    main()
