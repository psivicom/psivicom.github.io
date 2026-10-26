#!/usr/bin/env python3
"""
WENDY Goldstream Beekeeping Research - Dependency Updater
Queries PyPI to update all requirements*.txt files to the latest stable versions.
Zero external dependencies (uses standard library urllib and pathlib).
"""
import sys
import json
import urllib.request
import urllib.error
import re
from pathlib import Path

def get_latest_version(package_name: str) -> str:
    """Fetches the latest stable version from PyPI."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WENDY-Updater/1.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data['info']['version']
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError, TimeoutError) as e:
        print(f"Warning: Could not fetch latest version for {package_name}: {e}")
        return None

def update_single_file(file_path: Path) -> bool:
    """Parses and updates a single requirements file in place."""
    if not file_path.exists():
        print(f"Error: {file_path} not found.")
        return False

    updated_lines = []
    # Matches standard package names (PEP 508 simplified)
    pkg_pattern = re.compile(r'^([A-Za-z0-9_.-]+)\s*(.*)$')

    with file_path.open('r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.strip()
        
        # Preserve empty lines, full-line comments, and pip flags
        if not stripped or stripped.startswith('#') or stripped.startswith('-'):
            updated_lines.append(line)
            continue
        
        # Ignore VCS links, local paths, or complex extras for safety
        if '://' in stripped or stripped.startswith('.') or stripped.startswith('/'):
            updated_lines.append(line)
            continue

        # Handle inline comments
        inline_comment = ""
        if '#' in stripped:
            parts = stripped.split('#', 1)
            stripped = parts[0].strip()
            inline_comment = f"  # {parts[1].strip()}"

        match = pkg_pattern.match(stripped)
        if not match:
            updated_lines.append(line)
            continue

        pkg_name = match.group(1)
        latest = get_latest_version(pkg_name)
        
        if latest:
            new_line = f"{pkg_name}=={latest}{inline_comment}\n"
            updated_lines.append(new_line)
            print(f"  Updated {pkg_name} to {latest}")
        else:
            updated_lines.append(line)

    with file_path.open('w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    return True

def main():
    """Main execution loop handling multiple files or auto-discovery."""
    if len(sys.argv) > 1:
        # Process explicitly passed file paths
        target_files = [Path(f) for f in sys.argv[1:]]
    else:
        # Auto-discover all requirements*.txt files in the root directory
        target_files = list(Path('.').glob('requirements*.txt'))
        if not target_files:
            print("No requirements*.txt files found in the root directory.")
            sys.exit(0)

    print(f"Discovered {len(target_files)} requirement file(s) to process.")
    
    for file_path in target_files:
        print(f"\nProcessing: {file_path}")
        if update_single_file(file_path):
            print(f"Successfully updated {file_path}")

if __name__ == "__main__":
    main()
