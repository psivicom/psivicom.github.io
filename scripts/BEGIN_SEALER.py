# scripts/BEGIN_SEALER.py
"""
PSIVI AETHER Mesh — Instruction Sealer (BEGIN_SEALER.py)
Location: /scripts/BEGIN_SEALER.py

Creates RFC 1001 compliant .psvc + .json instruction pairs.
Reads configuration from ENV vars set by GitHub Actions.
"""

import json
import struct
import zlib
from pathlib import Path
from datetime import datetime, timezone
import sys
import os
import numpy as np

MAGIC = b'PSVI'
VERSION = 1
PRECISION_FLOAT32 = 2
OUTPUT_DIR = Path("data/instruction_queue")

def get_zulu_time_ms() -> str:
    now_utc = datetime.now(timezone.utc)
    return f"{now_utc.strftime('%Y-%m-%dT%H:%M:%S.')}{now_utc.microsecond // 1000:03d}Z"

def seal_instruction(command: str, params: dict, source: str = "workflow_seed"):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    ts_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:-3]
    iso_ts = get_zulu_time_ms()
    filename_base = f"instruction_{command}_{ts_str}"
    
    sidecar_data = {
        "command": command,
        "params": params,
        "source": source,
        "timestamp": iso_ts,
        "rfc1001_compliant": True
    }
    
    sidecar_path = OUTPUT_DIR / f"{filename_base}.json"
    with open(sidecar_path, 'w') as f:
        json.dump(sidecar_data, f, indent=2)
        
    intent_vector = np.random.randn(4096).astype(np.float32)
    intent_vector /= np.linalg.norm(intent_vector)
    
    vector_bytes = intent_vector.tobytes()
    compressed = zlib.compress(vector_bytes, level=9)
    
    header = MAGIC
    header += struct.pack('B', VERSION)
    header += struct.pack('B', PRECISION_FLOAT32)
    header += struct.pack('<I', len(intent_vector))
    header += struct.pack('<I', len(compressed))
    
    psvc_path = OUTPUT_DIR / f"{filename_base}.psvc"
    psvc_path.write_bytes(header + compressed)
    
    print(f"   Sealed: {psvc_path.name}")
    return str(psvc_path), str(sidecar_path)

def main():
    command_type = os.getenv("COMMAND_TYPE", "spawn_agent")
    template_name = os.getenv("TEMPLATE_NAME", "satellite_observer")
    target_region = os.getenv("TARGET_REGION", "Goldstream_Watershed")
    gene_focus = os.getenv("GENE_FOCUS", "IGFBP7")
    
    try:
        if command_type == "spawn_agent":
            if template_name == "literature_resolver":
                params = {
                    "template_name": template_name,
                    "agent_name": f"resolve_{gene_focus.lower()}_{datetime.now().strftime('%H%M%S')}",
                    "config": {
                        "gene": gene_focus,
                        "organism": "Mus_musculus", # Default mock
                        "context": "Spaceflight_Biology_OSDR"
                    }
                }
            else:
                params = {
                    "template_name": template_name,
                    "agent_name": f"{template_name}_seed_{datetime.now().strftime('%H%M%S')}",
                    "config": {
                        "target_region": target_region,
                        "modality": "RADARSAT_SAR",
                        "priority": "HIGH"
                    }
                }
            
            seal_instruction("spawn_agent", params)
            
        elif command_type == "request_report":
            seal_instruction("request_report", {
                "topic": "Initial Mesh Health Check",
                "format": "JSON"
            })
            
        else:
            raise ValueError(f"Unknown command: {command_type}")
            
        print("✅ Sealing Complete.")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
