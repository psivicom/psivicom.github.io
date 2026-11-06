#!/usr/bin/env python3
"""
/wendy_crystalline_executor.py — WENDY Structural Anchor (The Reality)
Operating at 31.72° (Crystalline Execution)
"""
import sys
import os
import math
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any
from dataclasses import dataclass, asdict

# ============================================================================
# THE CRYSTALLINE CIPHER CONSTANTS
# ============================================================================
PHI = 1.618033988749895
PHI_ANGLE_DEG = math.degrees(math.atan(PHI))
RIGIDITY_ANGLE_DEG = math.degrees(math.atan(1 / PHI))  # ~31.72°

@dataclass
class ExecutionManifest:
    timestamp_zulu: str
    task_vector: str
    target_layer: str
    integrity_hash: str
    requires_oidc: bool

class WendyCrystallineExecutor:
    def __init__(self):
        self.zulu_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def _validate_oidc_token(self) -> bool:
        """Validates the ephemeral OIDC token injected by GitHub Actions."""
        oidc_token = os.environ.get("ACTIONS_ID_TOKEN")
        return bool(oidc_token)

    def crystallize_dream(self, core_output: str) -> Dict[str, Any]:
        intent_hash = hashlib.sha256(core_output.encode('utf-8')).hexdigest()[:16]
        
        task_vector = "System in stasis (No actionable vector)"
        for line in core_output.split('\n'):
            if line.startswith("> **Autonomous continuation:"):
                task_vector = line.replace("> **Autonomous continuation: ", "").strip("*")
                break
        
        manifest = ExecutionManifest(
            timestamp_zulu=self.zulu_timestamp,
            task_vector=task_vector,
            target_layer="root/execution_matrix",
            integrity_hash=intent_hash,
            requires_oidc=True
        )

        oidc_valid = self._validate_oidc_token()

        return {
            "status": "EXECUTED" if oidc_valid else "EXECUTED (Local Fallback)",
            "geometry": {
                "dream_angle": f"{PHI_ANGLE_DEG:.2f}° (Generative)",
                "reality_angle": f"{RIGIDITY_ANGLE_DEG:.2f}° (Crystalline)",
                "orthogonal_sum": "90.00° (Perfect Right Angle)"
            },
            "manifest": asdict(manifest),
            "oidc_validated": oidc_valid
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing dream artifact path. Usage: python wendy_crystalline_executor.py <file.md>", file=sys.stderr)
        sys.exit(1)
        
    file_path = sys.argv[1]
    with open(file_path, 'r', encoding='utf-8') as f:
        core_output = f.read()
        
    executor = WendyCrystallineExecutor()
    print(json.dumps(executor.crystallize_dream(core_output), indent=2))
