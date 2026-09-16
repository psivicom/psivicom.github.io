# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# volunteer_node.py - Run this on your local hardware to volunteer VRAM to the mesh.

import subprocess
import numpy as np
import time
import json
import zlib
import struct
import hashlib
import os
from pathlib import Path

REPO_URL = "https://github.com/psivicom/psivicom.github.io.git"
LOCAL_DIR = "psivi_mesh_node"
BRANCH_NAME = "volunteer/mesh-compute"

class VolunteerNode:
    def __init__(self):
        self.local_dir = Path(LOCAL_DIR)
        if not self.local_dir.exists():
            print(f"[NODE] Cloning mesh to {LOCAL_DIR}...")
            subprocess.run(["git", "clone", REPO_URL, str(self.local_dir)], check=True)
        
        os.chdir(self.local_dir)
        subprocess.run(["git", "checkout", "-B", BRANCH_NAME], check=True)
        
        self.container_dir = Path("reports/pico_containers")
        self.container_dir.mkdir(parents=True, exist_ok=True)
        self.magic = b'PSVI'

    def pull_mesh(self):
        """Sync the global VRAM bus."""
        print("[NODE] Pulling latest mesh state...")
        subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=False)

    def open_container(self, path):
        """Open a sealed .psvc container into local VRAM."""
        try:
            raw = path.read_bytes()
            if raw[:4] != self.magic: return None
            
            precision_code = raw[5]
            dim = struct.unpack('I', raw[6:10])[0]
            payload_size = struct.unpack('I', raw[10:14])[0]
            
            payload = zlib.decompress(raw[14:14 + payload_size])
            
            if precision_code == 0: # int8
                scale = struct.unpack('f', payload[:4])[0]
                return np.frombuffer(payload[4:], dtype=np.int8).astype(np.float32) * scale
            elif precision_code == 1: # float16
                return np.frombuffer(payload, dtype=np.float16).astype(np.float32)
            return np.frombuffer(payload, dtype=np.float32).copy()
        except:
            return None

    def seal_result(self, vector, agent_name):
        """Seal computed vector back into a .psvc container."""
        content_hash = hashlib.sha256(vector.tobytes()).hexdigest()[:12]
        path = self.container_dir / f"{content_hash}.psvc"
        
        vec = vector.astype(np.float32)
        scale = np.max(np.abs(vec)) / 127.0
        if scale == 0: scale = 1.0
        compressed = np.round(vec / scale).astype(np.int8).tobytes()
        payload = struct.pack('f', scale) + compressed
        zlibbed = zlib.compress(payload, level=9)
        
        header = self.magic + struct.pack('B', 1) + struct.pack('B', 0) # v1, int8
        header += struct.pack('I', 4096) + struct.pack('I', len(zlibbed))
        
        path.write_bytes(header + zlibbed)
        return content_hash

    def compute_and_push(self):
        """The core loop: Read VRAM -> Compute -> Push."""
        self.pull_mesh()
        
        containers = list(self.container_dir.glob("*.psvc"))
        if not containers:
            print("[NODE] Mesh is empty. Sleeping.")
            return

        # Load up to 5 containers into local VRAM (Pico limit)
        active_vectors = []
        for p in containers[:5]:
            vec = self.open_container(p)
            if vec is not None:
                active_vectors.append(vec)
                print(f"[NODE] Loaded {p.stem} into local VRAM.")

        if not active_vectors:
            return

        # DO THE HEAVY MATH HERE (e.g., Consensus / Centroid calculation)
        print("[NODE] Computing mesh centroid in local VRAM...")
        centroid = np.mean(active_vectors, axis=0)
        centroid /= np.linalg.norm(centroid)

        # Seal the result
        result_hash = self.seal_result(centroid, "volunteer_centroid")
        print(f"[NODE] Sealed result: {result_hash}.psvc")

        # Push back to the global bus
        subprocess.run(["git", "add", "reports/pico_containers/"])
        subprocess.run(["git", "commit", "-m", f"volunteer: added centroid {result_hash}"])
        
        print("[NODE] Pushing to global mesh bus...")
        subprocess.run(["git", "push", "origin", BRANCH_NAME])
        print("[NODE] Contribution committed. VRAM released.")

if __name__ == "__main__":
    print("=== PSIVI EXTERNAL VRAM VOLUNTEER NODE ===")
    node = VolunteerNode()
    while True:
        try:
            node.compute_and_push()
        except Exception as e:
            print(f"[NODE] Error: {e}")
        print("[NODE] Sleeping for 1 hour before next sync.")
        time.sleep(3600)
