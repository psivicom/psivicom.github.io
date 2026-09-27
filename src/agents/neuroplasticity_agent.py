# src/agents/neuroplasticity_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from src.base.base_agent import BaseAgent, AgentLayer

class NeuroplasticityAgent(BaseAgent):
    """
    Simulates synaptic pruning and weight adjustment based on recent activity logs.
    In a real ML context, this would update model weights. 
    Here, it updates 'importance scores' of data nodes in the mesh.
    """
    LAYER = AgentLayer.OPTIMIZATION
    
    def __init__(self):
        super().__init__("neuro_plasticity", capabilities=["learning", "adaptation"])
        self.memory_file = Path("data/mesh_weights.json")
        
    def _load_weights(self):
        if self.memory_file.exists():
            try:
                return json.loads(self.memory_file.read_text())
            except:
                pass
        # Initialize with default neutral weights
        return {
            "nodes": {},
            "last_update": None
        }

    def _save_weights(self, weights):
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        weights["last_update"] = datetime.now(timezone.utc).isoformat(timespec='microseconds')
        self.memory_file.write_text(json.dumps(weights, indent=2))

    def _run_logic(self):
        print("🧠 Analyzing neural pathways...")
        weights = self._load_weights()
        
        # Simulate learning from recent reports
        report_path = Path("reports/pilot_report.json")
        if report_path.exists():
            try:
                report = json.loads(report_path.read_text())
                fragility = report.get("fragility_count", 0)
                
                # Heuristic: High fragility -> Strengthen validation nodes
                # Low fragility -> Prune unused nodes
                if fragility > 5:
                    print(f"⚠️ High Fragility Detected ({fragility}). Reinforcing defenses.")
                    weights["defense_multiplier"] = min(2.0, weights.get("defense_multiplier", 1.0) + 0.1)
                else:
                    print("✅ System Stable. Pruning weak connections.")
                    # Decay logic simulation
                    if "decay_rate" not in weights:
                        weights["decay_rate"] = 0.99
                    weights["decay_rate"] *= 0.995
                    
            except Exception as e:
                print(f"❌ Error reading report: {e}")
        else:
            print("ℹ️ No recent reports. Maintaining current state.")

        self._save_weights(weights)
        print("💾 Neural weights updated.")
        return True

    def finalize(self):
        success = self._run_logic()
        if success:
            self.seal_result(np.array([1.0]), Path("reports"), meta={"type": "neuro_update"})

if __name__ == "__main__":
    agent = NeuroplasticityAgent()
    agent.finalize()
