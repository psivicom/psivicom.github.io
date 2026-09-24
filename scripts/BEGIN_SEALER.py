# scripts/BEGIN_SEALER.py
"""
PSIVI AETHER Mesh — Instruction Sealer (BEGIN_SEALER.py)
Location: /scripts/BEGIN_SEALER.py

This script is used to CREATE and DROP instructions into the mesh queue.
It reads environment variables to determine what kind of instruction to create.

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

def seal_instruction(command: str, params: dict, source: str = "workflow_seed", intent_vector: np.ndarray = None):
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
    
    # Read configuration from Environment Variables (set by GitHub Actions)
    command_type = os.getenv("COMMAND_TYPE", "spawn_agent")
    template_name = os.getenv("TEMPLATE_NAME", "satellite_observer")
    target_region = os.getenv("TARGET_REGION", "Goldstream_Watershed")
    
    try:
        if command_type == "spawn_agent":
            psvc_path, json_path = seal_instruction(
                command="spawn_agent",
                params={
                    "template_name": template_name,
                    "agent_name": f"{template_name}_seed_{datetime.now().strftime('%H%M%S')}",
                    "config": {
                        "target_region": target_region,
                        "modality": "RADARSAT_SAR",
                        "priority": "HIGH"
                    }
                },
                source="workflow_seed"
            )
        elif command_type == "request_report":
            psvc_path, json_path = seal_instruction(
                command="request_report",
                params={
                    "topic": "Initial Mesh Health Check",
                    "format": "JSON"
                },
                source="workflow_seed"
            )
        else:
            raise ValueError(f"Unknown command type: {command_type}")
        
        print(f"✅ Instruction Sealed:")
        print(f"   PSVC: {psvc_path}")
        print(f"   JSON: {json_path}")
        
    except Exception as e:
        print(f"❌ Error sealing instruction: {e}", file=sys.stderr)
        sys.exit(1)

    print("="*60)
    print("🏁 Sealing Complete")
    print("="*60)

if __name__ == "__main__":
    main()
