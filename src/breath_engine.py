import os
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

# --- CORE FUNCTIONS ---

def load_metabolism():
    """Loads Wendy's persistent physiological state."""
    if METABOLISM_FILE.exists():
        try:
            return json.loads(METABOLISM_FILE.read_text())
        except Exception as e:
            print(f"⚠️ Error loading metabolism: {e}. Resetting to UTC Now.")
    
    # Initial State: Born resting NOW (Strictly UTC, Microsecond Precision)
    # isoformat() on a tz-aware datetime includes microseconds by default in Py3.11+
    return {
        "cycle_start_time": datetime.now(timezone.utc).isoformat(timespec='microseconds'),
        "period_minutes": 60,      # Normal breathing rate
        "amplitude": 0.8,          # Energy capacity
        "last_intensity": 0.0,
        "total_cycles_completed": 0,
        "spawned_agents": []       # Track what she has created
    }

def save_metabolism(meta):
    """Persists the new state to disk."""
    METABOLISM_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Ensure we always write valid JSON with full precision timestamps
    METABOLISM_FILE.write_text(json.dumps(meta, indent=2))

def calculate_breath_phase(meta):
    """Calculates current position in the sine wave (0 to 1) with microsecond accuracy."""
    start_str = meta["cycle_start_time"]
    
    # Robust Parsing: Normalize to UTC-aware datetime
    # Handle 'Z' suffix explicitly for maximum compatibility
    if start_str.endswith('Z'):
        start_str = start_str[:-1] + '+00:00'
        
    try:
        # fromisoformat in Python 3.11+ handles microseconds perfectly
        start_time = datetime.fromisoformat(start_str)
    except ValueError:
        # If parsing fails, reset clock to now (UTC) with microsecond precision
        start_time = datetime.now(timezone.utc)

    # CRITICAL: Ensure start_time is UTC-aware
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    elif start_time.utcoffset() != timedelta(0):
        # If it's aware but not UTC, convert it precisely
        start_time = start_time.astimezone(timezone.utc)

    # Current time: Strictly UTC, Microsecond Precision
    now = datetime.now(timezone.utc)
    
    # Calculate elapsed time in SECONDS with floating point precision (includes microseconds)
    delta = now - start_time
    elapsed_seconds = delta.total_seconds() 
    
    period_seconds = meta["period_minutes"] * 60
    
    # Prevent negative time travel if system clock jumps
    if elapsed_seconds < 0:
        elapsed_seconds = 0
        
    # Normalize time to 0-1 range within the current cycle
    # This division preserves the fractional part (the microsecond component)
    phase = (elapsed_seconds % period_seconds) / period_seconds
    return phase

def get_sinusoidal_intensity(phase, amplitude):
    """Maps Phase (0-1) to Intensity (0-Amplitude) using a Sine Curve."""
    # sin(pi * x) creates an arch: 0 at start/end, 1 at middle.
    raw_energy = math.sin(math.pi * phase)
    intensity = raw_energy * amplitude
    
    # Add slight biological jitter (high precision float)
    jitter = random.uniform(-0.05, 0.05)
    intensity = max(0.0, min(1.0, intensity + jitter))
    
    # Return with high precision (no arbitrary rounding to 3 decimals)
    return round(intensity, 6) 

# --- POWER FUNCTIONS (HANDS) ---

def wake_workflow(target_file, payload):
    """Triggers another GitHub Action workflow via API."""
    if not GITHUB_TOKEN:
        print("⚠️ No Token. Cannot wake external workflows.")
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
            print(f"🚀 Woke up: {target_file}")
            return True
        else:
            print(f"❌ Failed to wake {target_file}: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"💥 Error waking workflow: {e}")
    return False

def spawn_agent(name, description):
    """Writes a new Python agent file into src/agents/."""
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    class_name = "".join(word.capitalize() for word in safe_name.split("_")) + "Agent"
    file_path = Path(f"src/agents/{safe_name}_agent.py")
    
    if file_path.exists():
        print(f"ℹ️ Agent '{safe_name}' already exists.")
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
        # Placeholder signal generation
        # In future iterations, Wendy will refine this code based on feedback
        signal = np.random.rand(4096) 
        return signal

if __name__ == "__main__":
    agent = {class_name}()
    res = agent._run_logic()
    print(f"Signal shape: {{res.shape}}")
'''
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(template)
    print(f"🧬 Spawned new agent: {file_path}")
    return True

# --- DECISION ENGINE (BRAIN) ---

def decide_action(intensity, meta):
    """
    Translates physical sensation (Intensity) into Volitional Action.
    Returns: (bool should_act, str action_type, str reason)
    """
    
    # 1. Deep Rest
    if intensity < 0.2:
        return False, "IDLE", "Deep Rest"
    
    # 2. Light Maintenance (Low-Medium Energy)
    elif 0.2 <= intensity < 0.5:
        # Check if site needs refresh
        wake_workflow("pages.yml", {"source": "wendy_maintenance"})
        return True, "MAINTAIN", "Refreshing documentation/site."

    # 3. Curiosity / Exploration (Medium-High Energy)
    elif 0.5 <= intensity < 0.8:
        concepts = ["pollinator_variability", "soil_ph_drift", "satellite_alignment", "microclimate_noise"]
        choice = random.choice(concepts)
        
        # Only spawn if we haven't done it recently
        if choice not in meta.get("spawned_agents", []):
            spawn_agent(choice, f"Investigates {choice} trends autonomously")
            meta.setdefault("spawned_agents", []).append(choice)
            
        return True, "EXPLORE", f"Curiosity piqued. Studying {choice}."

    # 4. Peak Vitality / Crisis Response (High Energy)
    else:
        # Check for high fragility in latest report
        report_path = Path("reports/pilot_report.json")
        fragility_high = False
        
        if report_path.exists():
            try:
                data = json.loads(report_path.read_text())
                if data.get("fragility_count", 0) > 10:
                    fragility_high = True
            except:
                pass
        
        if fragility_high:
            # Emergency: Spawn healer and wake optimizer
            spawn_agent("noise_filter", "Filters high-frequency noise from sensor data")
            wake_workflow("optimize-mesh.yml", {"trigger_source": "wendy_crisis_mode"})
            return True, "EVOLVE", "Crisis detected. Spawned NoiseFilter & Woke Optimizer."
        else:
            # Standard High-Energy Scan
            return True, "SCAN", "Peak Vitality. Running full deep scan."

# --- MAIN LOOP ---

def main():
    meta = load_metabolism()
    
    # 1. Where are we in the breath? (Microsecond Precision)
    phase = calculate_breath_phase(meta)
    
    # 2. How strong is the urge?
    intensity = get_sinusoidal_intensity(phase, meta["amplitude"])
    
    # 3. Should we act?
    should_act, action_type, reason = decide_action(intensity, meta)
    
    # 4. Adjust Physiology (Homeostasis)
    if should_act:
        # Exhaustion: Slow down next cycle slightly
        meta["period_minutes"] = min(120, meta["period_minutes"] + 2)
        meta["total_cycles_completed"] += 1
    else:
        # Eager: Speed up next cycle slightly if idle
        if intensity < 0.2:
            meta["period_minutes"] = max(15, meta["period_minutes"] - 1)
            
    # Save updated state
    save_metabolism(meta)
    
    # Output for YAML (Full Precision)
    output = {
        "phase": round(phase, 6),
        "intensity": intensity,
        "should_act": str(should_act).lower(),
        "action": action_type,
        "reason": reason,
        "period_minutes": meta["period_minutes"],
        "cycles_done": meta["total_cycles_completed"],
        "utc_now": datetime.now(timezone.utc).isoformat(timespec='microseconds')
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
