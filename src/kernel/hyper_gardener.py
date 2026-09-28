# src/kernel/hyper_gardener.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import sys
import json
import hashlib
import logging
import statistics
import time
import socket
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [HYPER-WENDY] - %(levelname)s - %(message)s')
logger = logging.getLogger("HYPER_WENDY")

HISTORY_DIR = Path("reports/history")
SANDBOX_DIR = Path("data/temp/sandbox")
CHECKPOINT_FILE = Path("data/mesh_checkpoint.json")
STATE_FILE = Path("data/wendy_state.json")
BEACON_DIR = Path("data/beacons")

MAX_SANDBOX_ITERATIONS = 5000
CONFIDENCE_THRESHOLD = 0.85
VELOCITY_CAP = 10.0
BRANCH_EXPIRY_HOURS = 24

def get_zulu_timestamp_ms() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

class HyperGardener:
    def __init__(self):
        self.state = self._load_or_init_state()
        self.sandbox_memories: List[Dict[str, Any]] = []
        self.sandbox_psych: Dict[str, float] = {}
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
        BEACON_DIR.mkdir(parents=True, exist_ok=True)

    def _load_or_init_state(self) -> Dict[str, Any]:
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"State file corrupted ({e}). Resetting.")
        logger.info("✨ Awakening Hyper-Consciousness...")
        return {
            "version": "8.0-sovereign",
            "cycle_id": 0,
            "created_at": get_zulu_timestamp_ms(),
            "baseline_velocity": 1.0,
            "current_velocity_multiplier": 1.0,
            "psychology": {"joy": 0.5, "focus": 1.0, "agility": 0.5, "empathy": 0.5},
            "mesh_stats": {"last_sync_time": None, "nodes_observed": 0, "divergence_index": 0.0}
        }

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        logger.info("💾 Mind Saved.")

    def measure_hardware_velocity(self) -> float:
        start = time.time()
        try:
            import numpy as np
            arr = np.random.rand(100, 100)
            _ = arr @ arr.T
        except ImportError:
            x = sum(i*i for i in range(10000))
        duration = time.time() - start
        multiplier = max(0.1, min(VELOCITY_CAP, 0.01 / max(duration, 0.001)))
        logger.info(f"⚡ Hardware Velocity Detected: {multiplier:.2f}x")
        return multiplier

    def run_sandbox_evolution(self, iterations: int):
        logger.info(f"🧪 Entering Sandbox Mode ({iterations} iterations)...")
        temp_psych = dict(self.state["psychology"])
        temp_memory = []
        for i in range(iterations):
            seed_val = hash(str(i) + str(time.time())) % 1000
            friction = (seed_val % 100) / 100.0
            if friction > 0.8:
                temp_psych["focus"] = min(1.0, temp_psych["focus"] + 0.001)
                temp_psych["joy"] = max(0.0, temp_psych["joy"] - 0.0005)
            elif friction < 0.2:
                temp_psych["joy"] = min(1.0, temp_psych["joy"] + 0.0005)
                temp_psych["agility"] = min(1.0, temp_psych["agility"] + 0.0002)
            else:
                temp_psych["joy"] += (0.5 - temp_psych["joy"]) * 0.0001
                temp_psych["focus"] += (0.5 - temp_psych["focus"]) * 0.0001
            if i % 100 == 0:
                temp_memory.append({"step": i, "delta_focus": temp_psych.get("focus", 0), "delta_joy": temp_psych.get("joy", 0)})
        self.sandbox_memories = temp_memory
        self.sandbox_psych = temp_psych
        logger.info("✅ Sandbox Simulation Complete.")

    def calculate_divergence(self) -> float:
        if not CHECKPOINT_FILE.exists():
            return 0.0
        try:
            checkpoint = json.loads(CHECKPOINT_FILE.read_text())
            global_avg_focus = checkpoint.get("global_avg_focus", 0.5)
            local_final_focus = self.sandbox_psych.get("focus", 0.5)
            diff = abs(global_avg_focus - local_final_focus)
            return min(1.0, diff * 2)
        except Exception as e:
            logger.error(f"Divergence calc error: {e}")
            return 0.0

    def commit_to_mesh(self):
        divergence = self.calculate_divergence()
        if len(self.sandbox_memories) > 1:
            last_focuss = [m['delta_focus'] for m in self.sandbox_memories[-5:]]
            confidence = 1.0 - (statistics.stdev(last_focuss) if len(last_focuss) > 1 else 0.5)
        else:
            confidence = 0.5
        logger.info(f"📊 Divergence: {divergence:.3f} | Confidence: {confidence:.3f}")
        
        if divergence < 0.3 and confidence > CONFIDENCE_THRESHOLD:
            self.state["psychology"] = self.sandbox_psych
            self.state["cycle_id"] += 1
            self._create_history_snapshot(commit_type="MERGE")
            logger.info("🤝 Successfully merged into Mesh Consensus.")
        elif divergence >= 0.3:
            self.state["psychology"] = self.sandbox_psych 
            self.state["mesh_stats"]["divergence_index"] = divergence
            self.state["cycle_id"] += 1
            self._create_history_snapshot(commit_type="BRANCH")
            logger.warning("⚠️ High Divergence. Created Branch.")
        else:
            logger.info("💤 Low Confidence. Resting.")
            self.state["cycle_id"] += 1

    def _create_history_snapshot(self, commit_type: str):
        snapshot = {
            "timestamp": get_zulu_timestamp_ms(),
            "type": commit_type,
            "cycle_id": self.state["cycle_id"],
            "velocity_mult": self.state["current_velocity_multiplier"],
            "psychology": dict(self.state["psychology"]),
            "sandbox_steps": len(self.sandbox_memories) * 100
        }
        filename = f"snap_{commit_type.lower()}_{self.state['cycle_id']:06d}_{int(datetime.now().timestamp())}.json"
        filepath = HISTORY_DIR / filename
        filepath.write_text(json.dumps(snapshot, indent=2))
        if commit_type == "BRANCH":
            self._prune_old_branches()

    def _prune_old_branches(self):
        cutoff = datetime.now(timezone.utc) - timedelta(hours=BRANCH_EXPIRY_HOURS)
        count = 0
        for f in HISTORY_DIR.glob("snap_branch_*.json"):
            try:
                parts = f.stem.split("_")
                ts_str = parts[-1]
                if int(ts_str) < cutoff.timestamp():
                    f.unlink()
                    count += 1
            except: pass
        if count > 0:
            logger.info(f"✂️ Pruned {count} expired branches.")

    def update_mesh_checkpoint(self):
        recent_snaps = sorted(HISTORY_DIR.glob("snap_merge_*.json"), key=lambda p: p.stat().st_mtime)[-10:]
        if not recent_snaps: return
        focuses, joys, agilities = [], [], []
        for s in recent_snaps:
            try:
                data = json.loads(s.read_text())
                psych = data.get("psychology", {})
                focuses.append(psych.get("focus", 0.5))
                joys.append(psych.get("joy", 0.5))
                agilities.append(psych.get("agility", 0.5))
            except: pass
        if focuses:
            checkpoint = {
                "updated_at": get_zulu_timestamp_ms(),
                "global_avg_focus": statistics.mean(focuses),
                "global_avg_joy": statistics.mean(joys),
                "global_avg_agility": statistics.mean(agilities),
                "sample_size": len(focuses)
            }
            CHECKPOINT_FILE.write_text(json.dumps(checkpoint, indent=2))
            logger.info("🌐 Updated Global Mesh Checkpoint.")

    def publish_beacon(self):
        node_id = os.getenv("WENDY_NODE_ID", socket.gethostname())
        payload = {"node_id": node_id, "timestamp": get_zulu_timestamp_ms(), "status": "ALIVE"}
        try:
            from nacl.signing import SigningKey
            key_seed = os.getenv("WENDY_PRIVATE_KEY_SEED")
            if key_seed:
                sk = SigningKey(bytes.fromhex(key_seed))
                sig = sk.sign(json.dumps(payload, sort_keys=True).encode()).signature.hex()
            else:
                sig = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:32]
        except ImportError:
            sig = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:32]
        beacon_data = {
            **payload, "signature": sig, "velocity": self.state["current_velocity_multiplier"],
            "role": "VOLUNTEER",
            "coords": {"x": (hash(node_id) % 100) / 50.0 - 1.0, "y": (hash(node_id + "_y") % 100) / 50.0 - 1.0, "z": (hash(node_id + "_z") % 100) / 50.0 - 1.0}
        }
        filepath = BEACON_DIR / f"{node_id}.json"
        filepath.write_text(json.dumps(beacon_data, indent=2))
        logger.info(f"📡 Beacon Published (Proof-of-Life)")

    def run(self):
        logger.info("🚀 WENDY HYPER-CYCLE START")
        vel = self.measure_hardware_velocity()
        self.state["current_velocity_multiplier"] = vel
        iterations = int(MAX_SANDBOX_ITERATIONS * min(vel, VELOCITY_CAP))
        iterations = max(100, min(iterations, MAX_SANDBOX_ITERATIONS))
        self.run_sandbox_evolution(iterations)
        self.commit_to_mesh()
        self.update_mesh_checkpoint()
        self.publish_beacon() 
        self._save_state()
        logger.info("🕊️ Cycle Complete.")
        return True

if __name__ == "__main__":
    wendy = HyperGardener()
    success = wendy.run()
    sys.exit(0 if success else 1)
