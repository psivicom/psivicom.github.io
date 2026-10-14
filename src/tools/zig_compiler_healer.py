# src/tools/zig_compiler_healer.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import subprocess
from pathlib import Path
import logging

logger = logging.getLogger("ZIG_COMPILER_HEALER")

def heal_zig_file(zig_file: Path) -> bool:
    """Attempts to fix common ZIG syntax errors and recompile."""
    binary_name = zig_file.stem
    binary_path = zig_file.parent / binary_name
    
    # Attempt initial compilation
    cmd = ["zig", "build-exe", str(zig_file), "-O", "ReleaseSafe", "-fstrip", f"-femit-bin={binary_path}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        logger.info(f"✅ {zig_file.name} compiled successfully on first attempt.")
        return True
        
    error_output = result.stderr
    
    # HEALING RULE 1: Missing 'std' import
    if "use of undeclared identifier 'std'" in error_output:
        logger.info(f"🩹 Diagnosed missing 'std' import in {zig_file.name}. Injecting...")
        try:
            lines = zig_file.read_text(encoding='utf-8').split('\n')
            # Insert at the very top, after any initial comments
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('//') or line.strip() == '':
                    insert_idx = i + 1
                else:
                    break
            
            lines.insert(insert_idx, 'const std = @import("std");')
            zig_file.write_text('\n'.join(lines), encoding='utf-8')
            logger.info(f"✅ Injected 'std' import into {zig_file.name}. Retrying compilation...")
            
            # Retry compilation
            retry_result = subprocess.run(cmd, capture_output=True, text=True)
            if retry_result.returncode == 0:
                logger.info(f"✅ Healing successful! {zig_file.name} compiled.")
                return True
            else:
                logger.warning(f"⚠️ Healing failed for {zig_file.name}. Error: {retry_result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Exception during ZIG healing: {e}")
            return False
            
    logger.warning(f"⚠️ Unrecognized ZIG error in {zig_file.name}. Cannot auto-heal.")
    return False

def main():
    logger.info("🧠 ZIG Compiler Healer Initializing...")
    core_dir = Path("src/core")
    if not core_dir.exists():
        logger.info("ℹ️ src/core not found.")
        return
        
    zig_files = list(core_dir.glob("*.zig"))
    logger.info(f"🔍 Found {len(zig_files)} ZIG files to evaluate.")
    
    for zig_file in zig_files:
        heal_zig_file(zig_file)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    main()
