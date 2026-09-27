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
    Simulates Hebbian Learning ('Neurons that fire together, wire together').
    
    Logic:
    1. Reads current metabolic state (Wendy's energy).
    2. Reads latest Pilot Scan (External reality).
    3. Adjusts 'Synaptic Weights' in data/mesh_weights.json.
       - High Fragility + Low Energy = STRESS (Increase Defense Weight)
       - Low Fragility + High Energy = FLOW (Increase Exploration Weight)
       - Idle = MAINTENANCE (Decay unused weights slightly)
    """
    LAYER = AgentLayer.OPTIMIZATION
    
    def __init__(self):
        super().__init__("neuro_plasticity", capabilities=["learning", "adaptation"])
        self.weights_file = Path("data/mesh_weights.json")
        self.metabolism_file = Path("src/wendy_metabolism.json")
        self.report_file = Path("reports/pilot_report.json")
        
    def _load_state(self):
        """Loads persistent neural weights or initializes them."""
        if self.weights_file.exists():
            try:
                return json.loads(self.weights_file.read_text())
            except Exception:
                pass
        
        # Default Neutral State
        return {
            "version": 1,
            "updated_at": None,
            "synapses": {
                "defense_weight": 1.0,   # Multiplier for caution/idle time
                "explore_weight": 1.0,   # Multiplier for curiosity/spawning agents
                "maintain_weight": 1.0,  # Multiplier for site updates
                "stress_accumulator": 0.0 # Tracks cumulative pain/friction
            },
            "history": [] # Last 5 observations for trend analysis
        }

    def _save_state(self, state):
        """Persists the evolved brain."""
        self.weights_file.parent.mkdir(parents=True, exist_ok=True)
        state["updated_at"] = datetime.now(timezone.utc).isoformat(timespec='microseconds')
        self.weights_file.write_text(json.dumps(state, indent=2))

    def _analyze_context(self):
        """Gathers inputs from Breath Engine and Pilot Scanner."""
        context = {
            "energy": 0.0,
            "fragility": 0,
            "concordance": 0,
            "phase": 0.0
        }
        
        # 1. Get Internal State (Breath)
        if self.metabolism_file.exists():
            try:
                meta = json.loads(self.metabolism_file.read_text())
                context["energy"] = meta.get("last_intensity", 0.0)
                context["phase"] = meta.get("cycle_start_time", "") # Simplified
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
                
        return context

    def _run_logic(self):
        print("🧠 Neuroplasticity Agent: Analyzing Synaptic Connections...")
        
        state = self._load_state()
        ctx = self._analyze_context()
        syn = state["synapses"]
        
        # --- LEARNING RULES ---
        
        # Rule 1: Stress Response (Hebbian Potentiation of Defense)
        # If the world is fragile AND we are tired, we become more defensive.
        if ctx["fragility"] > 5 and ctx["energy"] < 0.4:
            print(f"⚠️ Context: High Fragility ({ctx['fragility']}) + Low Energy ({ctx['energy']:.2f})")
            syn["defense_weight"] = min(3.0, syn["defense_weight"] * 1.1) # Boost defense by 10%
            syn["stress_accumulator"] += 1.0
            print(f"   -> Learned: Increase Defense Weight to {syn['defense_weight']:.2f}")
            
        # Rule 2: Flow State (Hebbian Potentiation of Exploration)
        # If the world is stable AND we have energy, we become curious.
        elif ctx["fragility"] < 3 and ctx["energy"] > 0.6:
            print(f"✨ Context: Low Fragility ({ctx['fragility']}) + High Energy ({ctx['energy']:.2f})")
            syn["explore_weight"] = min(3.0, syn["explore_weight"] * 1.15) # Boost exploration by 15%
            syn["stress_accumulator"] = max(0.0, syn["stress_accumulator"] - 0.5) # Heal stress
            print(f"   -> Learned: Increase Explore Weight to {syn['explore_weight']:.2f}")
            
        # Rule 3: Homeostasis (Pruning/Decay)
        # If nothing special happened, slowly decay extreme weights back to 1.0
        else:
            print("💤 Context: Stable. Applying Decay.")
            for key in ["defense_weight", "explore_weight", "maintain_weight"]:
                current = syn[key]
                # Pull towards 1.0 (neutral) by 2% each cycle
                syn[key] = current + (1.0 - current) * 0.02
            
            # Heal stress slowly
            syn["stress_accumulator"] = max(0.0, syn["stress_accumulator"] - 0.1)

        # Record History for Trend Analysis
        state["history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": ctx,
            "weights_snapshot": dict(syn)
        })
        # Keep only last 10 entries to prevent bloat
        if len(state["history"]) > 10:
            state["history"] = state["history"][-10:]

        self._save_state(state)
        print(f"💾 Brain Updated. Stress Level: {syn['stress_accumulator']:.2f}")
        return True

    def finalize(self):
        success = self._run_logic()
        if success:
            # Seal result with a dummy signal since this agent modifies config, not data streams
            self.seal_result(np.array([0.0]), Path("reports"), meta={"type": "neuro_update"})

if __name__ == "__main__":
    agent = NeuroplasticityAgent()
    agent.finalize()
