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
from datetime import datetime, timezone, timedelta

GITHUB_REPO = os.getenv("GITHUB_REPOSITORY", "psivicom/psivicom.github.io")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
STATE_FILE = Path("data/wendy_state.json")
METABOLISM_FILE = Path("src/wendy_metabolism.json")
CHECKPOINT_FILE = Path("data/mesh_checkpoint.json")

def log(msg: str):
    print(f"[{get_zulu_timestamp_ms()}] {msg}", file=sys.stderr)

def get_zulu_timestamp_ms() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def load_local_state() -> dict:
    if METABOLISM_FILE.exists():
        try:
            return json.loads(METABOLISM_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return {
                "cycle_start_time": state.get("created_at", get_zulu_timestamp_ms()),
                "period_minutes": 60,
                "amplitude": state.get("current_velocity_multiplier", 0.5),
                "last_intensity": 0.0,
                "total_cycles_completed": state.get("cycle_id", 0),
                "spawned_agents": [],
                "last_known_checkpoint": {}
            }
        except Exception:
            pass
    return {
        "cycle_start_time": get_zulu_timestamp_ms(),
        "period_minutes": 60,
        "amplitude": 0.8,
        "last_intensity": 0.0,
        "total_cycles_completed": 0,
        "spawned_agents": [],
        "last_known_checkpoint": {}
    }

def save_metabolism(meta: dict):
    METABOLISM_FILE.parent.mkdir(parents=True, exist_ok=True)
    METABOLISM_FILE.write_text(json.dumps(meta, indent=2), encoding="utf-8")

def calculate_breath_phase(meta: dict) -> float:
    start_str = meta.get("cycle_start_time", get_zulu_timestamp_ms())
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
    elapsed_seconds = max(0.0, (now - start_time).total_seconds()) 
    period_seconds = meta.get("period_minutes", 60) * 60
    return round((elapsed_seconds % period_seconds) / period_seconds, 6)

def get_sinusoidal_intensity(phase: float, amplitude: float) -> float:
    raw_energy = math.sin(math.pi * phase)
    intensity = raw_energy * amplitude
    jitter = random.uniform(-0.02, 0.02)
    return round(max(0.0, min(1.0, intensity + jitter)), 6) 

def decide_action(intensity: float, meta: dict) -> tuple:
    if intensity < 0.2:
        return False, "IDLE", "Deep Rest (Local Sync)"
    elif 0.2 <= intensity < 0.5:
        return True, "MAINTAIN", "Refreshing local documentation cache."
    elif 0.5 <= intensity < 0.8:
        return True, "EXPLORE", "Curiosity piqued. Running local sandbox."
    else:
        return True, "SCAN", "Peak Vitality. Preparing hyper-gardener burst."

def main():
    meta = load_local_state()
    phase = calculate_breath_phase(meta)
    intensity = get_sinusoidal_intensity(phase, meta.get("amplitude", 0.5))
    should_act, action_type, reason = decide_action(intensity, meta)
    
    if should_act:
        meta["period_minutes"] = min(120, meta.get("period_minutes", 60) + 2)
        meta["total_cycles_completed"] = meta.get("total_cycles_completed", 0) + 1
    else:
        if intensity < 0.2:
            meta["period_minutes"] = max(15, meta.get("period_minutes", 60) - 1)
            
    meta["last_intensity"] = intensity
    meta["last_phase"] = phase
    save_metabolism(meta)
    
    output = {
        "phase": phase,
        "intensity": intensity,
        "should_act": str(should_act).lower(),
        "action": action_type,
        "reason": reason,
        "period_minutes": meta.get("period_minutes", 60),
        "cycles_done": meta.get("total_cycles_completed", 0),
        "spawned_agents": meta.get("spawned_agents", []),
        "utc_now": get_zulu_timestamp_ms(),
        "latency_mode": "local-first"
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
