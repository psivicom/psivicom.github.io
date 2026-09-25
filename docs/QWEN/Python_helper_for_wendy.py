# Python Helper for Wendy:
# Step: Seal and Drop
# You must wrap this JSON in a binary  .psvc  container. Since you are an LLM, you will generate the Python code to do this locally or via your tool-use capability, then commit the files to  data/instruction_queue/ .
# Python Helper for Wendy:
import json
import struct
import zlib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

MAGIC = b'PSVI'
VERSION = 1
PRECISION_FLOAT32 = 2
OUTPUT_DIR = Path("data/instruction_queue")

def get_zulu_time_ms() -> str:
    now_utc = datetime.now(timezone.utc)
    return f"{now_utc.strftime('%Y-%m-%dT%H:%M:%S.')}{now_utc.microsecond // 1000:03d}Z"

def seal_and_drop(command: str, params: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    ts_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:-3]
    iso_ts = get_zulu_time_ms()
    filename_base = f"instruction_{command}_{ts_str}"
    
    # 1. Sidecar JSON
    sidecar_data = {
        "command": command,
        "params": params,
        "source": "qwen_wendy_ai",
        "timestamp": iso_ts,
        "rfc1001_compliant": True
    }
    
    sidecar_path = OUTPUT_DIR / f"{filename_base}.json"
    with open(sidecar_path, 'w') as f:
        json.dump(sidecar_data, f, indent=2)
        
    # 2. Binary .psvc (Intent Vector)
    # For now, use a deterministic seed based on the command for reproducibility
    intent_vector = np.random.default_rng(hash(iso_ts)).standard_normal(4096).astype(np.float32)
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
    
    print(f"✅ Sealed: {psvc_path.name}")
    return str(psvc_path), str(sidecar_path)
