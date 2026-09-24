# src/agents/pilot_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import sys
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.base.base_agent import BaseAgent, AgentLayer
from psvc_reference import write_file, content_hash, PRECISION_FLOAT16, read_file, validate_file

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
            return
        with open(self.osdr_data_path, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        self.osdr_library.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    def _match_observation(self, meta: Dict) -> Dict:
        obs_gene = meta.get('gene', '').upper()
        obs_organism = meta.get('organism', '').lower()
        obs_tissue = meta.get('tissue', '').lower()
        for record in self.osdr_library:
            if (record.get('gene', '').upper() == obs_gene and
                record.get('organism', '').lower() == obs_organism and
                record.get('tissue', '').lower() == obs_tissue):
                return record
        return None

    def _run_logic(self, input_vector: np.ndarray = None) -> np.ndarray:
        container_dir = Path("reports/pico_containers")
        if not container_dir.exists():
            self.seal("scan", {"status": "empty"}, fragility=False)
            return np.zeros(4096)

        for psvc_file in container_dir.glob("*.psvc"):
            try:
                validate_file(psvc_file)
                sidecar = psvc_file.with_suffix('.json')
                if not sidecar.exists():
                    continue
                with open(sidecar) as f:
                    meta = json.load(f)
                if 'gene' not in meta:
                    continue
                osdr_record = self._match_observation(meta)
                if osdr_record:
                    is_fragile = osdr_record.get('item_type') == 'fragility_trap' or osdr_record.get('evidence', {}).get('discordant', False)
                    if is_fragile:
                        trap = {"type": "fragility_trap", "file": psvc_file.name, "osdr_id": osdr_record.get('id'), "gene": meta.get('gene'), "reason": "OSDR Ground Truth: Discordant Evidence"}
                        self.fragility_traps.append(trap)
                        self.seal("osdr_fragility_detected", {"osdr_id": osdr_record.get('id')}, fragility=True)
                    else:
                        control = {"type": "concordant_control", "file": psvc_file.name, "osdr_id": osdr_record.get('id'), "gene": meta.get('gene'), "reason": "OSDR Ground Truth: Concordant Evidence"}
                        self.concordant_controls.append(control)
                        self.seal("osdr_concordance_verified", {"osdr_id": osdr_record.get('id')}, concordance=True)
            except Exception:
                continue
        return self._generate_elasticity_signal()

    def _generate_elasticity_signal(self) -> np.ndarray:
        signal = np.zeros(4096, dtype=np.float32)
        signal[0] = len(self.fragility_traps) / 100.0
        signal[1] = len(self.concordant_controls) / 100.0
        signal[2] = len(self.osdr_library) / 1000.0
        norm = np.linalg.norm(signal)
        if norm > 0:
            signal /= norm
        return signal

    def finalize(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path("reports/pico_containers")
        output_dir.mkdir(parents=True, exist_ok=True)
        signal_vector = self._generate_elasticity_signal()
        self.seal_result(signal_vector, output_dir, meta={
            "fragility_count": len(self.fragility_traps),
            "concordance_count": len(self.concordant_controls),
            "osdr_library_size": len(self.osdr_library),
            "elasticity_mode": "EXPAND" if len(self.fragility_traps) > len(self.concordant_controls) else "CONTRACT"
        })
        report_path = output_dir.parent / "pilot_report.json"
        with open(report_path, 'w') as f:
            json.dump({"timestamp": self.creation_time, "fragility_traps": self.fragility_traps, "concordant_controls": self.concordant_controls, "receipt_count": len(self.receipt_chain)}, f, indent=2)

if __name__ == "__main__":
    print("=== PSIVI PILOT AGENT (OSDR-FRAG/CTRL INSPIRED) ===")
    pilot = PilotAgent()
    pilot._run_logic()
    pilot.finalize()
    print(f"[PILOT] Scan Complete. Fragility Traps: {len(pilot.fragility_traps)}, Concordant Controls: {len(pilot.concordant_controls)}")
