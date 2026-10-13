# src/tools/universal_mesh_executor.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import ast
import sys
import subprocess
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

def resolve_dependencies(file_path: str) -> list:
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=file_path)
        
    required_packages = {"numpy>=2.1.0", "pyyaml>=6.0.2"} # Baseline
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                pkg = IMPORT_TO_PACKAGE.get(alias.name.split('.')[0])
                if pkg: required_packages.add(pkg)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                pkg = IMPORT_TO_PACKAGE.get(node.module.split('.')[0])
                if pkg: required_packages.add(pkg)
                
    return sorted(list(required_packages))

def execute_agent(agent_module: str, file_path: str):
    print(f"🧠 WENDY Autonomous Execution: {agent_module}")
    
    # 1. Resolve dependencies autonomously
    packages = resolve_dependencies(file_path)
    print(f"📦 Declared minimal dependencies: {', '.join(packages)}")
    
    # 2. Install dynamically (Zero Bloat)
    print("⚡ Installing task-specific dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
    
    # 3. Execute the agent
    print(f"🚀 Executing {agent_module}...")
    subprocess.check_call([sys.executable, "-m", agent_module])
    print("✅ Execution complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WENDY Universal Mesh Executor")
    parser.add_argument("--agent", required=True, help="Module path (e.g., src.agents.lidar_agent)")
    parser.add_argument("--file", required=True, help="Source file path (e.g., src/agents/lidar_agent.py)")
    args = parser.parse_args()
    
    execute_agent(args.agent, args.file)
