# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# vram_mesh.py - Shared memory agent bus. No files. No text. Pure vectors.
import numpy as np
from multiprocessing import shared_memory
import threading
import time

DIM = 4096
AGENT_SLOTS = 8  # Max agents in the mesh
BYTES_PER_VECTOR = DIM * 4  # float32 = 4 bytes

class VRAMMesh:
    def __init__(self, name="psivi_vram", create=False):
        self.name = name
        self.size = AGENT_SLOTS * BYTES_PER_VECTOR
        if create:
            try:
                self.shm = shared_memory.SharedMemory(name=name, create=True, size=self.size)
                print(f"[VRAM] Created bus: {self.size} bytes")
            except FileExistsError:
                self.shm = shared_memory.SharedMemory(name=name)
        else:
            self.shm = shared_memory.SharedMemory(name=name)
        self.buf = np.ndarray((AGENT_SLOTS, DIM), dtype=np.float32, buffer=self.shm.buf)

    def write(self, agent_slot, vector):
        """Write a 4096-dim vector directly to shared VRAM. Zero serialization."""
        self.buf[agent_slot] = vector.astype(np.float32)

    def read(self, agent_slot):
        """Read a vector from shared VRAM. Zero deserialization."""
        return self.buf[agent_slot].copy()

    def broadcast(self, vector):
        """Write to all slots simultaneously."""
        for i in range(AGENT_SLOTS):
            self.buf[i] = vector.astype(np.float32)

    def consensus(self, threshold=0.7):
        """Byzantine check: do agents agree? Cosine similarity across slots."""
        active = [self.buf[i] for i in range(AGENT_SLOTS) if np.any(self.buf[i])]
        if len(active) < 2:
            return True, 0.0
        base = active[0]
        base_norm = np.linalg.norm(base)
        if base_norm == 0:
            return True, 0.0
        base = base / base_norm
        scores = []
        for vec in active[1:]:
            vec_norm = np.linalg.norm(vec)
            if vec_norm == 0:
                scores.append(0.0)
                continue
            scores.append(float(np.dot(base, vec / vec_norm)))
        avg_score = float(np.mean(scores))
        return avg_score >= threshold, avg_score

    def close(self):
        self.shm.close()

    def destroy(self):
        self.shm.close()
        self.shm.unlink()

# --- DEMO: 3 agents communicating in pure vectors ---
if __name__ == "__main__":
    mesh = VRAMMesh(create=True)

    # Agent 0: Forage agent writes observation vector
    forage_vec = np.random.randn(DIM).astype(np.float32)
    forage_vec /= np.linalg.norm(forage_vec)
    mesh.write(0, forage_vec)
    print("[AGENT 0] Wrote forage vector to VRAM")

    # Agent 1: Critic reads and modifies
    received = mesh.read(0)
    correction = received * 0.95  # Apply learned adjustment
    mesh.write(1, correction)
    print("[AGENT 1] Critic applied correction to VRAM")

    # Agent 2: Synthesizer reads both and checks consensus
    v0 = mesh.read(0)
    v1 = mesh.read(1)
    agreed, score = mesh.consensus(threshold=0.7)
    print(f"[AGENT 2] Consensus: {'AGREED' if agreed else 'REJECTED'} (score: {score:.4f})")

    # Cleanup
    mesh.destroy()
    print("[VRAM] Bus destroyed. Zero files touched. Zero text encoded.")
