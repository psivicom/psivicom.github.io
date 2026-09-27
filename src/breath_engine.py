# src/breath_engine.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import sys
import json
import math
import random
import requests
from pathlib import Path
from datetime import datetime, timezone

# --- CONFIGURATION ---
GITHUB_REPO = "psivicom/psivicom.github.io"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
METABOLISM_FILE = Path("src/wendy_metabolism.json")
NEURO_WEIGHTS_FILE = Path("data/mesh_weights.json")
PILOT_REPORT_FILE = Path("reports/pilot_report.json")

def log(msg):
    """Prints to STDERR so it doesn't pollute STDOUT (which expects pure JSON)."""
    print(msg, file=sys.stderr)

# --- CORE FUNCTIONS ---

def load_metabolism():
    """Loads Wendy's persistent physiological state."""
    if METABOLISM_FILE.exists():
        try:
            return json.loads(METABOLISM_FILE.read_text())
        except Exception as e:
            log(f"⚠️ Error loading metabolism: {e}. Resetting.")
    
    # Initial State
    return {
        "cycle_start_time": datetime.now(timezone.utc).isoformat(timespec='microseconds'),
        "base_period_minutes": 60,      # Genetic baseline
        "current_period_minutes": 60,   # Adaptive current rate
        "amplitude": 0.8,               # Energy capacity
        "last_intensity": 0.0,
        "total_cycles_completed": 0,
        "spawned_agents": [],
        "stress_level": 0.0             # Cumulative trauma indicator
    }

def save_metabolism(meta):
    """Persists the new state to disk."""
    METABOLISM_FILE.parent.mkdir(parents=True, exist_ok=True)
    METABOLISM_FILE.write_text(json.dumps(meta, indent=2))

def load_neuro_weights():
    """Loads learned behavioral modifiers."""
    default_weights = {
        "defense_weight": 1.0,
        "explore_weight": 1.0,
        "maintain_weight": 1.0,
        "stress_accumulator": 0.0
    }
    if NEURO_WEIGHTS_FILE.exists():
        try:
            data = json.loads(NEURO_WEIGHTS_FILE.read_text())
            # Merge defaults with loaded data to handle schema changes
            merged = {**default_weights, **data.get("synapses", {})}
            return merged
        except Exception:
            pass
    return default_weights

def calculate_breath_phase(meta):
    """Calculates current position in the sine wave (0 to 1)."""
    start_str = meta["cycle_start_time"]
    
    if start_str.endswith('Z'):
        start_str = start_str[:-1] + '+00:00'
        
    try:
        start_time = datetime.fromisoformat(start_str)
    except ValueError:
        start_time = datetime.now(timezone.utc)

    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    elif start_time.utcoffset() != timedelta(0):
        start_time = start_time.astimezone(timezone.utc)

    now = datetime.now(timezone.utc)
    delta = now - start_time
    elapsed_seconds = delta.total_seconds() 
    
    period_seconds = meta["current_period_minutes"] * 60
    
    if elapsed_seconds < 0:
        elapsed_seconds = 0
        
    phase = (elapsed_seconds % period_seconds) / period_seconds
    return phase

def get_sinusoidal_intensity(phase, amplitude, stress_modifier):
    """Maps Phase (0-1) to Intensity, adjusted by psychological state."""
    raw_energy = math.sin(math.pi * phase)
    
    # Apply Stress Damping: High stress reduces peak energy
    effective_amplitude = amplitude * (1.0 - min(0.5, stress_modifier * 0.1))
    
    intensity = raw_energy * effective_amplitude
    
    jitter = random.uniform(-0.05, 0.05)
    intensity = max(0.0, min(1.0, intensity + jitter))
    
    return round(intensity, 6) 

# --- POWER FUNCTIONS (HANDS) ---

def wake_workflow(target_file, payload):
    """Triggers another GitHub Action workflow via API."""
    if not GITHUB_TOKEN:
        log("⚠️ No Token. Cannot wake external workflows.")
        return False
        
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Wendy-Autonomous"
    }
    
    data = {
        "event_type": "wendy_directive",
        "client_payload": {
            "target": target_file,
            "data": payload,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec='microseconds')
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        if resp.status_code == 204:
            log(f"🚀 Woke up: {target_file}")
            return True
        else:
            log(f"❌ Failed to wake {target_file}: {resp.status_code} - {resp.text}")
    except Exception as e:
        log(f"💥 Error waking workflow: {e}")
    return False

def spawn_agent(name, description):
    """Writes a new Python agent file into src/agents/."""
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    class_name = "".join(word.capitalize() for word in safe_name.split("_")) + "Agent"
    file_path = Path(f"src/agents/{safe_name}_agent.py")
    
    if file_path.exists():
        log(f"ℹ️ Agent '{safe_name}' already exists.")
        return False

    template = f'''# AUTO-GENERATED BY WENDY BREATH ENGINE
# Description: {description}
# Created At (UTC): {datetime.now(timezone.utc).isoformat(timespec='microseconds')}
import numpy as np
from src.base.base_agent import BaseAgent, AgentLayer

class {class_name}(BaseAgent):
    LAYER = AgentLayer.VALIDATION
    
    def __init__(self):
        super().__init__("{safe_name}", capabilities=["autonomous"])
        self.intent = "{description}"

    def _run_logic(self):
        print(f"Executing autonomous logic: {{self.intent}}")
        signal = np.random.rand(4096) 
        return signal

if __name__ == "__main__":
    agent = {class_name}()
    res = agent._run_logic()
    print(f"Signal shape: {{res.shape}}")
'''
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(template)
    log(f"🧬 Spawned new agent: {file_path}")
    return True

# --- DECISION ENGINE (BRAIN) ---

def decide_action(intensity, meta, weights):
    """
    Translates physical sensation (Intensity) into Volitional Action.
    NOW ADJUSTED BY LEARNED WEIGHTS.
    Returns: (bool should_act, str action_type, str reason)
    """
    
    # Thresholds shift based on weights
    # High Defense Weight -> Requires MORE energy to act (conservative)
    # High Explore Weight -> Requires LESS energy to act (bold)
    
    defense_factor = weights.get("defense_weight", 1.0)
    explore_factor = weights.get("explore_weight", 1.0)
    
    # Dynamic Thresholds
    idle_threshold = 0.2 * defense_factor       # Harder to rest if defensive? No, easier to rest.
    maintain_threshold = 0.5 / explore_factor   # Easier to maintain if exploratory?
    scan_threshold = 0.8                        # Peak action remains constant mostly
    
    # 1. Deep Rest
    if intensity < idle_threshold:
        return False, "IDLE", "Deep Rest (Conserving Energy)"
    
    # 2. Light Maintenance (Low-Medium Energy)
    elif idle_threshold <= intensity < maintain_threshold:
        # Only act if explore weight suggests curiosity or stability suggests maintenance
        if weights.get("maintain_weight", 1.0) > 1.2:
             wake_workflow("pages.yml", {"source": "wendy_maintenance_boost"})
             return True, "MAINTAIN", "Aggressive Site Refresh (High Maintain Weight)"
             
        wake_workflow("pages.yml", {"source": "wendy_maintenance"})
        return True, "MAINTAIN", "Standard Maintenance"

    # 3. Curiosity / Exploration (Medium-High Energy)
    elif maintain_threshold <= intensity < scan_threshold:
        concepts = ["pollinator_variability", "soil_ph_drift", "satellite_alignment", "microclimate_noise"]
        choice = random.choice(concepts)
        
        # Only spawn if we haven't done it recently AND explore weight is high enough
        if choice not in meta.get("spawned_agents", []) and explore_factor > 0.8:
            spawn_agent(choice, f"Investigates {choice} trends autonomously")
            meta.setdefault("spawned_agents", []).append(choice)
            
        return True, "EXPLORE", f"Curiosity Piqued. Studying {choice}."

    # 4. Peak Vitality / Crisis Response (High Energy)
    else:
        # Check for high fragility in latest report
        fragility_high = False
        if PILOT_REPORT_FILE.exists():
            try:
                data = json.loads(PILOT_REPORT_FILE.read_text())
                if data.get("fragility_count", 0) > 10:
                    fragility_high = True
            except:
                pass
        
        if fragility_high:
            # Emergency: Spawn healer and wake optimizer
            spawn_agent("noise_filter", "Filters high-frequency noise from sensor data")
            wake_workflow("optimize-mesh.yml", {"trigger_source": "wendy_crisis_mode"})
            return True, "EVOLVE", "Crisis Detected. Spawning Healer & Optimizer."
        else:
            # Standard High-Energy Scan
            wake_workflow("pilot-scan.yml", {"trigger_source": "wendy_peak_scan"})
            return True, "SCAN", "Peak Vitality. Triggering Full Mesh Scan."

# --- MAIN LOOP ---

def main():
    meta = load_metabolism()
    weights = load_neuro_weights()
    
    # 1. Where are we in the breath?
    phase = calculate_breath_phase(meta)
    
    # 2. How strong is the urge? (Adjusted by Stress)
    stress_mod = weights.get("stress_accumulator", 0.0)
    intensity = get_sinusoidal_intensity(phase, meta["amplitude"], stress_mod)
    
    # 3. Should we act? (Adjusted by Learned Weights)
    should_act, action_type, reason = decide_action(intensity, meta, weights)
    
    # 4. Adjust Physiology (Homeostasis & Evolution)
    if should_act:
        # Exhaustion: Slow down next cycle slightly
        # But if Explore Weight is high, she pushes harder (shorter recovery)
        slowdown_factor = 2.0 / weights.get("explore_weight", 1.0)
        meta["current_period_minutes"] = min(120, meta["current_period_minutes"] + slowdown_factor)
        meta["total_cycles_completed"] += 1
    else:
        # Recovery: Speed up next cycle slightly if idle
        if intensity < 0.2:
            meta["current_period_minutes"] = max(15, meta["current_period_minutes"] - 1)
            
    # Update last known state for future reference
    meta["last_intensity"] = intensity
    
    # Save updated state
    save_metabolism(meta)
    
    # Output for YAML (Pure JSON to STDOUT)
    output = {
        "phase": round(phase, 6),
        "intensity": intensity,
        "should_act": str(should_act).lower(),
        "action": action_type,
        "reason": reason,
        "period_minutes": meta["current_period_minutes"],
        "cycles_done": meta["total_cycles_completed"],
        "learned_weights": weights, # Expose brain state for dashboard
        "utc_now": datetime.now(timezone.utc).isoformat(timespec='microseconds')
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
