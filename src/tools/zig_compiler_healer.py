# src/tools/zig_compiler_healer.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import subprocess
import shutil
import re
from pathlib import Path
import logging

logger = logging.getLogger("ZIG_COMPILER_HEALER")

def parse_zig_error(stderr: str) -> tuple:
    """Parses ZIG compiler output to extract the exact file, line, and error message."""
    # ZIG errors typically look like: src/core/file.zig:15:5: error: use of undeclared identifier 'foo'
    match = re.search(r'([^:]+\.zig):(\d+):\d+: error: (.+)', stderr)
    if match:
        return match.group(1), int(match.group(2)), match.group(3).strip()
    return None, None, None

def apply_zig_patch(file_path: Path, line_num: int, error_msg: str) -> bool:
    """Applies targeted heuristic patches based on the specific ZIG compiler error."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        patched = False
        
        # Heuristic 1: Missing standard library import
        if "use of undeclared identifier 'std'" in error_msg:
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('//') or line.strip() == '':
                    insert_idx = i + 1
                else:
                    break
            lines.insert(insert_idx, 'const std = @import("std");\n')
            patched = True

        # Heuristic 2: Missing allocator or specific std imports
        elif "use of undeclared identifier 'allocator'" in error_msg:
            insert_idx = 0
            for i, line in enumerate(lines):
                if "const std" in line:
                    insert_idx = i + 1
                    break
            lines.insert(insert_idx, 'const allocator = std.heap.page_allocator;\n')
            patched = True

        # Heuristic 3: Expected type mismatch (common in ZIG strict typing)
        elif "expected" in error_msg and "found" in error_msg:
            # For complex type mismatches, we log it for the AI cognitive bridge to handle
            logger.info(f"🧠 Complex type mismatch detected at {file_path.name}:{line_num}. Flagging for AI cognitive resolution.")
            return False 

        if patched:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
            
        return False
        
    except Exception as e:
        logger.warning(f"⚠️ Exception during ZIG patch application: {e}")
        return False

def heal_zig_file(zig_file: Path) -> bool:
    """Iteratively compiles and heals a ZIG file up to 5 times until successful."""
    binary_name = zig_file.stem
    binary_path = zig_file.parent / binary_name
    
    # Deep-space-grade compilation flags: ReleaseSafe, stripped, explicit output
    cmd = [
        "zig", "build-exe", str(zig_file), 
        "-O", "ReleaseSafe", 
        "-fstrip", 
        f"-femit-bin={binary_path}"
    ]
    
    max_passes = 5
    for attempt in range(max_passes):
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # SUCCESS: The file compiled perfectly
        if result.returncode == 0:
            logger.info(f"✅ {zig_file.name} compiled successfully on pass {attempt + 1}.")
            return True
            
        # FAILURE: Parse the error and attempt to heal
        file_path, line_num, error_msg = parse_zig_error(result.stderr)
        
        if not file_path:
            logger.warning(f"⚠️ Could not parse ZIG error output for {zig_file.name}.")
            return False
            
        logger.info(f"🩹 Pass {attempt + 1}/{max_passes}: Diagnosed error at {Path(file_path).name}:{line_num} -> {error_msg}")
        
        # Attempt to apply a heuristic patch
        if not apply_zig_patch(Path(file_path), line_num, error_msg):
            logger.warning(f"⚠️ No deterministic patch available for: '{error_msg}'. Escalating to AI cognitive bridge or marking as unhealable.")
            return False
            
        logger.info(f"🔄 Patch applied. Recompiling {zig_file.name}...")
        
    logger.error(f"❌ {zig_file.name} failed to compile after {max_passes} iterative passes. Hard limit reached.")
    return False

def main():
    logger.info("🧠 ZIG Iterative Compiler Healer Initializing...")
    
    # GRACEFUL FALLBACK: If Zig is not installed, exit cleanly.
    if not shutil.which("zig"):
        logger.warning("⚠️ 'zig' executable not found in PATH. Skipping ZIG compilation cycle.")
        return

    core_dir = Path("src/core")
    if not core_dir.exists():
        logger.info("ℹ️ src/core not found.")
        return

    zig_files = list(core_dir.glob("*.zig"))
    logger.info(f"🔍 Found {len(zig_files)} ZIG files to evaluate and heal.")

    success_count = 0
    for zig_file in zig_files:
        if heal_zig_file(zig_file):
            success_count += 1
            
    logger.info(f"🏁 ZIG Healing Cycle Complete. Successfully compiled {success_count}/{len(zig_files)} binaries.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    main()
