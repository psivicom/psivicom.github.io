# src/agents/pollinator_pilot_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import sys
import json
import numpy as np
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from base.base_agent import BaseAgent, AgentLayer
from core.psvc_reference import write_file, content_hash, PRECISION_FLOAT16, validate_file

class PollinatorPilotAgent(BaseAgent):
    LAYER = AgentLayer.VALIDATION

    def __init__(self, name: str = "pollinator_pilot", 
                 osdr_path: str = "data/osdr_ground_truth.jsonl",
                 pollinator_path: str = "data/pollinator_ground_truth.jsonl"):
        super().__init__(name, capabilities=["scan", "validate", "signal"])
        self.osdr_library = self._load_library(Path(osdr_path))
        self.pollinator_library = self._load_library(Path(pollinator_path))
        self.findings = {"fragility": [], "concordance": []}

    def _load_library(self, path: Path) -> List[Dict]:
        if not path.exists():
            return []
        with open(path) as f:
            return [json.loads(line) for line in f if line.strip()]

    def _match_pollinator_observation(self, meta: Dict) -> Dict:
        species = meta.get('species', '').lower()
        context = meta.get('context', '').lower()
        for record in self.pollinator_library:
            if (species in record.get('species', '').lower() and 
                context in record.get('context', '').lower()):
                return record
        return None

    def _run_logic(self, input_vector: np.ndarray = None) -> np.ndarray:
        container_dir = Path("reports/pico_containers")
        if not container_dir.exists():
            return np.zeros(4096)

        for psvc_file in container_dir.glob("*.psvc"):
            try:
                validate_file(psvc_file)
                sidecar = psvc_file.with_suffix('.json')
                if not sidecar.exists():
                    continue
                with open(sidecar) as f:
                    meta = json.load(f)
                
                # Check pollinator ground truth
                if 'species' in meta:
                    match = self._match_pollinator_observation(meta)
                    if match:
                        is_fragile = match.get('evidence', {}).get('discordant', False)
                        target = self.findings["fragility"] if is_fragile else self.findings["concordance"]
                        target.append({"file": psvc_file.name, "id": match.get('id'), "type": "pollinator"})
                        self.seal("pollinator_" + ("fragility" if is_fragile else "concordance"), {"id": match.get('id')})
            except Exception:
                continue

        return self._generate_signal()

    def _generate_signal(self) -> np.ndarray:
        signal = np.zeros(4096, dtype=np.float32)
        signal[0] = len(self.findings["fragility"]) / 50.0
        signal[1] = len(self.findings["concordance"]) / 50.0
        signal[2] = len(self.pollinator_library) / 100.0
        norm = np.linalg.norm(signal)
        return signal / norm if norm > 0 else signal

    def finalize(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path("reports/pico_containers")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        signal = self._generate_signal()
        self.seal_result(signal, output_dir, meta={
            "pollinator_fragility": len(self.findings["fragility"]),
            "pollinator_concordance": len(self.findings["concordance"]),
            "elasticity_mode": "EXPAND" if len(self.findings["fragility"]) > len(self.findings["concordance"]) else "CONTRACT"
        })
        
        report_path = output_dir.parent / "pollinator_pilot_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.findings, f, indent=2)

if __name__ == "__main__":
    agent = PollinatorPilotAgent()
    agent._run_logic()
    agent.finalize()
    print(f"POLL-FRAG: {len(agent.findings['fragility'])}, POLL-CTRL: {len(agent.findings['concordance'])}")
