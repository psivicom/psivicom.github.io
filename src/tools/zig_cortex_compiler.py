#!/usr/bin/env python3
# src/tools/zig_cortex_compiler.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
WENDY Zig Cortex Compiler - Intelligent Automated Build System
Handles executables, libraries, API migrations, and mutability corrections.
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
LIB_DIR = Path("zig-out/lib")
MANIFEST_PATH = Path("config/zig_cortex_hashes.json")

# Comprehensive Zig 0.13.0 API migration patterns
API_FIXES = [
    # SHA-256 import path
    (r'std\.crypto\.hash\.Sha256', 'std.crypto.hash.sha2.Sha256'),
    # @std typo fix
    (r'@import\("@std"\)', '@import("std")'),
]

def is_executable(zig_file: Path) -> bool:
    """Detect if a Zig file has pub fn main() — making it an executable."""
    try:
        content = zig_file.read_text()
        return bool(re.search(r'pub\s+fn\s+main\s*\(', content))
    except Exception:
        return False

def smart_var_to_const(content: str) -> str:
    """
    Heuristic var → const converter.
    Analyzes each 'var IDENT = ...' declaration and checks if IDENT is ever
    reassigned or mutated. If not, converts to 'const'.
    """
    lines = content.split('\n')
    result_lines = []
    
    for i, line in enumerate(lines):
        # Match: var IDENT = <expression>;
        match = re.match(r'^(\s*)var\s+(\w+)\s*=\s*(.+)$', line)
        if match:
            indent, var_name, expr = match.groups()
            
            # Check if var_name is mutated anywhere in the file
            is_mutated = False
            
            for j, other_line in enumerate(lines):
                if j == i:
                    continue
                
                # Direct assignment: var_name = ...
                if re.search(rf'\b{re.escape(var_name)}\s*=[^=]', other_line):
                    is_mutated = True
                    break
                
                # Compound assignment: var_name += ..., etc.
                if re.search(rf'\b{re.escape(var_name)}\s*(\+|-|\*|/|%|&|\||\^|<<|>>)=', other_line):
                    is_mutated = True
                    break
                
                # Pointer dereference mutation: var_name.* = ...
                if re.search(rf'\b{re.escape(var_name)}\.\*\s*=', other_line):
                    is_mutated = True
                    break
                
                # Array/slice index mutation: var_name[...] = ...
                if re.search(rf'\b{re.escape(var_name)}\[.*\]\s*=', other_line):
                    is_mutated = True
                    break
            
            if not is_mutated:
                line = f"{indent}const {var_name} = {expr}"
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)

def apply_zig_fixes(zig_file: Path) -> bool:
    """Apply all known Zig API fixes and mutability corrections."""
    try:
        original = zig_file.read_text()
        modified = original
        
        for pattern, replacement in API_FIXES:
            modified = re.sub(pattern, replacement, modified)
        
        # Smart var → const fixer
        modified = smart_var_to_const(modified)
        
        if modified != original:
            zig_file.write_text(modified)
            return True
        return False
    except Exception as e:
        logger.warning(f"⚠️ Could not apply fixes to {zig_file.name}: {e}")
        return False

def compile_module(zig_file: Path, is_exe: bool) -> tuple[bool, Path]:
    """Compile a Zig module as executable or library."""
    output_dir = OUTPUT_DIR if is_exe else LIB_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    artifact_type = "executable" if is_exe else "library"
    logger.info(f"⚡ Compiling {zig_file.name} as {artifact_type}...")
    
    try:
        if is_exe:
            output_path = output_dir / zig_file.stem
            cmd = [
                "zig", "build-exe", str(zig_file),
                "-O", "ReleaseSafe",
                "--name", zig_file.stem,
                f"-femit-bin={output_path}",
            ]
        else:
            output_path = output_dir / f"lib{zig_file.stem}.a"
            cmd = [
                "zig", "build-lib", str(zig_file),
                "-O", "ReleaseSafe",
                "--name", zig_file.stem,
                f"-femit-bin={output_path}",
            ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(CORE_DIR.parent.parent)
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Compilation failed for {zig_file.name}:")
            logger.error(result.stderr)
            return False, None
        
        if output_path.exists():
            logger.info(f"✅ Successfully compiled {zig_file.name} → {output_path}")
            return True, output_path
        else:
            logger.warning(f"⚠️ Compilation succeeded but artifact not found for {zig_file.name}")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ Compilation error for {zig_file.name}: {e}")
        return False, None

def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a binary file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_hash_manifest(artifacts: list[Path]) -> dict:
    """Generate JSON manifest mapping artifact names to SHA-256 hashes."""
    manifest = {}
    for artifact_path in artifacts:
        name = artifact_path.stem
        if name.startswith("lib"):
            name = name[3:]
        manifest[name] = compute_file_hash(artifact_path)
        logger.info(f"🔐 {name}: {manifest[name][:16]}...")
    return manifest

def main():
    logger.info("🧠 WENDY Zig Cortex Compiler Initializing...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    
    zig_files = [f for f in CORE_DIR.glob("*.zig") if f.name != "build.zig"]
    
    if not zig_files:
        logger.error(f"❌ No Zig files found in {CORE_DIR}")
        sys.exit(1)
    
    logger.info(f"🔍 Found {len(zig_files)} Zig modules to process")
    
    # Classify files
    executables = []
    libraries = []
    for f in zig_files:
        if is_executable(f):
            executables.append(f)
        else:
            libraries.append(f)
    
    logger.info(f"📦 Classified: {len(executables)} executables, {len(libraries)} libraries")
    
    # Apply fixes
    fixed_count = sum(1 for f in zig_files if apply_zig_fixes(f))
    if fixed_count > 0:
        logger.info(f"✅ Applied API/mutability fixes to {fixed_count} files")
    
    # Compile
    compiled_artifacts = []
    failed = []
    
    for exe in executables:
        success, artifact = compile_module(exe, is_exe=True)
        if success and artifact:
            compiled_artifacts.append(artifact)
        else:
            failed.append(exe.name)
    
    for lib in libraries:
        success, artifact = compile_module(lib, is_exe=False)
        if success and artifact:
            compiled_artifacts.append(artifact)
        else:
            failed.append(lib.name)
    
    if failed:
        logger.error(f"❌ {len(failed)} modules failed: {', '.join(failed)}")
        sys.exit(1)
    
    logger.info(f"✅ Successfully compiled {len(compiled_artifacts)} artifacts")
    
    # Generate manifest
    manifest = generate_hash_manifest(compiled_artifacts)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"✅ Hash manifest written to {MANIFEST_PATH}")
    logger.info("🏁 WENDY Zig Cortex Compiler: Build cycle complete.")

if __name__ == "__main__":
    main()
