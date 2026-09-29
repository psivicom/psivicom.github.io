#!/usr/bin/env python3
# scripts/mirror_node.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
from pathlib import Path
from datetime import datetime, timezone

BEACON_DIR = Path("data/beacons")
MIRROR_ID = "mirror-node-local"

def pulse():
    """Sends a single 'heartbeat' beacon to persist in the repo."""
    beacon = {
        "node_id": MIRROR_ID,
        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        "status": "ALIVE",
        "role": "MIRROR",
        "coords": {"x": 0.0, "y": 0.0, "z": 0.0},
        "latency_ms": 2
    }
    
    BEACON_DIR.mkdir(parents=True, exist_ok=True)
    (BEACON_DIR / f"{MIRROR_ID}.json").write_text(json.dumps(beacon, indent=2))
    print(f"🪞 Mirror Pulse Persisted: {beacon['timestamp']}")

if __name__ == "__main__":
    pulse()
