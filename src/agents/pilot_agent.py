# src/agents/pilot_agent.py
import sys
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple

# CRITICAL FIX: Ensure project root is in path if run directly, 
# BUT rely on PYTHONPATH env var for CI correctness.
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_reference import write_file, content_hash, PRECISION_FLOAT16, read_file, validate_file

class PilotAgent(BaseAgent):
    LAYER = AgentLayer.VALIDATION

    def __init__(self, name: str = "pilot", osdr_data_path: str = "data/osdr_ground_truth.jsonl"):
        super().__init__(name, capabilities=["scan", "analyze", "signal"])
        self.osdr_data_path = Path(osdr_data_path)
        self.osdr_library: List[Dict] = []
        self.fragility_traps: List[Dict] = []
        self.concordant_controls: List[Dict] = []
        self._load_osdr_library()

    def _load_osdr_library(self):
        if not self.osdr_data_path.exists():
            # Create dummy library if missing so it doesn't crash
            self.osdr_library = []
            return
        with open(self.osdr_data_path, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        self.osdr_library.append(record)
                    except json.JSONDecodeError:
                        continue

    def _run_logic(self) -> np.ndarray:
        container_dir = Path("reports/pico_containers")
        if not container_dir.exists():
            self.seal("scan", {"status": "empty"}, fragility=False)
            return np.zeros(4096)

        self.fragility_traps = []
        self.concordant_controls = []

        # Simulate scanning containers
        count = 0
        for psvc_file in container_dir.glob("*.psvc"):
            count += 1
            # Simple heuristic for demo: Even index = control, Odd = trap
            if count % 2 == 0:
                self.concordant_controls.append({"file": psvc_file.name})
            else:
                self.fragility_traps.append({"file": psvc_file.name})
            
            self.seal("container_checked", {"file": psvc_file.name}, fragility=(count%2!=0))
            
        return self._generate_elasticity_signal()

    def _generate_elasticity_signal(self) -> np.ndarray:
        signal = np.zeros(4096, dtype=np.float32)
        signal[0] = len(self.fragility_traps) / 100.0
        signal[1] = len(self.concordant_controls) / 100.0
        norm = np.linalg.norm(signal)
        if norm > 0:
            signal /= norm
        return signal

    def finalize(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path("reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        signal_vector = self._run_logic()
        
        self.seal_result(signal_vector, output_dir, meta={
            "fragility_count": len(self.fragility_traps),
            "concordance_count": len(self.concordant_controls),
            "osdr_library_size": len(self.osdr_library)
        })
        
        # Write the report Wendy reads
        report_path = output_dir / "pilot_report.json"
        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": self.creation_time,
                "fragility_count": len(self.fragility_traps),
                "concordance_count": len(self.concordant_controls),
                "receipt_count": len(self.receipt_chain)
            }, f, indent=2)
        print(f"📄 Report written to {report_path}")

if __name__ == "__main__":
    pilot = PilotAgent()
    pilot.finalize()
