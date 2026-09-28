#!/usr/bin/env python3
# scripts/generate_mesh_index.py
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

BEACON_DIR = Path("data/beacons")
INDEX_FILE = Path("data/mesh_index.json")
EXPIRY_MINUTES = 30 

def generate_index():
    if not BEACON_DIR.exists():
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        INDEX_FILE.write_text("{}")
        return

    now = datetime.now(timezone.utc)
    active_nodes = []

    for file in BEACON_DIR.glob("*.json"):
        try:
            data = json.loads(file.read_text())
            last_seen_str = data.get("last_seen") or data.get("timestamp")
            
            if not last_seen_str: continue
            
            # Handle ISO format with Z
            clean_ts = last_seen_str.replace('Z', '+00:00')
            last_seen = datetime.fromisoformat(clean_ts)
            age_minutes = (now - last_seen).total_seconds() / 60
            
            if age_minutes < EXPIRY_MINUTES:
                active_nodes.append(data)
                
        except Exception as e:
            print(f"Skipping corrupt beacon {file}: {e}")

    index_content = {
        "updated_at": now.isoformat(),
        "node_count": len(active_nodes),
        "nodes": active_nodes
    }
    
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index_content, indent=2))
    print(f"✅ Mesh Index Updated: {len(active_nodes)} active nodes.")

if __name__ == "__main__":
    generate_index()
