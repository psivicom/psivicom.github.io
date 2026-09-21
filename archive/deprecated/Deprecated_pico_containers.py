# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# pico_containers.py - Sealed vector containers. Open only when called from VRAM.

import numpy as np
import hashlib
import json
import zlib
import struct
from pathlib import Path

class PicoContainer:
    """A sealed micro-container holding one compressed vector.
    Opens only when explicitly called. Seals back when evicted."""

    MAGIC = b'PSVI'  # Container signature
    VERSION = 1

    def __init__(self, container_id, dim=4096):
        self.id = container_id
        self.dim = dim
        self.path = Path(f"reports/pico_containers/{container_id}.psvc")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._open_vector = None  # None = sealed
        self._metadata = {}

    def seal(self, vector, precision="int8"):
        """Compress vector into sealed container. Zero VRAM used."""
        vec = vector.astype(np.float32)
        
        if precision == "int8":
            scale = np.max(np.abs(vec)) / 127.0
            if scale == 0: scale = 1.0
            compressed = np.round(vec / scale).astype(np.int8).tobytes()
            payload = struct.pack('f', scale) + compressed
        elif precision == "float16":
            compressed = vec.astype(np.float16).tobytes()
            payload = compressed
        else:
            compressed = vec.astype(np.float32).tobytes()
            payload = compressed

        # zlib compress the payload
        zlibbed = zlib.compress(payload, level=9)

        # Write sealed container
        header = self.MAGIC + struct.pack('B', self.VERSION)
        header += struct.pack('B', {"int8": 0, "float16": 1, "float32": 2}[precision])
        header += struct.pack('I', self.dim)
        header += struct.pack('I', len(zlibbed))

        self.path.write_bytes(header + zlibbed)

        # Store metadata separately (tiny JSON)
        meta_path = self.path.with_suffix('.json')
        meta_path.write_text(json.dumps({
            "id": self.id,
            "dim": self.dim,
            "precision": precision,
            "sealed_size_bytes": len(zlibbed) + len(header),
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }))

        self._open_vector = None
        return len(zlibbed) + len(header)

    def open(self):
        """Open the container. Decompress directly into numpy array. VRAM activated."""
        if self._open_vector is not None:
            return self._open_vector  # Already open

        if not self.path.exists():
            return None

        raw = self.path.read_bytes()
        
        # Parse header
        magic = raw[:4]
        if magic != self.MAGIC:
            return None

        version = raw[4]
        precision_code = raw[5]
        dim = struct.unpack('I', raw[6:10])[0]
        payload_size = struct.unpack('I', raw[10:14])[0]

        # Decompress
        zlibbed = raw[14:14 + payload_size]
        payload = zlib.decompress(zlibbed)

        precision = {0: "int8", 1: "float16", 2: "float32"}[precision_code]

        if precision == "int8":
            scale = struct.unpack('f', payload[:4])[0]
            int8_data = np.frombuffer(payload[4:], dtype=np.int8)
            self._open_vector = int8_data.astype(np.float32) * scale
        elif precision == "float16":
            self._open_vector = np.frombuffer(payload, dtype=np.float16).astype(np.float32)
        else:
            self._open_vector = np.frombuffer(payload, dtype=np.float32).copy()

        return self._open_vector

    def close(self):
        """Seal back. Release VRAM."""
        self._open_vector = None

    @property
    def is_open(self):
        return self._open_vector is not None


class PicoMesh:
    """Mesh of sealed containers. Opens only what VRAM needs."""

    def __init__(self, folder="reports/pico_containers", vram_slots=5, dim=4096):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.vram_slots = vram_slots
        self.dim = dim
        self.active_containers = {}  # slot -> container_id
        self.open_order = []

    def store(self, vector, agent_name, precision="int8"):
        """Store vector as sealed container."""
        content_hash = hashlib.sha256(vector.astype(np.float32).tobytes()).hexdigest()[:12]
        container = PicoContainer(content_hash, self.dim)
        size = container.seal(vector, precision)
        print(f"[PICO] Sealed {agent_name} vector: {content_hash} ({size} bytes)")
        return content_hash

    def call(self, container_id):
        """Call a container open. Evicts oldest if VRAM full."""
        # Already open?
        if container_id in self.active_containers.values():
            for slot, cid in self.active_containers.items():
                if cid == container_id:
                    self.open_order.remove(container_id)
                    self.open_order.append(container_id)
                    return PicoContainer(container_id, self.dim).open()

        # Evict if full
        if len(self.active_containers) >= self.vram_slots:
            oldest_id = self.open_order.pop(0)
            evict_slot = [s for s, cid in self.active_containers.items() if cid == oldest_id][0]
            del self.active_containers[evict_slot]
            PicoContainer(oldest_id, self.dim).close()
            print(f"[PICO] Evicted {oldest_id} from VRAM. Sealed.")

        # Open new container
        container = PicoContainer(container_id, self.dim)
        vec = container.open()
        if vec is None:
            return None

        # Assign to free slot
        free_slot = next(s for s in range(self.vram_slots) if s not in self.active_containers)
        self.active_containers[free_slot] = container_id
        self.open_order.append(container_id)
        print(f"[PICO] Opened {container_id} into VRAM slot {free_slot}")
        return vec

    def mesh_stats(self):
        """Report: how many sealed, how many open."""
        total = len(list(self.folder.glob("*.psvc")))
        open_count = len(self.active_containers)
        return {
            "total_containers": total,
            "open_in_vram": open_count,
            "sealed_dormant": total - open_count,
            "vram_slots": self.vram_slots,
            "utilization": f"{open_count}/{self.vram_slots}"
        }


# --- DEMO ---
if __name__ == "__main__":
    print("=== PICO CONTAINER MESH ===")
    mesh = PicoMesh(vram_slots=3)

    # Store 10 vectors as sealed containers
    hashes = []
    for i in range(10):
        vec = np.random.randn(4096).astype(np.float32)
        h = mesh.store(vec, f"agent_{i}", precision="int8")
        hashes.append(h)

    print(f"\n[PICO] Stored 10 sealed containers.")
    print(f"[PICO] Stats: {mesh.mesh_stats()}")

    # Call 5 containers open (only 3 fit in VRAM)
    for i in range(5):
        mesh.call(hashes[i])

    print(f"\n[PICO] After calling 5 containers:")
    print(f"[PICO] Stats: {mesh.mesh_stats()}")
    # Expected: 3 open, 2 evicted back to sealed, 5 still dormant
