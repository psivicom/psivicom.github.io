# src/tools/autonomous_mesh_orchestrator.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import ast
import sys
import subprocess
from pathlib import Path
import logging
from src.tools.self_healing_agent import heal_and_retry

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("AUTONOMOUS_ORCHESTRATOR")

IMPORT_TO_PACKAGE = {
    "numpy": "numpy>=2.1.0", "scipy": "scipy>=1.14.0", "cv2": "opencv-python-headless>=4.10.0.84",
    "skimage": "scikit-image>=0.24.0", "sklearn": "scikit-learn>=1.5.1", "pandas": "pandas>=2.2.2",
    "matplotlib": "matplotlib>=3.9.2", "seaborn": "seaborn>=0.13.2", "torch": "torch>=2.5.0",
    "transformers": "transformers>=4.44.0", "yaml": "pyyaml>=6.0.2", "requests": "requests>=2.32.3",
    "dateutil": "python-dateutil>=2.9.0.post0", "nacl": "pynacl>=1.5.0", "loguru": "loguru>=0.7.2",
    "dotenv": "python-dotenv>=1.0.1",
}

def get_required_packages(file_path: Path) -> set:
    if not file_path.exists(): return set()
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
        except SyntaxError:
            return set()
    packages = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                pkg = IMPORT_TO_PACKAGE.get(alias.name.split('.')[0])
                if pkg: packages.add(pkg)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                pkg = IMPORT_TO_PACKAGE.get(node.module.split('.')[0])
                if pkg: packages.add(pkg)
    return packages

def discover_agents() -> list:
    agents_dir = Path("src/agents")
    if not agents_dir.exists(): return []
    agents = []
    for file in agents_dir.glob("*_agent.py"):
        if file.name == "__init__.py": continue
        module_path = str(file).replace('/', '.').replace('.py', '')
        agents.append({"file": file, "module": module_path})
    return agents

def main():
    logger.info("🧠 WENDY Autonomous Mesh Orchestrator Initializing...")
    agents = discover_agents()
    logger.info(f"🔍 Discovered {len(agents)} agents in the mesh.")
    
    if not agents:
        logger.info("ℹ️ No agents found. Mesh is dormant.")
        return

    all_packages = {"numpy>=2.1.0", "pyyaml>=6.0.2"}
    for agent in agents:
        all_packages.update(get_required_packages(agent["file"]))
        
    packages_list = sorted(list(all_packages))
    logger.info(f"📦 WENDY declared minimal dependencies: {', '.join(packages_list)}")
    
    logger.info("⚡ Installing task-specific dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "-q"])
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages_list + ["-q"])
    
    for agent in agents:
        logger.info(f"\n🚀 Processing {agent['module']}...")
        success = heal_and_retry(agent["module"])
        if success:
            logger.info(f"✅ {agent['module']} completed successfully.")
        else:
            logger.error(f"❌ {agent['module']} failed and could not be autonomously healed.")

    logger.info("\n🏁 WENDY Autonomous Mesh Execution Cycle Complete.")

if __name__ == "__main__":
    main()
