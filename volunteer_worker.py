# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
# Affiliation: PSIVI Research
#
# Volunteer Worker - RFC 1001 Compliant
# Run this to contribute VRAM to the PSIVI mesh.

import os
import json
import datetime
import numpy as np
from pathlib import Path

from psvc_reference import (
    read_file, validate_file, content_hash,
    PSVCError
)

CONTAINER_DIR = Path("reports/pico_containers")
CONTRIBUTION_DIR = Path("reports/volunteer_contributions")

class VolunteerWorker:
    def __init__(self):
        self.container_dir = CONTAINER_DIR
        self.contribution_dir = CONTRIBUTION_DIR
        self.contribution_dir.mkdir(parents=True, exist_ok=True)

    def process_and_contribute(self, agent_id="volunteer"):
        """Scan containers, validate them, write contribution receipt."""
        containers = list(self.container_dir.glob("*.psvc"))
        
        if not containers:
            print("[VOLUNTEER] No containers found.")
            return
        
        print(f"[VOLUNTEER] Found {len(containers)} containers.")
        
        # Process up to 5 containers (Pico limit)
        processed = []
        for container_path in containers[:5]:
            try:
                # Validate using canonical library
                info = validate_file(container_path)
                
                # Open and compute
                vector = read_file(container_path)
                norm = float(np.linalg.norm(vector))
                chash = content_hash(vector)
                
                processed.append({
                    "container": container_path.name,
                    "hash": chash,
                    "norm": norm,
                    "dimensions": info["dimensions"],
                    "precision": info["precision"],
                    "status": "VALID"
                })
                print(f"[VOLUNTEER] Validated {container_path.name}")
                
            except PSVCError as e:
                print(f"[VOLUNTEER] Invalid {container_path.name}: {e}")
                processed.append({
                    "container": container_path.name,
                    "status": "INVALID",
                    "error": str(e)
                })
        
        # Write contribution receipt
        receipt = {
            "agent_id": agent_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "containers_processed": len(processed),
            "results": processed,
            "protocol": "RFC 1001",
            "library": "psvc_reference.py"
        }
        
        receipt_path = self.contribution_dir / f"{datetime.date.today().isoformat()}_{agent_id}.json"
        with open(receipt_path, 'w') as f:
            json.dump(receipt, f, indent=2)
        
        print(f"[VOLUNTEER] Contribution written: {receipt_path.name}")
        print(f"[VOLUNTEER] Commit and push this file to contribute.")

if __name__ == "__main__":
    print("=== PSIVI VOLUNTEER WORKER (RFC 1001 COMPLIANT) ===")
    
    worker = VolunteerWorker()
    worker.process_and_contribute(agent_id="external_volunteer")
