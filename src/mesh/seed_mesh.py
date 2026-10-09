# src/mesh/mesh_seeder.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Mesh Seeder: RFC 1001 Compliant
Converts existing JSON memories into cryptographically sovereign .psvc containers.
"""

import json
import logging
import numpy as np
from pathlib import Path

from src.core.psvc_reference import write_file, content_hash, PRECISION_FLOAT32
from src.core.zulu_clock import get_zulu_timestamp_ms

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("MESH_SEEDER")

CONTAINER_DIR = Path("reports/pico_containers")
CONTAINER_DIR.mkdir(parents=True, exist_ok=True)

def seed_mesh():
    json_files = list(Path("reports").glob("*memory.json"))
    
    if not json_files:
        logger.info("[SEED] No JSON memories found. Creating sovereign seed vector.")
        seed_text = "PSIVI Mesh Pico AI initialization vector. Goldstream Watershed, Langford BC."
        
        # Enforce float32 precision
        vector = np.array([ord(c) for c in seed_text], dtype=np.float32)
        chash = content_hash(vector)
        output_path = CONTAINER_DIR / f"seed_{chash}.psvc"
        
        write_file(vector, output_path, precision=PRECISION_FLOAT32)
        
        sidecar_path = output_path.with_suffix('.json')
        sidecar_path.write_text(json.dumps({
            "text": seed_text,
            "agent": "seeder",
            "timestamp": get_zulu_timestamp_ms(),
            "type": "seed"
        }, indent=2), encoding="utf-8")
        
        logger.info(f"[SEED] Seeded: {output_path.name}")
    else:
        sealed_count = 0
        for json_file in json_files:
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                text = data.get("text", "")
                if not text:
                    continue
                
                vector = np.array([ord(c) for c in text], dtype=np.float32)
                chash = content_hash(vector)
                output_path = CONTAINER_DIR / f"{chash}.psvc"
                
                write_file(vector, output_path, precision=PRECISION_FLOAT32)
                
                sidecar_path = output_path.with_suffix('.json')
                sidecar_path.write_text(json.dumps({
                    "text": text,
                    "agent": data.get("agent", "unknown"),
                    "timestamp": get_zulu_timestamp_ms(),
                    "type": "memory"
                }, indent=2), encoding="utf-8")
                
                sealed_count += 1
                logger.info(f"[SEED] Sealed: {json_file.name} -> {output_path.name}")
            except Exception as e:
                logger.error(f"[SEED] Skipped {json_file.name}: {e}")
        
        logger.info(f"[SEED] Complete. Sealed {sealed_count} containers.")

if __name__ == "__main__":
    seed_mesh()
