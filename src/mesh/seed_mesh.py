# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
# Affiliation: PSIVI Research
#
# Mesh Seeder - RFC 1001 Compliant
# Converts existing JSON memories into .psvc containers.

import os
import json
import datetime
import numpy as np
from pathlib import Path

from psvc_reference import (
    encode_text, write_file, content_hash,
    PRECISION_INT8
)

print("=== SEEDING MESH (RFC 1001 COMPLIANT) ===")

CONTAINER_DIR = Path("reports/pico_containers")
CONTAINER_DIR.mkdir(parents=True, exist_ok=True)

# Find existing JSON memories
json_files = list(Path("reports").glob("*memory.json"))

if not json_files:
    print("[SEED] No JSON memories found. Creating seed vector.")
    seed_text = "PSIVI Mesh Pico AI initialization vector. Goldstream Watershed, Langford BC."
    vector = encode_text(seed_text)
    chash = content_hash(vector)
    output_path = CONTAINER_DIR / f"seed_{chash}.psvc"
    
    write_file(vector, output_path, precision=PRECISION_INT8)
    
    sidecar_path = output_path.with_suffix('.json')
    with open(sidecar_path, 'w') as f:
        json.dump({
            "text": seed_text,
            "agent": "seeder",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "type": "seed"
        }, f, indent=2)
    
    print(f"[SEED] Seeded: {output_path.name}")
else:
    sealed_count = 0
    for json_file in json_files:
        try:
            with open(json_file) as f:
                data = json.load(f)
            
            text = data.get("text", "")
            if not text:
                continue
            
            # Encode using canonical library
            vector = encode_text(text)
            chash = content_hash(vector)
            output_path = CONTAINER_DIR / f"{chash}.psvc"
            
            write_file(vector, output_path, precision=PRECISION_INT8)
            
            # Write sidecar
            sidecar_path = output_path.with_suffix('.json')
            with open(sidecar_path, 'w') as f:
                json.dump({
                    "text": text,
                    "agent": data.get("agent", "unknown"),
                    "timestamp": data.get("timestamp", datetime.datetime.utcnow().isoformat()),
                    "type": "memory"
                }, f, indent=2)
            
            sealed_count += 1
            print(f"[SEED] Sealed: {json_file.name} -> {output_path.name}")
            
        except Exception as e:
            print(f"[SEED] Skipped {json_file.name}: {e}")
    
    print(f"[SEED] Complete. Sealed {sealed_count} containers.")
