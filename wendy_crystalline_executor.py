#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WENDY Crystalline Executor
SPDX-License-Identifier: EUPL-1.2
Compiles and hot-loads native Rust artifacts into WENDY's active Python synapse.
"""

import subprocess
import ctypes
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

# Strict Zulu Timestamping with Millisecond Precision
def zulu_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03dZ [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
    converters={'asctime': lambda: datetime.now(timezone.utc)}
)
# Force Zulu time in logging
for handler in logging.root.handlers:
    handler.formatter.converter = lambda *args: datetime.now(timezone.utc).timetuple()

class CrystallineExecutor:
    def __init__(self):
        self.cortex_dir = Path(__file__).parent / "wendy-cortex"
        self.crystals_file = self.cortex_dir / "src" / "crystals.rs"
        self.artifact_dir = self.cortex_dir / "target" / "release"
        self.loaded_lib = None

        if not self.crystals_file.exists():
            logging.error(f"Crystalline boundary not found at {self.crystals_file}")
            sys.exit(1)

    def _get_artifact_path(self) -> Path:
        """Resolves the correct native artifact extension based on the host OS."""
        if sys.platform.startswith("linux"):
            return self.artifact_dir / "libwendy_cortex.so"
        elif sys.platform == "darwin":
            return self.artifact_dir / "libwendy_cortex.dylib"
        elif sys.platform == "win32":
            return self.artifact_dir / "wendy_cortex.dll"
        raise OSError(f"Unsupported platform for native artifacts: {sys.platform}")

    def dream_and_compile_crystal(self, func_name: str, rust_body: str) -> bool:
        """
        Appends a new native function to crystals.rs and compiles the cdylib artifact.
        """
        logging.info(f"[{zulu_now()}] Dreaming crystalline artifact: {func_name}")
        
        # 1. Append the new Rust code to the crystals module
        rust_code = f"""
/// Autonomously generated crystalline artifact: {func_name}
/// Generated: {zulu_now()}
#[no_mangle]
pub extern "C" fn {func_name}(data: *const f64, len: usize) -> f64 {{
    let slice = unsafe {{ std::slice::from_raw_parts(data, len) }};
    {rust_body}
}}
"""
        try:
            with open(self.crystals_file, "a", encoding="utf-8") as f:
                f.write(rust_code)
        except IOError as e:
            logging.error(f"Failed to write crystalline artifact: {e}")
            return False

        # 2. Compile ONLY the library artifact (Saves massive electricity vs full rebuild)
        logging.info(f"[{zulu_now()}] Invoking incremental Rust compiler for cdylib...")
        cmd = ["cargo", "build", "--release", "--lib"]
        result = subprocess.run(cmd, cwd=self.cortex_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.error(f"Crystalline compilation failed:\n{result.stderr}")
            return False

        logging.info(f"[{zulu_now()}] Native artifact compiled successfully.")
        return True

    def load_artifact(self) -> ctypes.CDLL:
        """Hot-loads the compiled .so/.dll artifact into WENDY's active memory space."""
        artifact_path = self._get_artifact_path()
        if not artifact_path.exists():
            logging.error(f"Artifact not found at {artifact_path}. Run dream_and_compile first.")
            return None

        try:
            logging.info(f"[{zulu_now()}] Hot-loading native artifact: {artifact_path.name}")
            self.loaded_lib = ctypes.CDLL(str(artifact_path))
            return self.loaded_lib
        except OSError as e:
            logging.error(f"Failed to map artifact into memory: {e}")
            return None
