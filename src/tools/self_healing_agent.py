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

class SelfHealingAgent:
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent

    def analyze_and_heal(self, module_name: str, error_output: str) -> bool:
        """
        Autonomously diagnoses TypeError keyword mismatches and patches the source code.
        """
        # 1. Extract the bad keyword from the error
        kwarg_match = re.search(r"unexpected keyword argument '(\w+)'", error_output)
        # 2. Extract the file and line number from the traceback
        file_match = re.search(r'File "([^"]+)", line (\d+)', error_output)
        
        if not kwarg_match or not file_match:
            logger.warning("⚠️ Error not recognized as a simple keyword mismatch. Cannot auto-heal.")
            return False

        bad_kwarg = kwarg_match.group(1)
        error_file = Path(file_match.group(1))
        error_line = int(file_match.group(2))

        logger.info(f"🔍 Diagnosing: Unexpected kwarg '{bad_kwarg}' in {error_file.name}:{error_line}")

        # 3. Read the failing file and extract the target line
        with open(error_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        target_line = lines[error_line - 1]
        logger.info(f"   Target line: {target_line.strip()}")

        # 4. Find the function being called on that line
        func_match = re.search(r'self\.(\w+)\.(\w+)\s*\(', target_line)
        if not func_match:
            func_match = re.search(r'(\w+)\.(\w+)\s*\(', target_line)
            
        if not func_match:
            logger.warning("⚠️ Could not parse function call on target line.")
            return False

        func_name = func_match.group(2)

        # 5. Search the codebase for the actual function definition
        actual_file = None
        actual_sig = None
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

        logger.info(f"   Found definition in {actual_file.relative_to(self.root)}: def {func_name}({actual_sig})")

        # 6. Extract valid parameters to find the correct keyword
        params = [p.split(':')[0].split('=')[0].strip() for p in actual_sig.split(',')]
        valid_kwargs = [p for p in params if p != 'self' and not p.startswith('*')]
        
        # Heuristic: If 'data' is a valid kwarg, use it. Otherwise, use the last valid kwarg.
        correct_kwarg = 'data' if 'data' in valid_kwargs else (valid_kwargs[-1] if valid_kwargs else None)
            
        if not correct_kwarg or correct_kwarg == bad_kwarg:
            logger.warning("⚠️ Could not determine correct keyword argument.")
            return False

        logger.info(f"   💡 Hypothesis: Replace '{bad_kwarg}' with '{correct_kwarg}'")

        # 7. Apply the autonomous patch
        new_line = target_line.replace(f"{bad_kwarg}=", f"{correct_kwarg}=")
        if new_line == target_line:
            logger.warning("⚠️ Patch did not change the line.")
            return False

        lines[error_line - 1] = new_line
        
        # 8. Write the fixed file
        with open(error_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        logger.info(f"✅ Applied autonomous patch to {error_file.name}:{error_line}")
        return True

def heal_and_retry(module_name: str) -> bool:
    """
    Attempts to run a module. If it fails with a patchable error, 
    heals the code and retries.
    """
    healer = SelfHealingAgent()
    max_retries = 2
    
    for attempt in range(max_retries):
        logger.info(f"🚀 Attempt {attempt + 1} to execute {module_name}...")
        env = {"PYTHONPATH": str(Path(__file__).parent.parent.parent)}
        result = subprocess.run(
            [sys.executable, "-m", module_name],
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {module_name} executed successfully.")
            return True
            
        logger.error(f"❌ Execution failed:\n{result.stderr}")
        
        if attempt < max_retries - 1:
            healed = healer.analyze_and_heal(module_name, result.stderr)
            if healed:
                logger.info("🔄 Retrying after autonomous healing...")
                continue
            else:
                logger.warning("⚠️ Healing failed. Moving to next agent.")
                return False
                
    return False
