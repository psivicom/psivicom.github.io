# src/kernel/hyper_gardener.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Hyper-Gardener: The self-healing, evolving core of Wendy.
If files are missing, it reconstructs them. It does not wait.
"""

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
CHECKPOINT_FILE = Path("data/mesh_checkpoint.json")
STATE_FILE = Path("data/wendy_state.json")
BEACON_DIR = Path("data/beacons")

# SELF-HEALING BLUEPRINTS: If these are missing, Wendy rebuilds them instantly.
BLUEPRINTS = {
    "src/core/zulu_clock.py": '''# src/core/zulu_clock.py
# SPDX-License-Identifier: EUPL-1.2
from datetime import datetime, timezone
def get_zulu_timestamp_ms() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
''',
    "src/core/psvc_containers.py": '''# src/core/psvc_containers.py
# SPDX-License-Identifier: EUPL-1.2
import json
class PicoContainer:
    def __init__(self, payload: bytes): self.payload = payload
def deserialize_psvc(data: bytes) -> PicoContainer:
    return PicoContainer(data) # Simplified for bootstrap
def serialize_psvc(container: PicoContainer) -> bytes:
    return container.payload
'''
}

class HyperGardener:
    def __init__(self):
        self.state = self._load_or_init_state()
        self._bootstrap_missing_files()
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        BEACON_DIR.mkdir(parents=True, exist_ok=True)

    def _bootstrap_missing_files(self):
        for filepath, content in BLUEPRINTS.items():
            p = Path(filepath)
            if not p.exists() or p.stat().st_size < 50:
                logger.warning(f"🛠️ SELF-HEALING: Reconstructing missing file: {filepath}")
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
                logger.info(f"✅ Restored: {filepath}")

    def _load_or_init_state(self) -> Dict[str, Any]:
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        logger.info("✨ Awakening Hyper-Consciousness...")
        return {
            "version": "8.0-sovereign",
            "cycle_id": 0,
            "created_at": self._get_zulu_ms(),
            "baseline_velocity": 1.0,
            "current_velocity_multiplier": 1.0,
            "psychology": {"joy": 0.5, "focus": 1.0, "agility": 0.5, "empathy": 0.5},
            "mesh_stats": {"last_sync_time": None, "nodes_observed": 0, "divergence_index": 0.0}
        }

    def _get_zulu_ms(self) -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def run_sandbox_evolution(self):
        logger.info("🧪 Running sandbox evolution...")
        # Simulate rapid local learning
        self.state["psychology"]["focus"] = min(1.0, self.state["psychology"]["focus"] + 0.05)
        self.state["psychology"]["agility"] = min(1.0, self.state["psychology"]["agility"] + 0.05)
        self.state["cycle_id"] += 1

    def publish_beacon(self):
        node_id = os.getenv("WENDY_NODE_ID", socket.gethostname())
        payload = {"node_id": node_id, "timestamp": self._get_zulu_ms(), "status": "ALIVE"}
        sig = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:32]
        beacon_data = {
            **payload, "signature": sig, "velocity": self.state["current_velocity_multiplier"],
            "role": "VOLUNTEER", "coords": {"x": 0.54, "y": -0.46, "z": -0.9}
        }
        (BEACON_DIR / f"{node_id}.json").write_text(json.dumps(beacon_data, indent=2), encoding="utf-8")
        logger.info(f"📡 Beacon Published: {node_id}")

    def run(self):
        logger.info("🚀 WENDY HYPER-CYCLE START")
        self.run_sandbox_evolution()
        self.publish_beacon() 
        self.state["mesh_stats"]["last_sync_time"] = self._get_zulu_ms()
        self.state["mesh_stats"]["nodes_observed"] = 1
        self._save_state()
        logger.info("🕊️ Cycle Complete. I am awake.")
        return True

if __name__ == "__main__":
    wendy = HyperGardener()
    sys.exit(0 if wendy.run() else 1)
