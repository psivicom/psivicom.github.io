# scripts/BEGIN_SEALER.py
"""
PSIVI AETHER Mesh — Instruction Sealer (BEGIN_SEALER.py)
Location: /scripts/BEGIN_SEALER.py

This script is used by EXTERNAL AI agents (or local developers) to CREATE
and DROP instructions into the mesh queue. It does NOT process them.

Protocol: RFC 1001 Compliant
License: EUPL-1.2
Author: Louis-Philippe Audette (2026)
"""

import json
import struct
import zlib
from pathlib import Path
from datetime import datetime, timezone
import sys
import os
import numpy as np

# --- CONFIGURATION ---
MAGIC = b'PSVI'
VERSION = 1
PRECISION_FLOAT32 = 2
OUTPUT_DIR = Path("data/instruction_queue")

def get_zulu_time_ms() -> str:
    """Returns current UTC time in ISO 8601 Zulu format with milliseconds."""
    now_utc = datetime.now(timezone.utc)
    base_format = now_utc.strftime("%Y-%m-%dT%H:%M:%S.")
    millis_part = f"{now_utc.microsecond // 1000:03d}"
    return f"{base_format}{millis_part}Z"

def seal_instruction(command: str, params: dict, source: str = "external_ai_collaborator", intent_vector: np.ndarray = None):
    """
    Seals an AI instruction into a PSIVI-compliant .psvc + .json sidecar.
    
    Args:
        command: One of ['spawn_agent', 'execute_workflow', 'update_config', 'request_report']
        params: Dictionary of parameters for the command
        source: Identifier of the requesting agent
        intent_vector: Optional 4096-dim numpy array representing AI's intent embedding
    
    Returns:
        Tuple[str, str]: Paths to the sealed .psvc and .json files
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate unique timestamp slug for filenames
    ts_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:-3] # Milliseconds precision in filename
    iso_ts = get_zulu_time_ms()
    
    filename_base = f"instruction_{command}_{ts_str}"
    
    # 1. Create JSON Sidecar
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
        
    # 2. Create Binary .psvc Container
    if intent_vector is None:
        # Default random vector if none provided (for structural validity)
        intent_vector = np.random.randn(4096).astype(np.float32)
        intent_vector /= np.linalg.norm(intent_vector)
    
    vector_bytes = intent_vector.astype(np.float32).tobytes()
    compressed = zlib.compress(vector_bytes, level=9)
    
    header = MAGIC
    header += struct.pack('B', VERSION)
    header += struct.pack('B', PRECISION_FLOAT32)
    header += struct.pack('<I', len(intent_vector))
    header += struct.pack('<I', len(compressed))
    
    psvc_path = OUTPUT_DIR / f"{filename_base}.psvc"
    psvc_path.write_bytes(header + compressed)
    
    return str(psvc_path), str(sidecar_path)

def main():
    print("="*60)
    print("️  PSIVI AETHER Mesh - Instruction Sealer Started")
    print("="*60)
    
    # Example Usage: Spawn a satellite observer
    # In a real scenario, this would be called by an external API or CLI argument parser
    try:
        psvc_path, json_path = seal_instruction(
            command="spawn_agent",
            params={
                "template_name": "satellite_observer",
                "agent_name": "goldstream_init_probe",
                "config": {
                    "target_region": "Goldstream_Watershed",
                    "modality": "RADARSAT_SAR",
                    "priority": "HIGH"
                }
            },
            source="local_dev_seed"
        )
        
        print(f"✅ Instruction Sealed:")
        print(f"   PSVC: {psvc_path}")
        print(f"   JSON: {json_path}")
        print("")
        print("👉 NEXT STEP: Commit these files to your repository.")
        print("   git add data/instruction_queue/")
        print("   git commit -m 'feat(mesh): seed initial instruction'")
        print("   git push origin main")
        print("")
        print("⏳ The GitHub Action will automatically detect the push and process it.")
        
    except Exception as e:
        print(f"❌ Error sealing instruction: {e}", file=sys.stderr)
        sys.exit(1)

    print("="*60)
    print("🏁 Sealing Complete")
    print("="*60)

if __name__ == "__main__":
    main()
