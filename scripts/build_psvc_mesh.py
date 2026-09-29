#!/usr/bin/env python3
# scripts/build_psvc_mesh.py
# SPDX-License-Identifier: EUPL-1.2

import json
import hashlib
from pathlib import Path
from src.core.psvc_containers import build_psvc_from_array, serialize_psvc
import numpy as np

def build_service_container(service_name: str, blueprint: dict):
    """Builds a .psvc container for a specific service."""
    print(f"🏗️ Building PSVC for: {service_name}")
    
    # Load source code as bytes
    entry_point = Path(blueprint['entry_point'])
    if not entry_point.exists():
        raise FileNotFoundError(f"Entry point not found: {entry_point}")
        
    source_bytes = entry_point.read_bytes()
    
    # Create a vector representation of the service (e.g., hash of source + config)
    # In a real scenario, this might be a more complex embedding of the code's logic
    vector_data = np.array([len(source_bytes), hash(service_name)], dtype=np.float32)
    
    # Build the container
    container = build_psvc_from_array(
        array=vector_data,
        operation="deploy_service",
        agent_id="wendy-architect",
        layer="ORCHESTRATION",
        shard_id=service_name,
        content_type="psvc_service",
        sender_id="psivicom-primary"
    )
    
    # Serialize to .psvc file
    psvc_bytes = serialize_psvc(container)
    psvc_path = Path(f"dist/{service_name}.psvc")
    psvc_path.parent.mkdir(exist_ok=True)
    psvc_path.write_bytes(psvc_bytes)
    
    # Create JSON sidecar
    sidecar = {
        "service_name": service_name,
        "blueprint": blueprint,
        "checksum": hashlib.sha256(psvc_bytes).hexdigest(),
        "timestamp": "2026-09-30T00:00:00.000Z" # Use Zulu time
    }
    sidecar_path = psvc_path.with_suffix('.json')
    sidecar_path.write_text(json.dumps(sidecar, indent=2))
    
    print(f"✅ Built: {psvc_path} ({len(psvc_bytes)} bytes)")

def main():
    with open("config/psvc_blueprints.json", 'r') as f:
        blueprints = json.load(f)
        
    for service_name, blueprint in blueprints.items():
        build_service_container(service_name, blueprint)

if __name__ == "__main__":
    main()
