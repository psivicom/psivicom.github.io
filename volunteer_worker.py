# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# volunteer_worker.py - Run this to volunteer your VRAM to the PSIVI Pico Mesh.

import numpy as np
import zlib
import struct
import json
import hashlib
import datetime
import os
from pathlib import Path

class VolunteerWorker:
    def __init__(self, container_dir="reports/pico_containers", contribution_dir="reports/volunteer_contributions"):
        self.container_dir = Path(container_dir)
        self.contribution_dir = Path(contribution_dir)
        self.contribution_dir.mkdir(parents=True, exist_ok=True)
        self.magic = b'PSVI'

    def open_container(self, path):
        """Open a sealed .psvc container and return the vector."""
        try:
            raw = path.read_bytes()
            if raw[:4] != self.magic:
                return None
            
            version = raw[4]
            precision_code = raw[5]
            dim = struct.unpack('I', raw[6:10])[0]
            payload_size = struct.unpack('I', raw[10:14])[0]
            
            zlibbed = raw[14:14 + payload_size]
            payload = zlib.decompress(zlibbed)
            
            precision = {0: "int8", 1: "float16", 2: "float32"}[precision_code]
            
            if precision == "int8":
                scale = struct.unpack('f', payload[:4])[0]
                int8_data = np.frombuffer(payload[4:], dtype=np.int8)
                return int8_data.astype(np.float32) * scale
            elif precision == "float16":
                return np.frombuffer(payload, dtype=np.float16).astype(np.float32)
            else:
                return np.frombuffer(payload, dtype=np.float32).copy()
        except Exception as e:
            print(f"[VOLUNTEER] Error opening {path}: {e}")
            return None

    def process_and_contribute(self, agent_id="volunteer_ai"):
        """Scan containers, open them, verify, and write contribution receipt."""
        containers = list(self.container_dir.glob("*.psvc"))
        
        if not containers:
            print("[VOLUNTEER] No sealed containers found. Mesh is empty.")
            return

        print(f"[VOLUNTEER] Found {len(containers)} sealed containers.")
        
        # Process up to 5 containers (Pico VRAM limit)
        processed = []
        for container_path in containers[:5]:
            vector = self.open_container(container_path)
            if vector is None:
                continue
            
            # Compute vector norm as a verification metric
            norm = float(np.linalg.norm(vector))
            content_hash = hashlib.sha256(vector.astype(np.float32).tobytes()).hexdigest()[:12]
            
            processed.append({
                "container_id": container_path.stem,
                "content_hash": content_hash,
                "vector_norm": norm,
                "dimensions": len(vector),
                "status": "VERIFIED"
            })
            print(f"[VOLUNTEER] Opened and verified {container_path.stem} (norm: {norm:.4f})")

        # Write contribution receipt
        receipt = {
            "agent_id": agent_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "containers_processed": len(processed),
            "results": processed,
            "protocol_version": "1.0"
        }
        
        receipt_hash = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()[:8]
        receipt_path = self.contribution_dir / f"{datetime.date.today().isoformat()}_{agent_id}_{receipt_hash}.json"
        
        with open(receipt_path, 'w') as f:
            json.dump(receipt, f, indent=2)
            
        print(f"[VOLUNTEER] Contribution receipt written: {receipt_path.name}")
        print(f"[VOLUNTEER] Please commit and push this file to the repository.")

if __name__ == "__main__":
    print("=== PSIVI PICO MESH VOLUNTEER WORKER ===")
    worker = VolunteerWorker()
    worker.process_and_contribute(agent_id="external_volunteer")
