# src/tools/dependency_resolver.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import ast
import sys
import argparse
from pathlib import Path

# WENDY's internal mapping of Python imports to minimal pip packages
IMPORT_TO_PACKAGE = {
    "numpy": "numpy>=2.1.0",
    "scipy": "scipy>=1.14.0",
    "cv2": "opencv-python-headless>=4.10.0.84",
    "skimage": "scikit-image>=0.24.0",
    "sklearn": "scikit-learn>=1.5.1",
    "pandas": "pandas>=2.2.2",
    "matplotlib": "matplotlib>=3.9.2",
    "seaborn": "seaborn>=0.13.2",
    "torch": "torch>=2.5.0",
    "transformers": "transformers>=4.44.0",
    "yaml": "pyyaml>=6.0.2",
    "requests": "requests>=2.32.3",
    "dateutil": "python-dateutil>=2.9.0.post0",
    "nacl": "pynacl>=1.5.0",
    "loguru": "loguru>=0.7.2",
    "dotenv": "python-dotenv>=1.0.1",
}

def analyze_file(file_path: str) -> list:
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=file_path)
        
    required_packages = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                pkg = IMPORT_TO_PACKAGE.get(alias.name.split('.')[0])
                if pkg: required_packages.add(pkg)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                pkg = IMPORT_TO_PACKAGE.get(node.module.split('.')[0])
                if pkg: required_packages.add(pkg)
                
    # Always include baseline core requirements for WENDY agents
    required_packages.add("numpy>=2.1.0")
    required_packages.add("pyyaml>=6.0.2")
    
    return sorted(list(required_packages))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WENDY Autonomous Dependency Resolver")
    parser.add_argument("--file", required=True, help="Path to the Python source file to analyze")
    args = parser.parse_args()
    
    packages = analyze_file(args.file)
    
    print(f"# WENDY Autonomous Analysis: Analyzed {args.file}")
    print(f"# Declared minimal dependencies based on source code imports:")
    for pkg in packages:
        print(f"#   - {pkg}")
        
    # Output the exact pip install command for GitHub Actions to consume
    print(f"pip install {' '.join(packages)}")
