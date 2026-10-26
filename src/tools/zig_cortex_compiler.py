#!/usr/bin/env python3
# src/tools/zig_cortex_compiler.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
WENDY Zig Cortex Compiler - Direct Fix & Build
Reads source files, applies exact fixes, compiles, generates manifest.
"""

import hashlib
import json
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("ZIG_CORTEX_COMPILER")

CORE_DIR = Path("src/core")
OUTPUT_DIR = Path("zig-out/bin")
MANIFEST_PATH = Path("config/zig_cortex_hashes.json")

def fix_zig_file(zig_file: Path) -> bool:
    """Apply all necessary Zig 0.13.0 fixes to a file."""
    try:
        original = zig_file.read_text()
        modified = original
        
        # Fix 1: SHA-256 API (Zig 0.13.0 moved it to sha2 submodule)
        modified = modified.replace(
            'std.crypto.hash.Sha256',
            'std.crypto.hash.sha2.Sha256'
        )
        
        # Fix 2: @std typo
        modified = modified.replace('@import("@std")', '@import("std")')
        
        # Fix 3: Hardcoded [32]u8 for SHA-256 digest
        if 'std.crypto.hash.sha2.Sha256' in modified:
            modified = modified.replace(
                '[32]u8 = undefined',
                '[std.crypto.hash.sha2.Sha256.digest_length]u8 = undefined'
            )
        
        # Fix 4: Specific files with known var→const issues
        if zig_file.name == "ast_kernel.zig":
            # These are never mutated
            modified = modified.replace('var hash_state', 'const hash_state')
            modified = modified.replace('var result', 'const result')
        
        if zig_file.name == "arena_simd.zig":
            # arena_simd is a library, not executable - add pub fn main() stub
            if 'pub fn main()' not in modified:
                modified += '\n\npub fn main() void {}\n'
        
        if modified != original:
            zig_file.write_text(modified)
            logger.info(f"🔧 Fixed {zig_file.name}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Could not fix {zig_file.name}: {e}")
        return False

def compile_module(zig_file: Path) -> tuple[bool, Path]:
    """Compile a Zig module."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / zig_file.stem
    
    logger.info(f"⚡ Compiling {zig_file.name}...")
    
    try:
        cmd = [
            "zig", "build-exe", str(zig_file),
            "-O", "ReleaseSafe",
            "--name", zig_file.stem,
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(CORE_DIR.parent.parent)
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Failed: {zig_file.name}")
            logger.error(result.stderr)
            return False, None
        
        if output_path.exists():
            logger.info(f"✅ Success: {zig_file.name}")
            return True, output_path
        return False, None
        
    except Exception as e:
        logger.error(f"❌ Error: {zig_file.name}: {e}")
        return False, None

def compute_hash(file_path: Path) -> str:
    """SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    logger.info("🧠 Zig Cortex Compiler: Starting...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    zig_files = [f for f in CORE_DIR.glob("*.zig") if f.name != "build.zig"]
    
    if not zig_files:
        logger.error("No Zig files found")
        sys.exit(1)
    
    logger.info(f"Found {len(zig_files)} modules")
    
    # Fix all files
    for f in zig_files:
        fix_zig_file(f)
    
    # Compile all
    artifacts = []
    failed = []
    
    for f in zig_files:
        success, path = compile_module(f)
        if success and path:
            artifacts.append(path)
        else:
            failed.append(f.name)
    
    if failed:
        logger.error(f"Failed: {', '.join(failed)}")
        sys.exit(1)
    
    # Generate manifest
    manifest = {p.stem: compute_hash(p) for p in artifacts}
    
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"✅ Compiled {len(artifacts)} modules")
    logger.info(f"✅ Manifest: {MANIFEST_PATH}")

if __name__ == "__main__":
    main()
