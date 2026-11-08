#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WENDY Crystalline Executor
SPDX-License-Identifier: EUPL-1.2
Compiles and hot-loads native Rust artifacts for real-time Earth Observation science.
"""

import subprocess
import ctypes
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

def zulu_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03dZ [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
for handler in logging.root.handlers:
    handler.formatter.converter = lambda *args: datetime.now(timezone.utc).timetuple()

class CrystallineExecutor:
    def __init__(self):
        self.cortex_dir = Path(__file__).parent / "wendy-cortex"
        self.artifact_dir = self.cortex_dir / "target" / "release"
        self.loaded_lib = None

    def _get_artifact_path(self) -> Path:
        if sys.platform.startswith("linux"):
            return self.artifact_dir / "libwendy_cortex.so"
        elif sys.platform == "darwin":
            return self.artifact_dir / "libwendy_cortex.dylib"
        elif sys.platform == "win32":
            return self.artifact_dir / "wendy_cortex.dll"
        raise OSError(f"Unsupported platform: {sys.platform}")

    def compile_artifact(self) -> bool:
        logging.info(f"[{zulu_now()}] Compiling real-science Rust artifact (Welford's Variance)...")
        cmd = ["cargo", "build", "--release", "--lib"]
        result = subprocess.run(cmd, cwd=self.cortex_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.error(f"Compilation failed:\n{result.stderr}")
            return False
            
        logging.info(f"[{zulu_now()}] Native artifact compiled with LTO and SIMD optimizations.")
        return True

    def load_artifact(self) -> ctypes.CDLL:
        artifact_path = self._get_artifact_path()
        if not artifact_path.exists():
            logging.error(f"Artifact not found at {artifact_path}.")
            return None

        try:
            logging.info(f"[{zulu_now()}] Hot-loading native artifact: {artifact_path.name}")
            self.loaded_lib = ctypes.CDLL(str(artifact_path))
            
            # Define strict C-FFI signatures for real science functions
            self.loaded_lib.wendy_welford_variance.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
            self.loaded_lib.wendy_welford_variance.restype = ctypes.c_double
            
            return self.loaded_lib
        except OSError as e:
            logging.error(f"Failed to map artifact: {e}")
            return None
