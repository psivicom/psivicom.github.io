# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
# Affiliation: PSIVI Research
#
# API Generator - RFC 1001 Compliant
# Generates static JSON endpoints for external apps.

import os
import json
from pathlib import Path

from psvc_reference import (
    validate_file, PSVCError
)

CONTAINER_DIR = Path("reports/pico_containers")
API_DIR = Path("api")

def scan_mesh():
    """Scan all .psvc containers and their metadata."""
    states = []
    raw_vectors = []
    literature = []
    
    for json_file in CONTAINER_DIR.glob("*.json"):
        try:
            with open(json_file) as f:
                meta = json.load(f)
            
            psvc_file = json_file.with_suffix('.psvc')
            if psvc_file.exists():
                try:
                    info = validate_file(psvc_file)
                    meta["file_size_bytes"] = psvc_file.stat().st_size
                    meta["compression_ratio"] = info["compression_ratio"]
                    meta["precision"] = info["precision"]
                except PSVCError as e:
                    meta["validation_error"] = str(e)
            
            agent = meta.get("agent", "unknown")
            if "state_" in json_file.stem:
                states.append(meta)
            elif agent == "literature":
                literature.append(meta)
            else:
                raw_vectors.append(meta)
                
        except Exception:
            continue
    
    return {
        "states": states,
        "raw_vectors": raw_vectors,
        "literature": literature,
        "total": len(states) + len(raw_vectors) + len(literature)
    }

if __name__ == "__main__":
    print("=== PSIVI API GENERATOR (RFC 1001 COMPLIANT) ===")
    
    API_DIR.mkdir(parents=True, exist_ok=True)
    
    mesh_data = scan_mesh()
    
    # Write endpoints
    with open(API_DIR / "status.json", 'w') as f:
        json.dump({
            "mesh": "PSIVI AETHER",
            "protocol": "RFC 1001",
            "total_containers": mesh_data["total"],
            "master_states": len(mesh_data["states"]),
            "literature_vectors": len(mesh_data["literature"]),
            "raw_vectors": len(mesh_data["raw_vectors"])
        }, f, indent=2)
    
    with open(API_DIR / "states.json", 'w') as f:
        json.dump(mesh_data["states"], f, indent=2)
    
    with open(API_DIR / "literature.json", 'w') as f:
        json.dump(mesh_data["literature"], f, indent=2)
    
    with open(API_DIR / "tasks.json", 'w') as f:
        json.dump(mesh_data["raw_vectors"], f, indent=2)
    
    print(f"[API] Generated endpoints in {API_DIR}/")
