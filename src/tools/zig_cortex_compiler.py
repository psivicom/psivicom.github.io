#!/usr/bin/env python3
# src/tools/zig_cortex_compiler.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
WENDY Zig Cortex Compiler - Sequential Sovereign Build
Compiles each Zig module one at a time, saving the binary directly into src/core/
with explicit verification before proceeding to the next module.
"""

import hashlib
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("ZIG_CORTEX_COMPILER")

CORE_DIR = Path("src/core")
MANIFEST_PATH = Path("config/zig_cortex_hashes.json")
SAVE_VERIFY_RETRIES = 5
SAVE_VERIFY_DELAY = 0.5

def apply_known_fixes(zig_file: Path) -> bool:
    """Apply only the verified Zig 0.13.0 API fixes."""
    try:
        original = zig_file.read_text()
        modified = original
        modified = modified.replace('std.crypto.hash.Sha256', 'std.crypto.hash.sha2.Sha256')
        modified = modified.replace('@import("@std")', '@import("std")')
        modified = modified.replace('"\\\\n"', '"\\n"')
        if modified != original:
            zig_file.write_text(modified)
            logger.info(f"Fixed {zig_file.name}")
            return True
        return False
    except Exception as e:
        logger.warning(f"Could not process {zig_file.name}: {e}")
        return False

def verify_binary_saved(binary_path: Path, expected_min_size: int = 1000) -> bool:
    """
    Verify that a binary file has been fully saved to disk.
    Checks existence, non-zero size, and stability across multiple reads.
    """
    for attempt in range(SAVE_VERIFY_RETRIES):
        if not binary_path.exists():
            logger.warning(f"Binary not found at {binary_path}, attempt {attempt + 1}/{SAVE_VERIFY_RETRIES}")
            time.sleep(SAVE_VERIFY_DELAY)
            continue
        
        size1 = binary_path.stat().st_size
        if size1 < expected_min_size:
            logger.warning(f"Binary too small ({size1} bytes), attempt {attempt + 1}/{SAVE_VERIFY_RETRIES}")
            time.sleep(SAVE_VERIFY_DELAY)
            continue
        
        time.sleep(0.2)
        size2 = binary_path.stat().st_size
        
        if size1 == size2 and size2 > 0:
            logger.info(f"Verified: {binary_path.name} ({size2} bytes, stable)")
            return True
        
        logger.warning(f"Binary size unstable ({size1} vs {size2}), attempt {attempt + 1}/{SAVE_VERIFY_RETRIES}")
    
    return False

def compile_and_save_sequentially(zig_file: Path) -> tuple[bool, Path]:
    """
    Compile a single Zig module and save the binary directly into src/core/.
    Blocks until the binary is verified as fully written to disk.
    """
    binary_name = f"{zig_file.stem}.bin"
    binary_path = CORE_DIR / binary_name
    
    logger.info(f"Compiling {zig_file.name} -> {binary_path}")
    
    try:
        cmd = [
            "zig", "build-exe", str(zig_file),
            "-O", "ReleaseSafe",
            "--name", zig_file.stem,
            "-femit-bin=" + str(binary_path),
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(Path.cwd())
        )
        
        if result.returncode != 0:
            logger.error(f"Compilation failed for {zig_file.name}:")
            logger.error(result.stderr)
            return False, None
        
        if not verify_binary_saved(binary_path):
            logger.error(f"Binary save verification failed for {zig_file.name}")
            return False, None
        
        logger.info(f"Saved and verified: {binary_path.name}")
        return True, binary_path
        
    except Exception as e:
        logger.error(f"Error compiling {zig_file.name}: {e}")
        return False, None

def compute_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    logger.info("WENDY Zig Cortex Compiler: Sequential Sovereign Build")
    
    zig_files = sorted([
        f for f in CORE_DIR.glob("*.zig")
        if f.name != "build.zig"
    ])
    
    if not zig_files:
        logger.error("No Zig files found in src/core/")
        sys.exit(1)
    
    logger.info(f"Found {len(zig_files)} modules to compile sequentially")
    
    for f in zig_files:
        apply_known_fixes(f)
    
    saved_binaries = []
    failed = []
    
    for i, zig_file in enumerate(zig_files, 1):
        logger.info(f"[{i}/{len(zig_files)}] Processing {zig_file.name}...")
        
        success, binary_path = compile_and_save_sequentially(zig_file)
        
        if success and binary_path:
            saved_binaries.append(binary_path)
            logger.info(f"[{i}/{len(zig_files)}] Complete: {zig_file.name}")
        else:
            failed.append(zig_file.name)
            logger.error(f"[{i}/{len(zig_files)}] Failed: {zig_file.name}")
    
    if failed:
        logger.error(f"Failed modules: {', '.join(failed)}")
        sys.exit(1)
    
    logger.info(f"All {len(saved_binaries)} binaries saved and verified in src/core/")
    
    manifest = {}
    for binary_path in saved_binaries:
        name = binary_path.stem
        manifest[name] = compute_hash(binary_path)
        logger.info(f"Hash {name}: {manifest[name][:16]}...")
    
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"Hash manifest written to {MANIFEST_PATH}")
    logger.info("Sequential sovereign build complete.")

if __name__ == "__main__":
    main()
