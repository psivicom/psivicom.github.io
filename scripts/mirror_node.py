#!/usr/bin/env python3
# scripts/mirror_node.py
# SPDX-License-Identifier: EUPL-1.2

import json
import time
from pathlib import Path
from datetime import datetime, timezone

BEACON_DIR = Path("data/beacons")
MIRROR_ID = "mirror-node-local"

def pulse():
    """Sends a 'heartbeat' beacon to trick Wendy into seeing a cluster."""
    while True:
        beacon = {
            "node_id": MIRROR_ID,
            "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            "status": "ALIVE",
            "role": "MIRROR",
            "coords": {"x": 0.0, "y": 0.0, "z": 0.0}, # Localhost
            "latency_ms": 2 # Ultra-low latency to boost her health score
        }
        
        BEACON_DIR.mkdir(exist_ok=True)
        (BEACON_DIR / f"{MIRROR_ID}.json").write_text(json.dumps(beacon, indent=2))
        
        print(f"🪞 Mirror Pulse: {beacon['timestamp']}")
        time.sleep(60) # Pulse every minute

if __name__ == "__main__":
    print("🪞 Mirror Node Active. Broadcasting presence to Wendy...")
    pulse()
