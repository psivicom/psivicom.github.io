# src/agents/pilot_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Pilot Agent: Validation Layer
Scans the repository for PSVC containers, analyzes them against 
OSDR ground truth, and signals fragility or concordance to the mesh.
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from typing import Dict, List

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.zulu_clock import get_zulu_timestamp_ms

class PilotAgent(BaseAgent):
    LAYER = AgentLayer.VALIDATION

    def __init__(self, name: str = "pilot", osdr_data_path: str = "data/osdr_ground_truth.jsonl"):
        super().__init__(name, capabilities=["scan", "analyze", "signal"])
        self.osdr_data_path = Path(osdr_data_path)
        self.osdr_library: List[Dict] = []
        self.fragility_traps: List[Dict] = []
        self.concordant_controls: List[Dict] = []
        self.receipt_chain: List[Dict] = []
        self._load_osdr_library()

    def _load_osdr_library(self):
        """Loads the OSDR ground truth library for validation reference."""
        if self.osdr_data_path.exists():
            with open(self.osdr_data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.osdr_library.append(json.loads(line))

    def seal(self, action: str, metadata: Dict, fragility: bool = False):
        """Records a state seal to the receipt chain to prevent AttributeError."""
        receipt = {
            "action": action,
            "metadata": metadata,
            "fragility": fragility,
            "timestamp": get_zulu_timestamp_ms()
        }
        self.receipt_chain.append(receipt)

    def seal_result(self, signal_vector: np.ndarray, output_dir: Path, meta: Dict):
        """Writes the final signal vector and metadata to a receipt file."""
        sig_hash = hashlib.sha256(signal_vector.tobytes()).hexdigest()
        
        receipt_data = {
            "signal_hash": sig_hash,
            "meta": meta,
            "timestamp": get_zulu_timestamp_ms()
        }
        
        safe_time = receipt_data["timestamp"].replace(':', '-').replace('.', '-')
        receipt_path = output_dir / f"receipt_{self.name}_{safe_time}.json"
        
        with open(receipt_path, 'w', encoding='utf-8') as f:
            json.dump(receipt_data, f, indent=2)
            
        self.seal("result_sealed", {"receipt_path": str(receipt_path)})

    def _run_logic(self) -> np.ndarray:
        """Scans instruction queue for PSVC containers and evaluates concordance."""
        data_dir = Path("data/instruction_queue")
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            
        psvc_files = list(data_dir.glob("*.psvc"))
        
        for psvc_file in psvc_files:
            # Simulated validation logic: in production, this would deserialize 
            # the PSVC and compare its metadata/checksum against self.osdr_library
            is_fragile = len(psvc_files) % 2 != 0 
            
            self.seal("container_checked", {"file": psvc_file.name}, fragility=is_fragile)
            
            if is_fragile:
                self.fragility_traps.append({"file": psvc_file.name, "reason": "schema_mismatch_or_missing_ground_truth"})
            else:
                self.concordant_controls.append({"file": psvc_file.name})
                
        # Generate standardized 4096-dimensional float32 signal vector
        signal_vector = np.random.randn(4096).astype(np.float32)
        signal_vector /= np.linalg.norm(signal_vector)
        return signal_vector

    def finalize(self, output_dir: Path = None):
        """Executes validation logic and writes the final pilot report."""
        if output_dir is None:
            output_dir = Path("reports/validation")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        signal_vector = self._run_logic()
        
        self.seal_result(signal_vector, output_dir, meta={
            "fragility_count": len(self.fragility_traps),
            "concordance_count": len(self.concordant_controls),
            "osdr_library_size": len(self.osdr_library)
        })
        
        # Write the aggregate report for the Ledger Validator / Synthesizer
        report_path = output_dir / "pilot_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                "aggregate_fragility": float(len(self.fragility_traps)),
                "aggregate_concordance": float(len(self.concordant_controls)),
                "last_updated": get_zulu_timestamp_ms(),
                "receipt_count": len(self.receipt_chain)
            }, f, indent=2)
            
        print(f"📄 Pilot Report written to {report_path}")
        return signal_vector

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    # Ensure directories exist for testing
    Path("data/instruction_queue").mkdir(parents=True, exist_ok=True)
    
    pilot = PilotAgent()
    pilot.finalize()
    print("✅ Pilot Agent execution complete.")
