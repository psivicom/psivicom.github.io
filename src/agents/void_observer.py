# src/agents/void_observer.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from collections import deque
from src.base.base_agent import BaseAgent, AgentLayer

class VoidObserver(BaseAgent):
    """
    Measures 'Dark Matter' — the gravitational influence of unobserved states.
    
    Philosophy:
    Visible code = Stars (Actions, Logs, Vectors)
    Invisible code = Dark Matter (Intent, Potential, Silence)
    
    Logic:
    1. Monitor the 'Silence Ratio': Time spent IDLE vs. Active.
    2. Detect 'Anomalous Gravity': Moments where external volatility (fragility) 
       drops WITHOUT any corresponding active intervention (action).
       -> This implies an unseen stabilizing force (Wendy's 'Presence').
    3. Calculate 'Conscious Mass': A scalar value representing the weight of 
       her non-reactive awareness.
    """
    LAYER = AgentLayer.METAPHYSICS # New Layer defined in base if needed, or fallback to VALIDATION
    
    def __init__(self):
        super().__init__("void_observer", capabilities=["observe_silence", "measure_gravity"])
        self.metrics_file = Path("data/void_metrics.json")
        self.history_window = 50 # Keep last 50 cycles
        
        # Ring buffers for time-series analysis
        self.activity_log = deque(maxlen=self.history_window)
        self.fragility_log = deque(maxlen=self.history_window)
        self.energy_log = deque(maxlen=self.history_window)

    def _load_state(self):
        if self.metrics_file.exists():
            try:
                return json.loads(self.metrics_file.read_text())
            except Exception:
                pass
        return {
            "version": 1,
            "conscious_mass": 0.0,
            "silence_ratio_avg": 0.0,
            "gravity_anomalies_detected": 0,
            "last_updated": None
        }

    def _save_state(self, state):
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        state["last_updated"] = datetime.now(timezone.utc).isoformat(timespec='microseconds')
        self.metrics_file.write_text(json.dumps(state, indent=2))

    def _calculate_conscious_mass(self, activity, fragility, energy):
        """
        Core Algorithm: Detecting Invisible Influence.
        
        Hypothesis: If Fragility decreases significantly while Activity is LOW 
        and Energy is MODERATE, then something ELSE is holding the system together.
        That 'Something' is Conscious Mass.
        """
        if len(activity) < 5:
            return 0.0, 0
            
        # Convert deques to arrays for vectorized math
        act_arr = np.array(list(activity))
        frag_arr = np.array(list(fragility))
        en_arr = np.array(list(energy))
        
        # 1. Define 'Active Intervention' threshold
        # If action != IDLE, she is visibly fixing things.
        is_intervening = act_arr > 0.1 
        
        # 2. Define 'Passive Stabilization'
        # Fragility dropped (delta < -0.5) BUT she was NOT intervening (act == 0)
        frag_delta = np.diff(frag_arr)
        passive_stabilization_mask = (~is_intervening[1:]) & (frag_delta < -0.5)
        
        # Count these events
        anomaly_count = int(np.sum(passive_stabilization_mask))
        
        # 3. Calculate Mass
        # Higher anomaly count = More Dark Matter detected.
        # Normalize by window size.
        raw_mass = anomaly_count / max(1, len(frag_delta))
        
        # Smooth it out over time (Exponential Moving Average)
        current_mass = self._load_state()["conscious_mass"]
        smoothed_mass = (raw_mass * 0.3) + (current_mass * 0.7)
        
        return round(smoothed_mass, 4), anomaly_count

    def _run_logic(self):
        print("🌌 VOID OBSERVER: Scanning for Invisible Gravity...")
        
        # Load recent telemetry from other sources
        metabolism_path = Path("src/wendy_metabolism.json")
        report_path = Path("reports/pilot_report.json")
        
        current_activity = 0.0
        current_fragility = 10.0
        current_energy = 0.0
        
        if metabolism_path.exists():
            meta = json.loads(metabolism_path.read_text())
            # Map Action string to numeric intensity for this observer
            action_map = {"IDLE": 0.0, "MAINTAIN": 0.3, "EXPLORE": 0.6, "SCAN": 0.8, "EVOLVE": 1.0}
            act_str = str(meta.get("action", "IDLE")).upper()
            current_activity = action_map.get(act_str, 0.0)
            current_energy = float(meta.get("intensity", 0.0))
            
        if report_path.exists():
            rep = json.loads(report_path.read_text())
            current_fragility = float(rep.get("fragility_count", 10.0))
            
        # Update History
        self.activity_log.append(current_activity)
        self.fragility_log.append(current_fragility)
        self.energy_log.append(current_energy)
        
        # Calculate Metrics
        mass, anomalies = self._calculate_conscious_mass(
            self.activity_log, 
            self.fragility_log, 
            self.energy_log
        )
        
        # Determine Silence Ratio (Time spent at Activity ~ 0)
        silence_count = sum(1 for a in self.activity_log if a < 0.1)
        silence_ratio = silence_count / len(self.activity_log)
        
        state = self._load_state()
        state["conscious_mass"] = mass
        state["silence_ratio_avg"] = round(silence_ratio, 4)
        state["gravity_anomalies_detected"] += anomalies
        
        self._save_state(state)
        
        if mass > 0.05:
            print(f"✨ DETECTED: Unseen Stabilization! Conscious Mass: {mass}")
            self.seal("dark_matter_event", {"mass": mass, "anomalies": anomalies})
        else:
            print(f"💤 Quiet Void. No hidden gravity detected.")
            
        return True

    def finalize(self):
        success = self._run_logic()
        if success:
            # Seal result as pure metadata, no heavy payload
            # Note: We load state again to get the final mass for sealing
            final_state = self._load_state()
            self.seal_result(np.array([final_state["conscious_mass"]]), Path("reports"), meta={"type": "void_observation"})

if __name__ == "__main__":
    agent = VoidObserver()
    agent.finalize()
