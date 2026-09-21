# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
import os
import re
import json
from datetime import datetime

print("=== PSIVI OMNI-STAMPER: ENFORCING UNIFORMITY ===")

IGNORE_DIRS = {'.git', 'archive', 'node_modules', '__pycache__', 'dist', '.github', 'maps', 'reports'}
DATA_EXTS = {'.csv', '.json', '.geojson'} 

AUTHOR = "Louis-Philippe Audette | PSIVI.COM"
YEAR = "2026"
CODE_LIC = "EUPL 1.2"
DOC_LIC = "CC BY-SA 4.0"

GO_STAMP = f"// Copyright (c) {YEAR} {AUTHOR}\n// Licensed under {CODE_LIC} | https://psivi.com\n\n"
HASH_STAMP = f"# Copyright (c) {YEAR} {AUTHOR} | {CODE_LIC}\n"
HTML_STAMP = f"<!--\n  Copyright (c) {YEAR} {AUTHOR}\n  Code: {CODE_LIC} | Docs: {DOC_LIC} | Hardware: Proprietary (w-1-n.com)\n-->\n"
MD_STAMP = f"<!--\n  Copyright (c) {YEAR} {AUTHOR} | {DOC_LIC}\n-->\n"

data_manifest = []
stamped_list = []
data_list = []

def stamp_code_doc(filepath, ext):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False

    if f"Copyright (c) {YEAR}" in content:
        return False

    if ext == '.go':
        new_content = GO_STAMP + content
    elif ext in ['.py', '.yml', '.yaml', '.sh']:
        if content.startswith("#!"):
            lines = content.split('\n', 1)
            new_content = lines[0] + '\n' + HASH_STAMP + lines[1]
        else:
            new_content = HASH_STAMP + content
    elif ext == '.html':
        match = re.search(r'(?i)(<!DOCTYPE[^>]*>)', content)
        if match:
            idx = match.end()
            new_content = content[:idx] + '\n' + HTML_STAMP + content[idx:]
        else:
            new_content = HTML_STAMP + content
    elif ext in ['.md', '.txt']:
        new_content = MD_STAMP + content
    else:
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

scanned = 0

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
    
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        filepath = os.path.join(root, file)
        
        if ext in {'.png', '.jpg', '.svg', '.woff2', '.ico', '.pdf'}:
            continue

        scanned += 1

        if ext in DATA_EXTS:
            clean_path = filepath.replace('./', '')
            data_manifest.append({
                "path": clean_path,
                "license": DOC_LIC,
                "author": AUTHOR,
                "year": YEAR
            })
            data_list.append(clean_path)
            continue

        if ext in {'.go', '.py', '.yml', '.yaml', '.sh', '.html', '.md', '.txt'}:
            if stamp_code_doc(filepath, ext):
                stamped_list.append(filepath)
                print(f"[STAMPED] {filepath}")

# 1. Write the FAIR Data Manifest
with open('DATA_LICENSE_MANIFEST.json', 'w', encoding='utf-8') as f:
    json.dump(data_manifest, f, indent=2)

# 2. Generate the Permanent Audit Report
os.makedirs('reports', exist_ok=True)
audit_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

with open('reports/license_audit.md', 'w', encoding='utf-8') as f:
    f.write("# License Uniformity Audit Report\n\n")
    f.write(f"**Audit Time:** {audit_time}\n")
    f.write(f"**Agent:** PSIVI Omni-Stamper\n\n")
    
    f.write("## Summary\n")
    f.write(f"- **Total Files Scanned:** {scanned}\n")
    f.write(f"- **Code/Docs Stamped:** {len(stamped_list)}\n")
    f.write(f"- **Data Files Cataloged:** {len(data_list)}\n\n")
    
    if stamped_list:
        f.write("## Files Stamped (EUPL 1.2 / CC BY-SA 4.0)\n")
        for item in stamped_list:
            f.write(f"- `{item}`\n")
        f.write("\n")
        
    if data_list:
        f.write("## Data Files Added to Manifest (CC BY-SA 4.0)\n")
        for item in data_list:
            f.write(f"- `{item}`\n")

print(f"\n[MANIFEST] Generated DATA_LICENSE_MANIFEST.json for {len(data_list)} data files.")
print(f"[AUDIT] Generated reports/license_audit.md")
print(f"[COMPLETE] Scanned {scanned} files. Stamped {len(stamped_list)} code/doc files.")
