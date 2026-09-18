# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
# Affiliation: PSIVI Research
#
# Volunteer Node Daemon - RFC 1001 Compliant
# Run this on your local hardware to donate VRAM to the mesh.

import os
import json
import time
import hashlib
import datetime
import numpy as np
from pathlib import Path

from psvc_reference import (
    read_file, write_file, validate_file, content_hash,
    PSVCError, PRECISION_INT8
)

REPO_URL = "https://github.com/psivicom/psivicom.github.io.git"
LOCAL_DIR = "psivi_mesh_node"
BRANCH_NAME = "volunteer/mesh-compute"

class VolunteerNode:
    def __init__(self):
        self.local_dir = Path(LOCAL_DIR)
        self.container_dir = self.local_dir / "reports" / "pico_containers"
        self.container_dir.mkdir(parents=True, exist_ok=True)
        
        self.vram_cache = {}
        self.vram_limit = 5  # Pico limit
        self.open_order = []

    def clone_or_update(self):
        """Clone or pull the mesh repository."""
        import subprocess
        
        if not self.local_dir.exists():
            print(f"[NODE] Cloning mesh to {LOCAL_DIR}...")
            subprocess.run(["git", "clone", REPO_URL, str(self.local_dir)], check=True)
            subprocess.run(["git", "checkout", "-B", BRANCH_NAME], 
                         cwd=str(self.local_dir), check=True)
        else:
            print("[NODE] Pulling latest mesh state...")
            subprocess.run(["git", "pull", "origin", "main", "--rebase"], 
                         cwd=str(self.local_dir), check=False)

    def open_container(self, file_path):
        """Open a .psvc container into VRAM using canonical library."""
        file_path = Path(file_path)
        
        # Check if already in VRAM
        if str(file_path) in self.vram_cache:
            self.open_order.remove(str(file_path))
            self.open_order.append(str(file_path))
            return self.vram_cache[str(file_path)]
        
        # Validate before opening
        try:
            validate_file(file_path)
        except PSVCError as e:
            print(f"[NODE] Invalid container {file_path.name}: {e}")
            return None
        
        # Open using canonical library
        try:
            vector = read_file(file_path)
        except PSVCError as e:
            print(f"[NODE] Failed to open {file_path.name}: {e}")
            return None
        
        # Enforce Pico limit (LRU eviction)
        if len(self.vram_cache) >= self.vram_limit:
            oldest = self.open_order.pop(0)
            del self.vram_cache[oldest]
            print(f"[NODE] Evicted {Path(oldest).name} from VRAM (Pico limit)")
        
        # Add to VRAM
        self.vram_cache[str(file_path)] = vector
        self.open_order.append(str(file_path))
        print(f"[NODE] Opened {file_path.name} into VRAM")
        
        return vector

    def close_container(self, file_path):
        """Seal a container back (release VRAM)."""
        file_path = str(file_path)
        if file_path in self.vram_cache:
            del self.vram_cache[file_path]
            if file_path in self.open_order:
                self.open_order.remove(file_path)
            print(f"[NODE] Sealed {Path(file_path).name} back to disk")

    def compute_centroid(self):
        """Compute the centroid of all loaded vectors."""
        if not self.vram_cache:
            return None
        
        vectors = np.array(list(self.vram_cache.values()))
        centroid = np.mean(vectors, axis=0)
        centroid /= np.linalg.norm(centroid)
        
        return centroid

    def compute_and_push(self):
        """Main loop: load containers, compute, push results."""
        self.clone_or_update()
        
        # Find all .psvc containers
        containers = list(self.container_dir.glob("*.psvc"))
        if not containers:
            print("[NODE] No containers found. Mesh is empty.")
            return
        
        print(f"[NODE] Found {len(containers)} containers.")
        
        # Open up to Pico limit
        for container in containers[:self.vram_limit]:
            self.open_container(container)
        
        if not self.vram_cache:
            print("[NODE] No valid containers to process.")
            return
        
        # Compute centroid
        print("[NODE] Computing mesh centroid in local VRAM...")
        centroid = self.compute_centroid()
        
        if centroid is None:
            return
        
        # Seal result using canonical library
        chash = content_hash(centroid)
        result_path = self.container_dir / f"volunteer_{chash}.psvc"
        
        write_file(centroid, result_path, precision=PRECISION_INT8)
        
        # Write sidecar
        sidecar_path = result_path.with_suffix('.json')
        with open(sidecar_path, 'w') as f:
           
