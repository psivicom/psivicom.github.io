# src/tools/self_healing_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import ast
import re
import subprocess
import sys
from pathlib import Path
import logging

logger = logging.getLogger("SELF_HEALING_AGENT")
TYPING_IMPORTS = {"List", "Dict", "Optional", "Tuple", "Any", "Union", "Set"}

class SelfHealingAgent:
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent

    def analyze_and_heal(self, module_name: str, error_output: str) -> bool:
        # 1. Check for Missing Module
        module_match = re.search(r"No module named ['\"](\w+)['\"]", error_output)
        if module_match:
            missing_module = module_match.group(1)
            logger.info(f"🔍 Diagnosing: Missing module '{missing_module}'. Attempting dynamic install...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", missing_module, "-q"])
                logger.info(f"✅ Dynamically installed '{missing_module}'.")
                return True
            except subprocess.CalledProcessError:
                logger.warning(f"⚠️ Failed to dynamically install '{missing_module}'.")
                return False

        # 2. Check for NameError (Missing typing imports)
        name_error_match = re.search(r"NameError: name '(\w+)' is not defined", error_output)
        if name_error_match:
            missing_name = name_error_match.group(1)
            if missing_name in TYPING_IMPORTS:
                logger.info(f"🔍 Diagnosing: Missing typing import '{missing_name}'. Attempting auto-import...")
                # CRITICAL FIX: Find all .py files in traceback and take the LAST one
                file_matches = re.findall(r'File "([^"]+\.py)", line (\d+)', error_output)
                if file_matches:
                    error_file = Path(file_matches[-1][0])
                    if self._inject_typing_import(error_file):
                        return True

        # 3. Check for Keyword Mismatch (TypeError)
        kwarg_match = re.search(r"unexpected keyword argument '(\w+)'", error_output)
        file_matches_kwarg = re.findall(r'File "([^"]+\.py)", line (\d+)', error_output)
        
        if not kwarg_match or not file_matches_kwarg:
            logger.warning("⚠️ Error not recognized as auto-healable. Cannot auto-heal.")
            return False

        bad_kwarg = kwarg_match.group(1)
        error_file = Path(file_matches_kwarg[-1][0])
        error_line = int(file_matches_kwarg[-1][1])

        logger.info(f"🔍 Diagnosing: Unexpected kwarg '{bad_kwarg}' in {error_file.name}:{error_line}")

        try:
            with open(error_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.warning(f"⚠️ File not found: {error_file}")
            return False
            
        target_line = lines[error_line - 1]
        func_match = re.search(r'(\w+)\.(\w+)\s*\(', target_line)
        
        if not func_match:
            logger.warning("⚠️ Could not parse function call on target line.")
            return False

        func_name = func_match.group(2)
        actual_file, actual_sig = None, None
        
        for py_file in self.root.rglob("*.py"):
            if py_file.name == "__init__.py": continue
            try:
                content = py_file.read_text(encoding='utf-8')
                sig_match = re.search(rf"def {func_name}\s*\(([^)]+)\)", content)
                if sig_match:
                    actual_file = py_file
                    actual_sig = sig_match.group(1)
                    break
            except Exception:
                continue

        if not actual_file:
            logger.warning(f"⚠️ Could not find definition of '{func_name}'.")
            return False

        params = [p.split(':')[0].split('=')[0].strip() for p in actual_sig.split(',')]
        valid_kwargs = [p for p in params if p != 'self' and not p.startswith('*')]
        correct_kwarg = 'data' if 'data' in valid_kwargs else (valid_kwargs[-1] if valid_kwargs else None)
            
        if not correct_kwarg or correct_kwarg == bad_kwarg:
            logger.warning("⚠️ Could not determine correct keyword argument.")
            return False

        logger.info(f"💡 Hypothesis: Replace '{bad_kwarg}' with '{correct_kwarg}'")
        new_line = target_line.replace(f"{bad_kwarg}=", f"{correct_kwarg}=")
        
        if new_line == target_line:
            return False

        lines[error_line - 1] = new_line
        with open(error_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        logger.info(f"✅ Applied autonomous patch to {error_file.name}:{error_line}")
        return True

    def _inject_typing_import(self, file_path: Path) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            typing_line_idx = -1
            for i, line in enumerate(lines):
                if "from typing import" in line:
                    typing_line_idx = i
                    break
            
            required = ["List", "Dict", "Optional", "Tuple", "Any", "Union"]
            
            if typing_line_idx != -1:
                line = lines[typing_line_idx]
                existing = [x.strip() for x in line.split("import")[1].split(",")]
                to_add = [t for t in required if t not in existing]
                if to_add:
                    new_imports = ", ".join(existing + to_add)
                    lines[typing_line_idx] = f"from typing import {new_imports}\n"
            else:
                insert_idx = 0
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('"""') or stripped.startswith("'''") or stripped.startswith('#'):
                        insert_idx = i + 1
                    elif stripped == "":
                        insert_idx = i + 1
                    else:
                        break
                lines.insert(insert_idx, "from typing import List, Dict, Optional, Tuple, Any, Union\n")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            logger.info(f"✅ Injected typing imports into {file_path.name}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Failed to inject typing imports: {e}")
            return False

def heal_and_retry(module_name: str) -> bool:
    healer = SelfHealingAgent()
    max_retries = 2
    env = {"PYTHONPATH": str(Path(__file__).parent.parent.parent)}
    
    for attempt in range(max_retries):
        logger.info(f"🚀 Attempt {attempt + 1} to execute {module_name}...")
        result = subprocess.run([sys.executable, "-m", module_name], capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            logger.info(f"✅ {module_name} executed successfully.")
            return True
            
        logger.error(f"❌ Execution failed:\n{result.stderr}")
        
        if attempt < max_retries - 1:
            if healer.analyze_and_heal(module_name, result.stderr):
                logger.info("🔄 Retrying after autonomous healing...")
                continue
        return False
    return False
