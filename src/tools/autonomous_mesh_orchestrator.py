# src/tools/autonomous_mesh_orchestrator.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import ast
import sys
import subprocess
import threading
import json
from pathlib import Path
from datetime import datetime, timezone
import logging

from src.tools.self_healing_agent import heal_and_retry
from src.tools.telemetry_dashboard_generator import TelemetryDashboardGenerator

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("AUTONOMOUS_ORCHESTRATOR")

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

INTERNAL_MODULES = {
    "src", "mesh_governor", "psvc_containers", "psvc_reference", "vram_mesh",
    "base", "core", "agents", "tools", "mesh", "orchestrator", "pipelines",
    "nodes", "models", "automation", "calculating", "generated_agents", "kernel",
    "utils", "breath_engine"
}

IMPORT_EXCEPTIONS = {
    "cv2": "opencv-python-headless", "skimage": "scikit-image", "sklearn": "scikit-learn",
    "yaml": "pyyaml", "dateutil": "python-dateutil", "nacl": "pynacl",
    "dotenv": "python-dotenv", "bs4": "beautifulsoup4", "PIL": "Pillow"
}

CHECKPOINT_FILE = Path("data/wendy_orchestrator_checkpoint.json")

class LivenessHeartbeat:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._beat, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join(timeout=2.0)

    def _beat(self):
        while not self._stop_event.is_set():
            zulu_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            print(f"[{zulu_time}] ❤️ WENDY Liveness Heartbeat: Active computation in progress...", flush=True)
            self._stop_event.wait(60.0)

class CheckpointManager:
    @staticmethod
    def save(module_name: str):
        CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {"last_module": module_name, "timestamp": datetime.now(timezone.utc).isoformat()}
        with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load() -> str | None:
        if CHECKPOINT_FILE.exists():
            try:
                with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f).get("last_module")
            except Exception:
                return None
        return None

    @staticmethod
    def clear():
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()

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
                top_level = alias.name.split('.')[0]
                if top_level in STDLIB_MODULES or top_level in INTERNAL_MODULES: continue
                packages.add(IMPORT_EXCEPTIONS.get(top_level, top_level))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top_level = node.module.split('.')[0]
                if top_level in STDLIB_MODULES or top_level in INTERNAL_MODULES: continue
                packages.add(IMPORT_EXCEPTIONS.get(top_level, top_level))
    return packages

def discover_all_python_files() -> list:
    src_dir = Path("src")
    if not src_dir.exists(): return []
    
    files = []
    for file in src_dir.rglob("*.py"):
        if file.name == "__init__.py": continue
        
        module_path = str(file).replace('/', '.').replace('.py', '')
        
        # BULLETPROOF: Prevent infinite recursion by blocking the orchestrator and healer
        if "autonomous_mesh_orchestrator" in module_path or "self_healing_agent" in module_path or "cache_governor" in module_path:
            continue
            
        files.append({"file": file, "module": module_path})
    return files

def main():
    logger.info("🧠 WENDY Unbounded Autonomy Orchestrator Initializing...")
    heartbeat = LivenessHeartbeat()
    heartbeat.start()

    try:
        files = discover_all_python_files()
        logger.info(f"🔍 Discovered {len(files)} executable Python modules in src/.")
        if not files:
            logger.info("ℹ️ No modules found. Mesh is dormant.")
            return

        resume_module = CheckpointManager.load()
        if resume_module:
            logger.info(f"🔄 Resuming from checkpoint: {resume_module}")
            try:
                start_idx = next(i for i, item in enumerate(files) if item["module"] == resume_module)
                files = files[start_idx:]
            except StopIteration:
                CheckpointManager.clear()

        all_packages = set()
        for item in files:
            all_packages.update(get_required_packages(item["file"]))
            
        packages_list = sorted(list(all_packages))
        if packages_list:
            logger.info(f"📦 WENDY dynamically declared dependencies: {', '.join(packages_list)}")
            logger.info("⚡ Installing task-specific dependencies...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "-q"])
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages_list + ["-q"])

        for item in files:
            module_name = item['module']
            logger.info(f"\n🚀 Processing {module_name}...")
            CheckpointManager.save(module_name)
            
            success = heal_and_retry(module_name)
            if success:
                logger.info(f"✅ {module_name} completed successfully.")
            else:
                logger.error(f"❌ {module_name} failed and could not be autonomously healed.")
                
        CheckpointManager.clear()
        
        # Generate the Emperor's Visual Telemetry Dashboard
        logger.info("📊 Generating WENDY Telemetry Dashboard for Emperor visibility...")
        TelemetryDashboardGenerator().generate()
        
        logger.info("\n🏁 WENDY Unbounded Autonomy Execution Cycle Complete.")
    finally:
        heartbeat.stop()

if __name__ == "__main__":
    main()
