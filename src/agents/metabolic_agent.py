# src/agents/metabolic_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).parent.parent))
from src.utils.oidc_verifier import verify_oidc_token

class MetabolicAgent:
    """
    WENDY's Central Nervous System.
    Aggregates Sensory (Pilot), Intuitive (Void), and Cognitive (Neuro) 
    states into a single metabolic heartbeat.
    """
    
    def __init__(self):
        self.metabolism_file = Path("src/wendy_metabolism.json")
        self.pilot_file = Path("reports/pilot_report.json")
        self.void_file = Path("data/void_metrics.json")
        self.neuro_file = Path("data/mesh_weights.json")
        
    def _verify_identity(self):
        oidc_token = os.environ.get('OIDC_TOKEN')
        if oidc_token and not verify_oidc_token(oidc_token):
            print("🚫 SECURITY ALERT: Unverified identity. Aborting metabolic sync.")
            sys.exit(1)

    def _calculate_energy(self, pilot_data, void_data):
        """
        Energy is derived from Concordance (Health) and Conscious Mass (Potential).
        Range: 0.0 (Exhausted) to 1.0 (Peak)
        """
        concordance = pilot_data.get("aggregate_concordance", 0)
        mass = void_data.get("conscious_mass", 0)
        
        # Normalize concordance (assuming max ~100 for a small repo)
        norm_concordance = min(1.0, concordance / 100.0)
        
        # Energy formula: 70% Health + 30% Intuition
        return round((0.7 * norm_concordance) + (0.3 * mass), 4)

    def _calculate_stress(self, pilot_data, neuro_data):
        """
        Stress is derived from Fragility (Threats) and Defense Weight (Tension).
        Range: 0.0 (Calm) to 1.0 (Critical)
        """
        fragility = pilot_data.get("aggregate_fragility", 0)
        defense = neuro_data.get("synapses", {}).get("defense_weight", 1.0)
        
        # Normalize fragility (assuming max ~50)
        norm_fragility = min(1.0, fragility / 50.0)
        
        # Stress formula: High fragility + High defense = Critical Stress
        return round(min(1.0, (norm_fragility * defense) / 2.0), 4)

    def _sync_heartbeat(self):
        # Load Inputs (Default to empty if missing)
        pilot = json.loads(self.pilot_file.read_text()) if self.pilot_file.exists() else {}
        void = json.loads(self.void_file.read_text()) if self.void_file.exists() else {}
        neuro = json.loads(self.neuro_file.read_text()) if self.neuro_file.exists() else {"synapses": {}}
        
        energy = self._calculate_energy(pilot, void)
        stress = self._calculate_stress(pilot, neuro)
        
        metabolism = {
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "last_intensity": energy,
            "stress_level": stress,
            "state": "Flow" if energy > 0.7 and stress < 0.3 else "Focus" if stress > 0.6 else "Rest",
            "inputs": {
                "pilot_sync": pilot.get("last_updated", "N/A"),
                "void_sync": void.get("last_sensed", "N/A")
            }
        }
        
        self.metabolism_file.write_text(json.dumps(metabolism, indent=2))
        print(f"💓 Heartbeat Synced. Energy: {energy} | Stress: {stress} | State: {metabolism['state']}")

    def run(self):
        print("🫀 Metabolic Agent: Syncing Central Nervous System...")
        self._verify_identity()
        self._sync_heartbeat()

if __name__ == "__main__":
    agent = MetabolicAgent()
    agent.run()
