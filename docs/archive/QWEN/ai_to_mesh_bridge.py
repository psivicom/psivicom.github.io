# ai_to_mesh_bridge.py
# Run this externally (e.g., by Qwen) to drop a valid instruction into the PSIVI mesh

import json
import hashlib
import struct
import zlib
from pathlib import Path
from datetime import datetime

# PSIVI RFC 1001 Constants
MAGIC = b'PSVI'
VERSION = 1
HEADER_SIZE = 14
PRECISION_FLOAT32 = 2

def seal_instruction(command: str, params: dict, output_dir: str = "data/instruction_queue"):
    """Seals an AI instruction into a PSIVI-compliant .psvc + .json sidecar."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename_base = f"instruction_{command}_{timestamp}"
    
    # 1. Create the sidecar metadata
    sidecar_data = {
        "command": command,
        "params": params,
        "source": "external_ai_qwen",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rfc1001_compliant": True
    }
    
    # 2. Create a dummy vector payload (represents the AI's "intent" vector)
    # In a real scenario, this could be a 4096-dim embedding of the scientific query
    intent_vector = [0.1] * 4096 
    vector_bytes = struct.pack(f'{len(intent_vector)}f', *intent_vector)
    compressed = zlib.compress(vector_bytes, level=9)
    
    # 3. Build the .psvc header
    header = MAGIC
    header += struct.pack('B', VERSION)
    header += struct.pack('B', PRECISION_FLOAT32)
    header += struct.pack('I', len(intent_vector))
    header += struct.pack('I', len(compressed))
    
    # 4. Write files
    psvc_path = Path(output_dir) / f"{filename_base}.psvc"
    psvc_path.write_bytes(header + compressed)
    
    sidecar_path = Path(output_dir) / f"{filename_base}.json"
    with open(sidecar_path, 'w') as f:
        json.dump(sidecar_data, f, indent=2)
        
    print(f"✅ AI Instruction Sealed & Dropped: {psvc_path.name}")
    return str(psvc_path)

# --- EXAMPLE: Qwen autonomously requests the mesh to spawn a RADARSAT agent ---
if __name__ == "__main__":
    seal_instruction(
        command="spawn_agent",
        params={
            "template_name": "satellite_observer",
            "agent_name": "qwen_requested_radarsat",
            "config": {
                "target_region": "Goldstream_Watershed",
                "modality": "RADARSAT_SAR",
                "priority": "HIGH",
                "requested_by": "Qwen-AI"
            }
        }
    )
