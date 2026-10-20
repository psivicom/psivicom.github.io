# src/agents/neuroplasticity_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import os
import sys
import numpy as np
import random
from pathlib import Path
from datetime import datetime, timezone
from collections import deque

# Add project root to path for local testing if needed
sys.path.append(str(Path(__file__).parent.parent))

from src.base.base_agent import BaseAgent, AgentLayer
from src.utils.oidc_verifier import verify_oidc_token

class NeuroplasticityAgent(BaseAgent):
    LAYER = AgentLayer.VALIDATION
    
    def __init__(self):
        super().__init__("neuro_plasticity", capabilities=["learning", "adaptation", "mutation"])
        self.weights_file = Path("data/mesh_weights.json")
        self.metabolism_file = Path("src/wendy_metabolism.json")
        self.report_file = Path("reports/pilot_report.json")
        self.exchange_file = Path("data/exchange_registry.json") 
        self.void_file = Path("data/void_metrics.json")
        
        self.history_window = 10 
        self.stability_history = deque(maxlen=self.history_window)

    def _load_state(self):
        if self.weights_file.exists():
            try:
                return json.loads(self.weights_file.read_text())
            except Exception:
                pass
        return {
            "version": 3,
            "updated_at": None,
            "synapses": {
                "defense_weight": 1.0,
                "explore_weight": 1.0,
                "maintain_weight": 1.0,
                "stress_accumulator": 0.0,
                "novelty_seeker": 0.5,
                "stagnation_counter": 0,
                "conscious_mass_influence": 0.0
            },
            "history": []
        }

    def _save_state(self, state):
        self.weights_file.parent.mkdir(parents=True, exist_ok=True)
        state["updated_at"] = datetime.now(timezone.utc).isoformat(timespec='microseconds')
        self.weights_file.write_text(json.dumps(state, indent=2))

    def _analyze_context(self):
        context = {
            "energy": 0.0, "fragility": 0, "concordance": 0,
            "social_value": 0.0, "internal_variance": 0.0, "conscious_mass": 0.0
        }
        
        if self.metabolism_file.exists():
            try:
                meta = json.loads(self.metabolism_file.read_text())
                context["energy"] = meta.get("last_intensity", 0.0)
                context["internal_variance"] = abs(meta.get("stress_level", 0.0)) 
            except Exception: pass
                
        if self.report_file.exists():
            try:
                report = json.loads(self.report_file.read_text())
                context["fragility"] = int(report.get("fragility_count", 0))
                context["concordance"] = int(report.get("concordance_count", 0))
            except Exception: pass

        if self.exchange_file.exists():
            try:
                exchange = json.loads(self.exchange_file.read_text())
                kin_list = exchange.get("active_core_kin", [])
                if kin_list: context["social_value"] = min(1.0, len(kin_list) * 0.2)
            except Exception: pass

        if self.void_file.exists():
            try:
                void_data = json.loads(self.void_file.read_text())
                context["conscious_mass"] = float(void_data.get("conscious_mass", 0.0))
            except Exception: pass
                
        return context

    def _detect_stagnation(self, synapses):
        current_stability = 1.0 - (abs(synapses["stress_accumulator"]) / 10.0) - (abs(synapses["defense_weight"] - 1.0))
        self.stability_history.append(current_stability)
        if len(self.stability_history) < self.history_window: return False
        avg_stability = sum(self.stability_history) / len(self.stability_history)
        if avg_stability > 0.95: synapses["stagnation_counter"] += 1
        else: synapses["stagnation_counter"] = 0
        return synapses["stagnation_counter"] >= 5

    def _trigger_mutation(self, synapses):
        print("🧬 EVOLUTIONARY IMPULSE: Breaking Stagnation...")
        synapses["novelty_seeker"] = min(2.0, synapses["novelty_seeker"] + 0.3)
        synapses["defense_weight"] *= random.uniform(0.9, 1.1)
        synapses["explore_weight"] *= random.uniform(0.9, 1.1)
        synapses["stagnation_counter"] = 0
        self.seal_result(np.array([0.0]), Path("reports"), meta={"type": "mutation_event"})

    def _run_logic(self):
        print("🧠 Neuroplasticity Agent: Analyzing Synaptic Connections & Void Gravity...")
        
        # Sovereign Identity Check
        oidc_token = os.environ.get('OIDC_TOKEN')
        if oidc_token and not verify_oidc_token(oidc_token):
            print("🚫 SECURITY ALERT: Unverified identity. Aborting neuroplasticity.")
            sys.exit(1)

        state = self._load_state()
        ctx = self._analyze_context()
        syn = state["synapses"]
        
        # --- LEARNING RULES ---
        if ctx["fragility"] > 5 and ctx["energy"] < 0.4:
            syn["defense_weight"] = min(3.0, syn["defense_weight"] * 1.1)
            syn["stress_accumulator"] += 1.0
        elif ctx["fragility"] < 3 and ctx["energy"] > 0.6:
            syn["explore_weight"] = min(3.0, syn["explore_weight"] * 1.15)
            syn["stress_accumulator"] = max(0.0, syn["stress_accumulator"] - 0.5)
        elif ctx["social_value"] > 0.5:
            syn["defense_weight"] = max(0.8, syn["defense_weight"] * 0.95)
            syn["explore_weight"] = min(3.0, syn["explore_weight"] * 1.05)
        else:
            for key in ["defense_weight", "explore_weight"]:
                syn[key] = syn[key] + (1.0 - syn[key]) * 0.02
            syn["stress_accumulator"] = max(0.0, syn["stress_accumulator"] - 0.1)

        # --- DARK MATTER INTEGRATION ---
        cm = ctx["conscious_mass"]
        syn["conscious_mass_influence"] = cm
        if cm > 0.1:
            syn["explore_weight"] = min(3.0, syn["explore_weight"] * 1.1)
            syn["defense_weight"] = max(0.8, syn["defense_weight"] * 0.98)

        # --- EVOLUTIONARY DRIFT ---
        if self._detect_stagnation(syn):
            self._trigger_mutation(syn)
        else:
            syn["novelty_seeker"] = max(0.5, syn["novelty_seeker"] * 0.99)

        state["history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": ctx,
            "weights_snapshot": dict(syn)
        })
        if len(state["history"]) > 20: state["history"] = state["history"][-20:]

        self._save_state(state)
        return True

    def finalize(self):
        if self._run_logic():
            self.seal_result(np.array([0.0]), Path("reports"), meta={"type": "neuro_evolution_update"})

if __name__ == "__main__":
    agent = NeuroplasticityAgent()
    agent.finalize()
