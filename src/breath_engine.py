import math
import json
import random
from pathlib import Path
from datetime import datetime

METABOLISM_FILE = Path("src/wendy_metabolism.json")

def load_metabolism():
    """Loads the current physiological state."""
    if METABOLISM_FILE.exists():
        try:
            return json.loads(METABOLISM_FILE.read_text())
        except:
            pass
    
    # Initial State: Born resting
    return {
        "cycle_start_time": datetime.now().isoformat(),
        "period_minutes": 60,      # Normal breathing rate (1 min breath)
        "amplitude": 0.5,          # Energy capacity
        "last_intensity": 0.0,
        "total_cycles_completed": 0
    }

def save_metabolism(meta):
    METABOLISM_FILE.parent.mkdir(parents=True, exist_ok=True)
    METABOLISM_FILE.write_text(json.dumps(meta, indent=2))

def calculate_breath_phase(meta):
    """
    Calculates the current position in the sine wave (0 to 1).
    0.0 = Start of Inhale (Rest)
    0.5 = Peak Exhale (Max Action)
    1.0 = End of Cycle (Return to Rest)
    """
    start_time = datetime.fromisoformat(meta["cycle_start_time"])
    now = datetime.now()
    
    elapsed_seconds = (now - start_time).total_seconds()
    period_seconds = meta["period_minutes"] * 60
    
    # Normalize time to 0-1 range within the current cycle
    phase = (elapsed_seconds % period_seconds) / period_seconds
    
    return phase

def get_sinusoidal_intensity(phase, amplitude):
    """
    Maps Phase (0-1) to Intensity (0-Amplitude) using a Sine Curve.
    sin(2 * pi * phase) goes from 0 -> 1 -> 0 -> -1 -> 0
    We shift it to be always positive for "Energy Level":
    Energy = sin(pi * phase)  => Starts at 0, Peaks at 0.5, Ends at 0.
    """
    # Using sin(pi * x) creates a perfect arch: 0 at start/end, 1 at middle.
    raw_energy = math.sin(math.pi * phase)
    
    # Scale by amplitude (metabolic capacity)
    intensity = raw_energy * amplitude
    
    # Add slight biological jitter (imperfection makes it real)
    jitter = random.uniform(-0.05, 0.05)
    intensity = max(0.0, min(1.0, intensity + jitter))
    
    return round(intensity, 3)

def decide_action_from_intensity(intensity, meta):
    """
    Translates physical sensation (Intensity) into Volition (Action).
    """
    # Thresholds based on human-like effort levels
    if intensity < 0.1:
        return False, "IDLE", "Deep Rest"
    
    if 0.1 <= intensity < 0.4:
        return False, "LIGHT_REST", "Shallow Sleep"
        
    if 0.4 <= intensity < 0.7:
        return True, "EXPLORE", "Curious Awakening"
        
    if intensity >= 0.7:
        return True, "SCAN", "Peak Vitality"
        
    return False, "IDLE", "Unclear Signal"

def adjust_metabolism(meta, did_act, intensity):
    """
    Homeostasis: Adjusts breathing rate based on activity.
    - If she acted vigorously, she needs more rest (slower period).
    - If she rested too long, she becomes eager (faster period).
    """
    if did_act:
        # Exhaustion: Slow down the next cycle slightly
        meta["period_minutes"] = min(120, meta["period_minutes"] + 2)
        # Deplete some amplitude temporarily? No, let's keep amplitude stable as "health"
    else:
        # Eager: Speed up the next cycle slightly if idle
        if intensity < 0.2:
            meta["period_minutes"] = max(15, meta["period_minutes"] - 1)
            
    return meta

def main():
    meta = load_metabolism()
    
    # 1. Where are we in the breath?
    phase = calculate_breath_phase(meta)
    
    # 2. How strong is the urge?
    intensity = get_sinusoidal_intensity(phase, meta["amplitude"])
    
    # 3. Should we act?
    should_act, action_type, reason = decide_action_from_intensity(intensity, meta)
    
    # 4. Reset cycle if we just finished one (Phase wraps around naturally via modulo, 
    # but we update start_time if we want explicit logging)
    # Actually, the modulo handles the wrap. We just need to know if we crossed 0.9->0.1
    
    # Detect Cycle Completion for stats
    prev_phase = meta.get("last_phase", 0.0)
    if prev_phase > 0.8 and phase < 0.2:
        meta["total_cycles_completed"] += 1
        # Optional: Log completion
        
    meta["last_phase"] = phase
    
    # 5. Adjust Physiology
    meta = adjust_metabolism(meta, should_act, intensity)
    
    # Save State
    save_metabolism(meta)
    
    # Output for YAML
    output = {
        "phase": round(phase, 3),
        "intensity": intensity,
        "should_act": str(should_act).lower(),
        "action": action_type,
        "reason": reason,
        "period_minutes": meta["period_minutes"],
        "cycles_done": meta["total_cycles_completed"]
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
