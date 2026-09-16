# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# seed_mesh.py - Converts existing JSON memories into binary .psvc containers.

import json
import numpy as np
import hashlib
import zlib
import struct
import os
from pathlib import Path

def encode_text(text, dim=4096):
    """Hashing trick to create a 4096-dim vector from text."""
    vec = np.zeros(dim, dtype=np.float32)
    text = text.lower().strip()
    for i in range(max(1, len(text) - 2)):
        trigram = text[i:i+3]
        h = int(hashlib.md5(trigram.encode()).hexdigest(), 16)
        idx = h % dim
        sign = 1 if (h % 2) == 0 else -1
        vec[idx] += sign
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec

def seal_container(vector, container_id, precision="int8"):
    """Compress and seal vector into a .psvc binary file."""
    vec = vector.astype(np.float32)
    scale = np.max(np.abs(vec)) / 127.0
    if scale == 0: scale = 1.0
    compressed = np.round(vec / scale).astype(np.int8).tobytes()
    payload = struct.pack('f', scale) + compressed
    zlibbed = zlib.compress(payload, level=9)
    
    header = b'PSVI' + struct.pack('B', 1) + struct.pack('B', 0) # Magic, v1, int8
    header += struct.pack('I', 4096) + struct.pack('I', len(zlibbed))
    
    path = Path(f"reports/pico_containers/{container_id}.psvc")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + zlibbed)
    return path

print("=== SEEDING PICO MESH ===")
json_files = list(Path("reports").glob("*memory.json"))

if not json_files:
    print("[SEED] No JSON memories found. Creating one dummy vector to seed the mesh.")
    dummy_vec = np.random.randn(4096).astype(np.float32)
    dummy_vec /= np.linalg.norm(dummy_vec)
    seal_container(dummy_vec, "seed_dummy_001")
    print("[SEED] Sealed 1 dummy container.")
else:
    sealed_count = 0
    for jf in json_files:
        try:
            with open(jf) as f:
                data = json.load(f)
            text = data.get("text", "")
            if not text: continue
            
            vec = encode_text(text)
            container_id = hashlib.sha256(vec.tobytes()).hexdigest()[:12]
            seal_container(vec, container_id)
            sealed_count += 1
            print(f"[SEED] Sealed {jf.name} -> {container_id}.psvc")
        except Exception as e:
            print(f"[SEED] Skipped {jf.name}: {e}")
            
    print(f"[SEED] Complete. Sealed {sealed_count} containers.")
