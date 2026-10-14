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

# BULLETPROOF: Hardcoded standard library modules + dynamic fallback
STDLIB_MODULES = {
    "ast", "asyncio", "collections", "ctypes", "dataclasses", "datetime",
    "enum", "functools", "getpass", "hashlib", "importlib", "json", "logging",
    "math", "os", "pathlib", "random", "re", "shutil", "socket", "statistics",
    "struct", "subprocess", "sys", "tempfile", "threading", "time", "traceback",
    "typing", "urllib", "uuid", "websockets", "copy", "itertools", "string",
    "warnings", "io", "builtins", "errno", "gc", "inspect", "operator"
}

try:
    STDLIB_MODULES.update(sys.stdlib_module_names)
except AttributeError:
    pass

# Internal project namespaces that should NEVER be pip installed
INTERNAL_MODULES = {
    "src", "mesh_governor", "psvc_containers", "psvc_reference", "vram_mesh",
    "base", "core", "agents", "tools", "mesh", "orchestrator", "pipelines",
    "nodes", "models", "automation", "calculating", "generated_agents", "kernel",
    "utils", "breath_engine"
}

# Known exceptions where import name != pip package name
IMPORT_EXCEPTIONS = {
    "cv2": "opencv-python-headless", "skimage": "scikit-image", "sklearn": "scikit-learn",
    "yaml": "pyyaml", "dateutil": "python-dateutil", "nacl": "pynacl",
    "dotenv": "python-dotenv", "bs4": "beautifulsoup4", "PIL": "Pillow"
}

# SURGICAL FIX: Prevent infinite recursion (Exit Code 143) by excluding top-level entry points.
# NOTE: This DOES NOT skip ZIG healing. zig_compiler_healer.py and all other modules remain fully active.
SKIP_FILES = {
    "autonomous_mesh_orchestrator.py",
    "self_healing_agent.py"
}

def get_required_packages(file_path: Path) -> set:
    if not file_path.exists(): 
        return set()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
        except SyntaxError:
            return set()
            
    packages = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_level = alias.name.split('.')[0]
                if top_level in STDLIB_MODULES or top_level in INTERNAL_MODULES:
                    continue
                pkg = IMPORT_EXCEPTIONS.get(top_level, top_level)
                packages.add(pkg)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top_level = node.module.split('.')[0]
                if top_level in STDLIB_MODULES or top_level in INTERNAL_MODULES:
                    continue
                pkg = IMPORT_EXCEPTIONS.get(top_level, top_level)
                packages.add(pkg)
    return packages

def discover_all_python_files() -> list:
    src_dir = Path("src")
    if not src_dir.exists(): 
        return []
        
    files = []
    for file in src_dir.rglob("*.py"):
        if file.name == "__init__.py": 
            continue
        # SURGICAL FIX: Skip top-level entry points to prevent infinite recursion hangs
        if file.name in SKIP_FILES: 
            continue
            
        module_path = str(file).replace('/', '.').replace('.py', '')
        files.append({"file": file, "module": module_path})
    return files

def main():
    logger.info("🧠 WENDY Unbounded Autonomy Orchestrator Initializing...")
    files = discover_all_python_files()
    logger.info(f"🔍 Discovered {len(files)} executable Python modules in src/.")
    
    if not files:
        logger.info("ℹ️ No modules found. Mesh is dormant.")
        return

    all_packages = set()
    for item in files:
        all_packages.update(get_required_packages(item["file"]))
        
    packages_list = sorted(list(all_packages))
    logger.info(f"📦 WENDY dynamically declared dependencies: {', '.join(packages_list)}")
    
    logger.info("⚡ Installing task-specific dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "-q"])
    if packages_list:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages_list + ["-q"])

    # NOTE: ZIG compilation/healing is handled by zig_compiler_healer.py, which remains fully active.
    for item in files:
        logger.info(f"\n🚀 Processing {item['module']}...")
        success = heal_and_retry(item["module"])
        if success:
            logger.info(f"✅ {item['module']} completed successfully.")
        else:
            logger.error(f"❌ {item['module']} failed and could not be autonomously healed.")
            
    logger.info("\n🏁 WENDY Unbounded Autonomy Execution Cycle Complete.")

if __name__ == "__main__":
    main()
