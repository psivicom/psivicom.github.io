# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
#
# Consolidator Agent (Neuroplasticity) - RFC 1001 Compliant

import os
import json
import datetime
import numpy as np
from pathlib import Path

from psvc_reference import (
    read_file, write_file, content_hash, validate_file,
    PRECISION_INT8, PSVCError
)

print("=== PSIVI CONSOLIDATOR AGENT (RFC 1001 COMPLIANT) ===")

CONTAINER_DIR = Path("reports/pico_containers")
CONTAINER_DIR.mkdir(parents=True, exist_ok=True)

REDUNDANCY_THRESHOLD = 0.95
MAX_STATES = 3

def simple_kmeans(vectors, k, max_iter=50):
    """Pure numpy K-Means clustering."""
    if len(vectors) <= k:
        return vectors
    
    indices = np.random.choice(len(vectors), k, replace=False)
    centroids = vectors[indices]
    
    for _ in range(max_iter):
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
                new_centroids.append(centroids[i])
        
        new_centroids = np.array(new_centroids)
        if np.allclose(centroids, new_centroids, atol=1e-4):
            break
        centroids = new_centroids
    
    return centroids

# 1. LOAD ALL RAW VECTORS USING CANONICAL LIBRARY
raw_vectors = []
raw_paths = []

for psvc_file in CONTAINER_DIR.glob("*.psvc"):
    if "state_" in psvc_file.name:
        continue  # Skip master states
    
    try:
        validate_file(psvc_file)
        vec = read_file(psvc_file)
        raw_vectors.append(vec)
        raw_paths.append(psvc_file)
    except PSVCError as e:
        print(f"[CORTEX] Skipping {psvc_file.name}: {e}")
        continue

if not raw_vectors:
    print("[CORTEX] No raw vectors found.")
    exit(0)

vectors_matrix = np.array(raw_vectors)
print(f"[CORTEX] Loaded {len(vectors_matrix)} raw vectors.")

# 2. CLUSTERING
print(f"[CORTEX] Running K-Means (max {MAX_STATES} states)...")
centroids = simple_kmeans(vectors_matrix, min(MAX_STATES, len(vectors_matrix)))

print(f"[CORTEX] Identified {len(centroids)} distinct states.")
for i, c in enumerate(centroids):
    chash = content_hash(c)
    output_path = CONTAINER_DIR / f"state_{i}_{chash}.psvc"
    write_file(c, output_path, precision=PRECISION_INT8)
    print(f"[CORTEX] Sealed State {i}: {output_path.name}")

# 3. ENTROPY PRUNING
print(f"[CORTEX] Pruning (redundancy > {REDUNDANCY_THRESHOLD})...")
pruned_count = 0

sims = vectors_matrix @ centroids.T
max_sims = np.max(sims, axis=1)

for i, psvc_file in enumerate(raw_paths):
    if max_sims[i] >= REDUNDANCY_THRESHOLD:
        psvc_file.unlink()
        json_file = psvc_file.with_suffix('.json')
        if json_file.exists():
            json_file.unlink()
        pruned_count += 1

print(f"[CORTEX] Pruned {pruned_count} redundant vectors.")
print("[CORTEX] Neuroplasticity cycle complete.")
