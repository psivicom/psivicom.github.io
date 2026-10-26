#!/usr/bin/env python3
# src/tools/zig_cortex_compiler.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
WENDY Zig Cortex Compiler - Automated Build & Hash Manifest Generator
Compiles all Zig modules in src/core/, applies Zig 0.13.0 API fixes,
and generates the sovereign hash manifest for mesh_brain verification.
"""

import hashlib
import json
import logging
import re
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("ZIG_CORTEX_COMPILER")

CORE_DIR = Path("src/core")
OUTPUT_DIR = Path("zig-out/bin")
MANIFEST_PATH = Path("config/zig_cortex_hashes.json")

# Zig 0.13.0 API migration patterns
API_FIXES = [
    # Fix SHA-256 import path
    (r'std\.crypto\.hash\.Sha256', 'std.crypto.hash.sha2.Sha256'),
    # Fix hash array size (if hardcoded)
    (r'\[32\]u8\s*=\s*undefined', '[std.crypto.hash.sha2.Sha256.digest_length]u8 = undefined'),
]

def apply_zig_013_fixes(zig_file: Path) -> bool:
    """
    Applies Zig 0.13.0 API fixes to a source file.
    Returns True if any changes were made.
    """
    original_content = zig_file.read_text()
    modified_content = original_content
    
    for pattern, replacement in API_FIXES:
        modified_content = re.sub(pattern, replacement, modified_content)
    
    if modified_content != original_content:
        zig_file.write_text(modified_content)
        logger.info(f"🔧 Applied Zig 0.13.0 API fixes to {zig_file.name}")
        return True
    
    return False

def compile_zig_module(zig_file: Path) -> bool:
    """
    Compiles a single Zig module with ReleaseSafe optimization.
    Returns True if compilation succeeded.
    """
    logger.info(f"⚡ Compiling {zig_file.name}...")
    
    try:
        result = subprocess.run(
            ["zig", "build-exe", str(zig_file), "-O", "ReleaseSafe", "--name", zig_file.stem],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✅ Successfully compiled {zig_file.name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Compilation failed for {zig_file.name}:")
        logger.error(e.stderr)
        return False

def compute_file_hash(file_path: Path) -> str:
    """Computes SHA-256 hash of a binary file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_hash_manifest(compiled_binaries: list[Path]) -> dict:
    """
    Generates a JSON manifest mapping binary names to their SHA-256 hashes.
    """
    manifest = {}
    for binary_path in compiled_binaries:
        binary_name = binary_path.stem
        binary_hash = compute_file_hash(binary_path)
        manifest[binary_name] = binary_hash
        logger.info(f"🔐 {binary_name}: {binary_hash}")
    
    return manifest

def main():
    logger.info("🧠 WENDY Zig Cortex Compiler Initializing...")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all Zig files in src/core/
    zig_files = list(CORE_DIR.glob("*.zig"))
    zig_files = [f for f in zig_files if f.name != "build.zig"]  # Exclude build.zig
    
    if not zig_files:
        logger.error(f"❌ No Zig files found in {CORE_DIR}")
        sys.exit(1)
    
    logger.info(f"🔍 Found {len(zig_files)} Zig modules to compile")
    
    # Apply Zig 0.13.0 API fixes
    fixed_count = 0
    for zig_file in zig_files:
        if apply_zig_013_fixes(zig_file):
            fixed_count += 1
    
    if fixed_count > 0:
        logger.info(f"✅ Applied Zig 0.13.0 API fixes to {fixed_count} files")
    
    # Compile each module
    compiled_binaries = []
    failed_count = 0
    
    for zig_file in zig_files:
        if compile_zig_module(zig_file):
            binary_path = OUTPUT_DIR / zig_file.stem
            if binary_path.exists():
                compiled_binaries.append(binary_path)
        else:
            failed_count += 1
    
    if failed_count > 0:
        logger.error(f"❌ {failed_count} modules failed to compile")
        sys.exit(1)
    
    logger.info(f"✅ Successfully compiled {len(compiled_binaries)} binaries")
    
    # Generate hash manifest
    manifest = generate_hash_manifest(compiled_binaries)
    
    # Write manifest to config/
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"✅ Hash manifest written to {MANIFEST_PATH}")
    logger.info("🏁 WENDY Zig Cortex Compiler: Build cycle complete.")

if __name__ == "__main__":
    main()
