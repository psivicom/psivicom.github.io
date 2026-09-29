#!/usr/bin/env python3
# scripts/build_psvc_mesh.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import hashlib
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

# Import your existing PSVC logic
from src.core.psvc_containers import build_psvc_from_array, serialize_psvc

def tokenize_source(source_bytes: bytes) -> List[int]:
    """
    Converts raw source code into a list of token-like integers.
    This simulates a lightweight tokenizer for vector embedding.
    """
    # Simple byte-level tokenization for demonstration
    # In production, you might use a real tokenizer like BPE or WordPiece
    return list(source_bytes)

def embed_tokens(tokens: List[int], dim: int = 64) -> np.ndarray:
    """
    Projects tokens into a fixed-dimensional vector space.
    Uses a deterministic projection to ensure the same code always 
    produces the same vector (crucial for mesh consensus).
    """
    if not tokens:
        return np.zeros(dim, dtype=np.float32)
        
    # Create a frequency distribution of tokens
    max_val = 256  # Byte range
    freq = np.zeros(max_val, dtype=np.float32)
    for t in tokens:
        freq[t] += 1
        
    # Normalize frequencies
    total = np.sum(freq)
    if total > 0:
        freq /= total
        
    # Project into 'dim' dimensions using a deterministic random matrix
    # We use a fixed seed so the projection is always the same for the same input
    rng = np.random.RandomState(seed=42) 
    projection_matrix = rng.randn(max_val, dim).astype(np.float32)
    
    # Matrix multiplication to get the embedding
    embedding = np.dot(freq, projection_matrix)
    
    # L2 Normalize the final vector for cosine similarity compatibility
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding /= norm
        
    return embedding

def build_service_container(service_name: str, blueprint: dict):
    """Builds a .psvc container with a semantic vector embedding."""
    print(f"🏗️ Building PSVC for: {service_name}")
    
    entry_point = Path(blueprint['entry_point'])
    if not entry_point.exists():
        raise FileNotFoundError(f"Entry point not found: {entry_point}")
        
    source_bytes = entry_point.read_bytes()
    
    # 1. Generate Semantic Vector
    tokens = tokenize_source(source_bytes)
    vector_embedding = embed_tokens(tokens, dim=blueprint.get('vector_dim', 64))
    
    # 2. Build the Container
    container = build_psvc_from_array(
        array=vector_embedding,
        operation="deploy_service",
        agent_id="wendy-architect",
        layer="ORCHESTRATION",
        shard_id=service_name,
        content_type="psvc_service_vector",
        sender_id="psivicom-primary"
    )
    
    # 3. Serialize to .psvc file
    psvc_bytes = serialize_psvc(container)
    psvc_path = Path(f"dist/{service_name}.psvc")
    psvc_path.parent.mkdir(exist_ok=True)
    psvc_path.write_bytes(psvc_bytes)
    
    # 4. Create JSON Sidecar with Metadata
    checksum = hashlib.sha256(psvc_bytes).hexdigest()
    sidecar = {
        "service_name": service_name,
        "blueprint": blueprint,
        "checksum": checksum,
        "vector_norm": float(np.linalg.norm(vector_embedding)),
        "timestamp": "2026-09-30T00:00:00.000Z", # Zulu time
        "status": "READY_FOR_MESH"
    }
    sidecar_path = psvc_path.with_suffix('.json')
    sidecar_path.write_text(json.dumps(sidecar, indent=2))
    
    print(f"✅ Built: {psvc_path} ({len(psvc_bytes)} bytes)")
    print(f"   Vector Norm: {sidecar['vector_norm']:.4f}")

def main():
    blueprint_path = Path("config/psvc_blueprints.json")
    if not blueprint_path.exists():
        print("❌ Blueprint file not found. Please create config/psvc_blueprints.json")
        return

    with open(blueprint_path, 'r') as f:
        blueprints = json.load(f)
        
    for service_name, blueprint in blueprints.items():
        try:
            build_service_container(service_name, blueprint)
        except Exception as e:
            print(f"❌ Failed to build {service_name}: {e}")

if __name__ == "__main__":
    main()
