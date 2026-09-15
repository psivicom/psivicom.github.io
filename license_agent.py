import os
import re
import json

print("=== PSIVI OMNI-STAMPER: ENFORCING UNIFORMITY ===")

IGNORE_DIRS = {'.git', 'archive', 'node_modules', '__pycache__', 'dist', '.github', 'maps', 'reports'}
DATA_EXTS = {'.csv', '.json', '.geojson'} 

AUTHOR = "Louis-Philippe Audette | PSIVI.COM"
YEAR = "2026"
CODE_LIC = "EUPL 1.2"
DOC_LIC = "CC BY-SA 4.0"

# 1. Go (Idiomatic //)
GO_STAMP = f"// Copyright (c) {YEAR} {AUTHOR}\n// Licensed under {CODE_LIC} | https://psivi.com\n\n"

# 2. Python/YAML/Shell (Idiomatic #)
HASH_STAMP = f"# Copyright (c) {YEAR} {AUTHOR} | {CODE_LIC}\n"

# 3. HTML
HTML_STAMP = f"<!--\n  Copyright (c) {YEAR} {AUTHOR}\n  Code: {CODE_LIC} | Docs: {DOC_LIC} | Hardware: Proprietary (w-1-n.com)\n-->\n"

# 4. Markdown / Text
MD_STAMP = f"<!--\n  Copyright (c) {YEAR} {AUTHOR} | {DOC_LIC}\n-->\n"

data_manifest = []

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

stamped = 0
scanned = 0

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
    
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        filepath = os.path.join(root, file)
        
        if ext in {'.png', '.jpg', '.svg', '.woff2', '.ico', '.pdf'}:
            continue

        scanned += 1

        # Protect Data Files (CSV/JSON) - Add to Manifest instead
        if ext in DATA_EXTS:
            data_manifest.append({
                "path": filepath.replace('./', ''),
                "license": DOC_LIC,
                "author": AUTHOR,
                "year": YEAR
            })
            continue

        # Stamp Code and Documents
        if ext in {'.go', '.py', '.yml', '.yaml', '.sh', '.html', '.md', '.txt'}:
            if stamp_code_doc(filepath, ext):
                stamped += 1
                print(f"[STAMPED] {filepath}")

# Write the FAIR Data Manifest for CSVs and JSONs
with open('DATA_LICENSE_MANIFEST.json', 'w', encoding='utf-8') as f:
    json.dump(data_manifest, f, indent=2)
    
print(f"\n[MANIFEST] Generated DATA_LICENSE_MANIFEST.json for {len(data_manifest)} data files.")
print(f"[COMPLETE] Scanned {scanned} files. Stamped {stamped} code/doc files.")
