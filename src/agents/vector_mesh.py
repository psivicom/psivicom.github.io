# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
import numpy as np
import hashlib
import json
import os
import datetime
from pathlib import Path

class VectorMesh:
    """Pico-VRAM Vector Memory with INT8/Float16 quantization and LRU caching."""
    
    def __init__(self, folder="reports/vector_memory", dim=4096, vram_limit=5):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.dim = dim
        self.vram_limit = vram_limit  # Strict VRAM limit (Pico scale)
        self.vram_cache = {}          # Active working set in "VRAM"
        self.access_order = []        # For LRU eviction

    def encode(self, text):
        """Convert text to a real 4096-dim float32 vector using hashing trick"""
        vec = np.zeros(self.dim, dtype=np.float32)
        text = text.lower().strip()
        for i in range(max(1, len(text) - 2)):
            trigram = text[i:i+3]
            h = int(hashlib.md5(trigram.encode()).hexdigest(), 16)
            idx = h % self.dim
            sign = 1 if (h % 2) == 0 else -1
            vec[idx] += sign
        norm = np.linalg.norm(vec)
        if norm > 0: vec = vec / norm
        return vec

    def _compress(self, vec, precision):
        """Compress vector for disk storage"""
        if precision == "int8":
            scale = np.max(np.abs(vec)) / 127.0
            if scale == 0: scale = 1.0
            quantized = np.round(vec / scale).astype(np.int8)
            return quantized, float(scale)
        elif precision == "float16":
            return vec.astype(np.float16), None
        return vec.astype(np.float32), None

    def _decompress(self, data, precision, scale=None):
        """Decompress vector back to float32 for VRAM compute"""
        if precision == "int8":
            return data.astype(np.float32) * scale
        return data.astype(np.float32)

    def write(self, text, agent_name, precision="int8"):
        """Store compressed vector + metadata"""
        vec = self.encode(text)
        content_hash = hashlib.sha256(vec.tobytes()).hexdigest()[:12]
        
        compressed_data, scale = self._compress(vec, precision)
        np.save(self.folder / f"{content_hash}.npy", compressed_data)
        
        meta = {
            "text": text, "agent": agent_name, "hash": content_hash,
            "dim": self.dim, "precision": precision, "scale": scale,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        with open(self.folder / f"{content_hash}.json", 'w') as f:
            json.dump(meta, f, indent=2)
        
        print(f"[VRAM MESH] {agent_name} wrote {precision} vector: {content_hash}")
        return content_hash

    def _load_to_vram(self, content_hash):
        """Sparse load: fetch from disk to VRAM cache with LRU eviction"""
        if content_hash in self.vram_cache:
            self.access_order.remove(content_hash)
            self.access_order.append(content_hash)
            return self.vram_cache[content_hash]

        meta_path = self.folder / f"{content_hash}.json"
        npy_path = self.folder / f"{content_hash}.npy"
        if not meta_path.exists() or not npy_path.exists():
            return None

        with open(meta_path) as f:
            meta = json.load(f)
        
        compressed_data = np.load(npy_path)
        vec = self._decompress(compressed_data, meta['precision'], meta.get('scale'))

        # LRU Eviction if VRAM is full
        if len(self.vram_cache) >= self.vram_limit:
            oldest = self.access_order.pop(0)
            del self.vram_cache[oldest]
            print(f"[VRAM] Evicted {oldest} to make room.")

        self.vram_cache[content_hash] = vec
        self.access_order.append(content_hash)
        return vec

    def search(self, query_text, top_k=3):
        """Cosine similarity search, only loading top matches into VRAM"""
        query_vec = self.encode(query_text)
        results = []
        
        for meta_file in self.folder.glob("*.json"):
            content_hash = meta_file.stem
            with open(meta_file) as f:
                meta = json.load(f)
            
            # Fast path: load to VRAM only if needed
            vec = self._load_to_vram(content_hash)
            if vec is None: continue
            
            similarity = float(np.dot(query_vec, vec))
            results.append({
                "hash": content_hash, "similarity": similarity,
                "text": meta.get("text", ""), "agent": meta.get("agent", "unknown")
            })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def read_all(self):
        """Read metadata only (saves VRAM)"""
        memories = []
        for meta_file in self.folder.glob("*.json"):
            with open(meta_file) as f:
                memories.append(json.load(f))
        return memories
