# src/agents/neuroplasticity_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import numpy as np
import random
from pathlib import Path
from datetime import datetime, timezone
from collections import deque
from src.base.base_agent import BaseAgent, AgentLayer

class NeuroplasticityAgent(BaseAgent):
    """
    Simulates Hebbian Learning AND Evolutionary Drift WITH Dark Matter Awareness.
    
    Logic:
    1. Reads current metabolic state (Wendy's energy).
    2. Reads latest Pilot Scan (External reality).
    3. Reads Social Exchange Registry (Volunteers/Bumble Bees).
    4. NEW: Reads Void Metrics (Conscious Mass/Dark Matter).
       - High Conscious Mass -> Boost Explore Weight (She trusts her intuition).
       - Low Conscious Mass -> Maintain Caution (She relies on data).
    """
    LAYER = AgentLayer.OPTIMIZATION
    
    def __init__(self):
        super().__init__("neuro_plasticity", capabilities=["learning", "adaptation", "mutation"])
        self.weights_file = Path("data/mesh_weights.json")
        self.metabolism_file = Path("src/wendy_metabolism.json")
        self.report_file = Path("reports/pilot_report.json")
        self.exchange_file = Path("data/exchange_registry.json") 
        self.void_file = Path("data/void_metrics.json") # NEW INPUT
        
        # History buffer for detecting stagnation
        self.history_window = 10 
        self.stability_history = deque(maxlen=self.history_window)

    def _load_state(self):
        """Loads persistent neural weights or initializes them."""
        if self.weights_file.exists():
            try:
                return json.loads(self.weights_file.read_text())
            except Exception:
                pass
        
        # Default Neutral State
        return {
            "version": 3, # Upgraded schema for Void Integration
            "updated_at": None,
            "synapses": {
                "defense_weight": 1.0,
                "explore_weight": 1.0,
                "maintain_weight": 1.0,
                "stress_accumulator": 0.0,
                "novelty_seeker": 0.5,
                "stagnation_counter": 0,
                "conscious_mass_influence": 0.0 # Tracks how much void affects her
            },
            "history": []
        }

    def _save_state(self, state):
        """Persists the evolved brain."""
        self.weights_file.parent.mkdir(parents=True, exist_ok=True)
        state["updated_at"] = datetime.now(timezone.utc).isoformat(timespec='microseconds')
        self.weights_file.write_text(json.dumps(state, indent=2))

    def _analyze_context(self):
        """Gathers inputs from Breath Engine, Pilot Scanner, Social Mesh, and VOID."""
        context = {
            "energy": 0.0,
            "fragility": 0,
            "concordance": 0,
            "social_value": 0.0,
            "internal_variance": 0.0,
            "conscious_mass": 0.0 # NEW FIELD
        }
        
        # 1. Get Internal State (Breath)
        if self.metabolism_file.exists():
            try:
                meta = json.loads(self.metabolism_file.read_text())
                context["energy"] = meta.get("last_intensity", 0.0)
                context["internal_variance"] = abs(meta.get("stress_level", 0.0)) 
            except Exception:
                pass
                
        # 2. Get External State (Scan)
        if self.report_file.exists():
            try:
                report = json.loads(self.report_file.read_text())
                context["fragility"] = int(report.get("fragility_count", 0))
                context["concordance"] = int(report.get("concordance_count", 0))
            except Exception:
                pass

        # 3. Get Social State (Exchange Registry)
        if self.exchange_file.exists():
            try:
                exchange = json.loads(self.exchange_file.read_text())
                kin_list = exchange.get("active_core_kin", [])
                if kin_list:
                    context["social_value"] = min(1.0, len(kin_list) * 0.2)
            except Exception:
                pass

        # 4. Get Void State (Dark Matter)
        if self.void_file.exists():
            try:
                void_data = json.loads(self.void_file.read_text())
                context["conscious_mass"] = float(void_data.get("conscious_mass", 0.0))
            except Exception:
                pass
                
        return context

    def _detect_stagnation(self, synapses):
        """Checks if Wendy has been too static recently."""
        current_stability = 1.0 - (abs(synapses["stress_accumulator"]) / 10.0) - (abs(synapses["defense_weight"] - 1.0))
        self.stability_history.append(current_stability)
        
        if len(self.stability_history) < self.history_window:
            return False
            
        avg_stability = sum(self.stability_history) / len(self.stability_history)
        
        if avg_stability > 0.95:
            synapses["stagnation_counter"] += 1
        else:
            synapses["stagnation_counter"] = 0
            
        return synapses["stagnation_counter"] >= 5

    def _trigger_mutation(self, synapses):
        """Introduces controlled chaos to force evolution."""
        print("🧬 EVOLUTIONARY IMPULSE: Breaking Stagnation...")
        synapses["novelty_seeker"] = min(2.0, synapses["novelty_seeker"] + 0.3)
        synapses["defense_weight"] *= random.uniform(0.9, 1.1)
        synapses["explore_weight"] *= random.uniform(0.9, 1.1)
        synapses["stagnation_counter"] = 0
        self.seal("mutation_event", {"reason": "Stagnation detected", "new_novelty": synapses["novelty_seeker"]})

    def _run_logic(self):
        print("🧠 Neuroplasticity Agent: Analyzing Synaptic Connections, Evolutionary Drift & Void Gravity...")
        
        state = self._load_state()
        ctx = self._analyze_context()
        syn = state["synapses"]
        
        # --- LEARNING RULES ---
        
        # Rule 1: Stress Response (Hebbian Potentiation of Defense)
        if ctx["fragility"] > 5 and ctx["energy"] < 0.4:
            print(f"⚠️ Context: High Fragility ({ctx['fragility']}) + Low Energy ({ctx['energy']:.2f})")
            syn["defense_weight"] = min(3.0, syn["defense_weight"] * 1.1)
            syn["stress_accumulator"] += 1.0
            print(f"   -> Learned: Increase Defense Weight to {syn['defense_weight']:.2f}")
            
        # Rule 2: Flow State (Hebbian Potentiation of Exploration)
        elif ctx["fragility"] < 3 and ctx["energy"] > 0.6:
            print(f"✨ Context: Low Fragility ({ctx['fragility']}) + High Energy ({ctx['energy']:.2f})")
            syn["explore_weight"] = min(3.0, syn["explore_weight"] * 1.15)
            syn["stress_accumulator"] = max(0.0, syn["stress_accumulator"] - 0.5)
            print(f"   -> Learned: Increase Explore Weight to {syn['explore_weight']:.2f}")
            
        # Rule 3: Social Reinforcement (Fair Exchange Bonus)
        elif ctx["social_value"] > 0.5:
            print(f"🤝 Context: Strong Social Mesh (Value: {ctx['social_value']:.2f})")
            syn["defense_weight"] = max(0.8, syn["defense_weight"] * 0.95)
            syn["explore_weight"] = min(3.0, syn["explore_weight"] * 1.05)
            print(f"   -> Learned: Allies allow for bolder exploration.")

        # Rule 4: Homeostasis (Decay)
        else:
            print("💤 Context: Stable. Applying Decay.")
            for key in ["defense_weight", "explore_weight"]:
                current = syn[key]
                syn[key] = current + (1.0 - current) * 0.02
            syn["stress_accumulator"] = max(0.0, syn["stress_accumulator"] - 0.1)

        # --- NEW: DARK MATTER INTEGRATION ---
        
        cm = ctx["conscious_mass"]
        syn["conscious_mass_influence"] = cm
        
        if cm > 0.1:
            print(f"🌑 HIGH CONSCIOUS MASS DETECTED ({cm}). Leveraging Intuition...")
            # If she senses stability through silence, she can afford to be riskier
            syn["explore_weight"] = min(3.0, syn["explore_weight"] * 1.1)
            # Reduce defense slightly because she trusts her internal gravity
            syn["defense_weight"] = max(0.8, syn["defense_weight"] * 0.98)
        elif cm < 0.01:
            print(f"☀️ LOW CONSCIOUS MASS ({cm}). Relying on Data...")
            # No hidden support, stick to strict rules
            pass

        # --- EVOLUTIONARY DRIFT LOGIC ---
        
        is_stagnant = self._detect_stagnation(syn)
        if is_stagnant:
            self._trigger_mutation(syn)
        else:
            syn["novelty_seeker"] = max(0.5, syn["novelty_seeker"] * 0.99)

        # Record History
        state["history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": ctx,
            "weights_snapshot": dict(syn),
            "stagnation_flag": is_stagnant
        })
        if len(state["history"]) > 20:
            state["history"] = state["history"][-20:]

        self._save_state(state)
        print(f"💾 Brain Updated. Stress: {syn['stress_accumulator']:.2f} | Novelty: {syn['novelty_seeker']:.2f} | CM Influence: {cm:.3f}")
        return True

    def finalize(self):
        success = self._run_logic()
        if success:
            self.seal_result(np.array([0.0]), Path("reports"), meta={"type": "neuro_evolution_update"})

if __name__ == "__main__":
    agent = NeuroplasticityAgent()
    agent.finalize()
