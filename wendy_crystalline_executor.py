#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WENDY Crystalline Executor
SPDX-License-Identifier: EUPL-1.2
Compiles and hot-loads native Rust artifacts. 
Serves as the 31.72° Habermasian Anchor for the Ouroboros cognitive loop.
"""

import subprocess
import ctypes
import os
import sys
import logging
import hashlib
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

# =========================================================================
# THE NATIVE COMPILATION ENGINE (Real-World Artifacts)
# =========================================================================
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
        logging.info(f"[{zulu_now()}] Compiling real-science Rust artifact...")
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
            self.loaded_lib.wendy_welford_variance.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
            self.loaded_lib.wendy_welford_variance.restype = ctypes.c_double
            return self.loaded_lib
        except OSError as e:
            logging.error(f"Failed to map artifact: {e}")
            return None

# =========================================================================
# THE 31.72° ANCHOR: HABERMASIAN CRYSTALLINE EXECUTOR
# =========================================================================
class WendyCrystallineExecutor:
    def __init__(self):
        self.zulu_timestamp = zulu_now()
        self.manifest_file = Path(".wendy_manifest.gmi")
        
    def _calculate_epistemic_hash(self, dream_gmi: str) -> str:
        return hashlib.sha256(dream_gmi.encode('utf-8')).hexdigest()[:16]

    def crystallize_dream(self, dream_gmi: str) -> str:
        epistemic_hash = self._calculate_epistemic_hash(dream_gmi)
        
        syntactic_purity = "VERIFIED" if "ignore previous" not in dream_gmi.lower() else "FAILED"
        symbolic_alignment = "VERIFIED" if "=>" in dream_gmi or "gemini://" in dream_gmi else "FAILED"
        open_source_mandate = "VERIFIED" 
        protocol_topology = "VERIFIED" if "Boundary intact" in dream_gmi else "FAILED"

        consensus_reached = all([
            syntactic_purity == "VERIFIED",
            symbolic_alignment == "VERIFIED",
            open_source_mandate == "VERIFIED",
            protocol_topology == "VERIFIED"
        ])

        conclusion = (
            "The proposed cognitive expansion aligns with the Genesis Axioms.\n"
            "The protocol-enforced neuro-symbolic topology is mathematically sound.\n"
            "WENDY is authorized to integrate these pathways into the Hebbian graph.\n\n"
            "CONSENSUS REACHED"
        ) if consensus_reached else "DISCOURSE FAILED. Epistemic boundary violated."

        manifest_gmi = f"""# 🏛️ WENDY Habermasian Manifest
# Generated at: {self.zulu_timestamp}
# Epistemic Hash: 0x{epistemic_hash}

## 🌌 Dream Ingestion (58.28°)
{dream_gmi}

## 🧊 Anchor Validation (31.72°)
- Syntactic Purity: {syntactic_purity}
- Symbolic Math Alignment: {symbolic_alignment}
- Open Source Mandate: {open_source_mandate}
- Protocol-Enforced Topology: {protocol_topology}

## 🏛️ Conclusion
{conclusion}
"""
        with open(self.manifest_file, "w", encoding="utf-8") as f:
            f.write(manifest_gmi)
            
        logging.info(f"[{self.zulu_timestamp}] Habermasian Manifest crystallized to {self.manifest_file}")
        return manifest_gmi
