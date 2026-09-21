# src/agents/pilot_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# RFC 1001 Compliant | OSDR-Inspired Fragility Detection

"""
The Pilot Agent: Monitors mesh epistemic health using OSDR-FRAG/CTRL logic.
Detects Fragility Traps (contradictions) and Concordant Controls (agreements).
Triggers elasticity changes based on uncertainty levels.
"""

import sys
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple

# Ensure src root is in path for imports
src_root = Path(__file__).parent.parent
sys.path.insert(0, str(src_root))

from base.base_agent import BaseAgent, AgentLayer
from core.psvc_reference import write_file, content_hash, PRECISION_FLOAT16, read_file, validate_file

class PilotAgent(BaseAgent):
    """
    Monitors the mesh for epistemic fragility (contradictions) and concordance (agreement).
    Inspired by OSDR-FRAG (Spaceflight Gene Expression Fragility) dataset.
    """
    LAYER = AgentLayer.VALIDATION

    def __init__(self, name: str = "pilot", fragility_threshold: float = 0.40, concordance_threshold: float = 0.85):
        super().__init__(name, capabilities=["scan", "analyze", "signal"])
        self.fragility_threshold = fragility_threshold
        self.concordance_threshold = concordance_threshold
        self.fragility_traps: List[Dict] = []
        self.concordant_controls: List[Dict] = []

    def _run_logic(self, input_vector: np.ndarray = None) -> np.ndarray:
        """
        Scan all vectors in the mesh, compare them, and identify fragility/concordance.
        Returns a summary vector encoding the mesh health status.
        """
        container_dir = Path("reports/pico_containers")
        if not container_dir.exists():
            self.seal("scan", {"status": "empty"}, fragility=False)
            return np.zeros(4096)

        # 1. Load all vectors with metadata
        vectors = []
        for psvc_file in container_dir.glob("*.psvc"):
            try:
                validate_file(psvc_file)
                vector = read_file(psvc_file)
                sidecar = psvc_file.with_suffix('.json')
                meta = {}
                if sidecar.exists():
                    with open(sidecar) as f:
                        meta = json.load(f)
                vectors.append({"vector": vector, "meta": meta, "file": psvc_file.name})
            except Exception:
                continue

        if len(vectors) < 2:
            self.seal("scan", {"status": "insufficient_data"}, fragility=False)
            return np.zeros(4096)

        # 2. Compare vectors (OSDR-Inspired Logic)
        # In OSDR, Fragility = Discordant log2FC signs. Here, Fragility = Low Cosine Similarity.
        self.fragility_traps = []
        self.concordant_controls = []

        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                v1 = vectors[i]["vector"]
                v2 = vectors[j]["vector"]
                
                # Calculate Cosine Similarity
                norm1 = np.linalg.norm(v1)
                norm2 = np.linalg.norm(v2)
                if norm1 == 0 or norm2 == 0:
                    continue
                similarity = float(np.dot(v1, v2) / (norm1 * norm2))

                # OSDR-FRAG Logic: Contradiction/Uncertainty
                if similarity < self.fragility_threshold:
                    trap = {
                        "type": "fragility_trap",
                        "file_a": vectors[i]["file"],
                        "file_b": vectors[j]["file"],
                        "similarity": similarity,
                        "threshold": self.fragility_threshold,
                        "agent_a": vectors[i]["meta"].get("agent", "unknown"),
                        "agent_b": vectors[j]["meta"].get("agent", "unknown")
                    }
                    self.fragility_traps.append(trap)
                    self.seal("fragility_detected", trap, fragility=True, concordance=False)

                # OSDR-CTRL Logic: Agreement/Verification
                elif similarity > self.concordance_threshold:
                    control = {
                        "type": "concordant_control",
                        "file_a": vectors[i]["file"],
                        "file_b": vectors[j]["file"],
                        "similarity": similarity,
                        "threshold": self.concordance_threshold,
                        "agent_a": vectors[i]["meta"].get("agent", "unknown"),
                        "agent_b": vectors[j]["meta"].get("agent", "unknown")
                    }
                    self.concordant_controls.append(control)
                    self.seal("concordance_verified", control, fragility=False, concordance=True)

        # 3. Generate Elasticity Signal Vector
        # Encodes the ratio of Fragility vs. Concordance for the Orchestrator to read
        signal_vector = self._generate_elasticity_signal()
        
        return signal_vector

    def _generate_elasticity_signal(self) -> np.ndarray:
        """
        Generates a 4096-dim vector encoding the mesh health.
        Used by ChainOrchestrator to decide expansion/contraction.
        """
        signal = np.zeros(4096, dtype=np.float32)
        
        # Encode counts into first few dimensions
        signal[0] = len(self.fragility_traps) / 100.0  # Normalized fragility count
        signal[1] = len(self.concordant_controls) / 100.0  # Normalized concordance count
        signal[2] = self.fragility_threshold
        signal[3] = self.concordance_threshold
        
        # Encode a hash of the receipts into the rest for integrity
        receipt_hashes = [r.payload_hash for r in self.receipt_chain]
        if receipt_hashes:
            combined_hash = content_hash(np.array(receipt_hashes))
            # Map hash to vector space (simple mapping)
            for i, char in enumerate(combined_hash[:4096]):
                signal[i+4] = ord(char) / 255.0
        
        # Normalize
        norm = np.linalg.norm(signal)
        if norm > 0:
            signal /= norm
            
        return signal

    def finalize(self, output_dir: Path = None):
        """
        Overrides BaseAgent finalize to ensure Pilot specific reports are sealed.
        """
        if output_dir is None:
            output_dir = Path("reports/pico_containers")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Seal the elasticity signal vector
        signal_vector = self._generate_elasticity_signal()
        self.seal_result(signal_vector, output_dir, meta={
            "fragility_count": len(self.fragility_traps),
            "concordance_count": len(self.concordant_controls),
            "elasticity_mode": "EXPAND" if len(self.fragility_traps) > len(self.concordant_controls) else "CONTRACT"
        })
        
        # Write human-readable OSDR-style report
        report_path = output_dir.parent / "pilot_report.json"
        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": self.creation_time,
                "fragility_traps": self.fragility_traps,
                "concordant_controls": self.concordant_controls,
                "receipt_count": len(self.receipt_chain)
            }, f, indent=2)

if __name__ == "__main__":
    print("=== PSIVI PILOT AGENT (OSDR-FRAG/CTRL INSPIRED) ===")
    pilot = PilotAgent()
    pilot._run_logic()
    pilot.finalize()
    print(f"[PILOT] Scan Complete. Fragility Traps: {len(pilot.fragility_traps)}, Concordant Controls: {len(pilot.concordant_controls)}")
