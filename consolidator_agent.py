# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# consolidator_agent.py - True Neuroplasticity: K-Means Clustering & Entropy Pruning.

import os
import json
import struct
import zlib
import hashlib
import datetime
import numpy as np
from pathlib import Path
from collections import defaultdict

CONTAINER_DIR = Path("reports/pico_containers")
MAGIC = b'PSVI'
DIM = 4096
REDUNDANCY_THRESHOLD = 0.95 # Prune if 95% similar to an existing concept
MAX_STATES = 3 # Max distinct ecological states to track (e.g., Bloom, Drought, Normal)

def read_psvc(path):
    try:
        raw = path.read_bytes()
        if raw[:4] != MAGIC: return None
        precision = raw[5]
        payload_size = struct.unpack('I', raw[10:14])[0]
        payload = zlib.decompress(raw[14:14 + payload_size])
        
        if precision == 0: 
            scale = struct.unpack('f', payload[:4])[0]
            return np.frombuffer(payload[4:], dtype=np.int8).astype(np.float32) * scale
        elif precision == 1: 
            return np.frombuffer(payload, dtype=np.float16).astype(np.float32)
        return np.frombuffer(payload, dtype=np.float32).copy()
    except Exception as e:
        print(f"[CORTEX] Error reading {path}: {e}")
        return None

def seal_master(vector, state_id):
    content_hash = hashlib.sha256(vector.tobytes()).hexdigest()[:12]
    path = CONTAINER_DIR / f"state_{state_id}_{content_hash}.psvc"
    
    vec = vector.astype(np.float32)
    scale = np.max(np.abs(vec)) / 127.0
    if scale == 0: scale = 1.0
    compressed = np.round(vec / scale).astype(np.int8).tobytes()
    payload = struct.pack('f', scale) + compressed
    zlibbed = zlib.compress(payload, level=9)
    
    header = MAGIC + struct.pack('B', 1) + struct.pack('B', 0) 
    header += struct.pack('I', DIM) + struct.pack('I', len(zlibbed))
    path.write_bytes(header + zlibbed)
    return path.name

def simple_kmeans(vectors, k, max_iter=50):
    """Pure numpy K-Means to find distinct ecological states."""
    if len(vectors) <= k:
        return vectors
    
    # Initialize centroids randomly from existing vectors
    indices = np.random.choice(len(vectors), k, replace=False)
    centroids = vectors[indices]
    
    for _ in range(max_iter):
        # Calculate cosine similarity between all vectors and all centroids
        # (vectors @ centroids.T) gives a matrix of similarities
        sims = vectors @ centroids.T 
        labels = np.argmax(sims, axis=1)
        
        new_centroids = []
        for i in range(k):
            cluster_points = vectors[labels == i]
            if len(cluster_points) > 0:
                c = np.mean(cluster_points, axis=0)
                c /= np.linalg.norm(c)
                new_centroids.append(c)
            else:
                new_centroids.append(centroids[i]) # Keep old if empty
        
        new_centroids = np.array(new_centroids)
        if np.allclose(centroids, new_centroids, atol=1e-4):
            break
        centroids = new_centroids
        
    return centroids

print("=== PSIVI CORTEX: K-MEANS CLUSTERING & ENTROPY PRUNING ===")
CONTAINER_DIR.mkdir(parents=True, exist_ok=True)

# 1. LOAD ALL RAW VECTORS
raw_vectors = []
raw_paths = []

for psvc_file in CONTAINER_DIR.glob("*.psvc"):
    if "state_" in psvc_file.name or "master_" in psvc_file.name: 
        continue # Skip existing consolidated states
        
    vec = read_psvc(psvc_file)
    if vec is not None:
        raw_vectors.append(vec)
        raw_paths.append(psvc_file)

if not raw_vectors:
    print("[CORTEX] No raw vectors found. Mesh is empty.")
    exit(0)

vectors_matrix = np.array(raw_vectors)
print(f"[CORTEX] Loaded {len(vectors_matrix)} raw vectors into cortex.")

# 2. CLUSTERING: Find the distinct ecological states
print(f"[CORTEX] Running K-Means to identify up to {MAX_STATES} distinct states...")
centroids = simple_kmeans(vectors_matrix, min(MAX_STATES, len(vectors_matrix)))

print(f"[CORTEX] Identified {len(centroids)} distinct ecological states.")
for i, c in enumerate(centroids):
    seal_master(c, i)
    print(f"[CORTEX] Sealed State {i} master vector.")

# 3. ENTROPY PRUNING: Delete only redundant data
# A raw vector is pruned if it is >95% similar to ANY of the new master states.
# This preserves novel data forever, but deletes routine noise.
print(f"[CORTEX] Pruning based on information entropy (redundancy > {REDUNDANCY_THRESHOLD})...")
pruned_count = 0

# Calculate similarity of all raw vectors against the new master centroids
sims = vectors_matrix @ centroids.T
max_sims = np.max(sims, axis=1)

for i, psvc_file in enumerate(raw_paths):
    if max_sims[i] >= REDUNDANCY_THRESHOLD:
        # This vector is highly redundant. The master state already captures it perfectly.
        psvc_file.unlink() # Delete binary
        
        # Also delete the associated JSON metadata if it exists
        json_file = psvc_file.with_suffix('.json')
        if json_file.exists():
            json_file.unlink()
            
        pruned_count += 1

print(f"[CORTEX] Pruned {pruned_count} highly redundant vectors. Novel data preserved.")
print("[CORTEX] Neuroplasticity cycle complete. Mesh intelligence optimized.")
