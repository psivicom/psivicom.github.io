import numpy as np
import hashlib
import json
import os
import datetime
from pathlib import Path

class VectorMesh:
    """Real 4096-dim vector memory using numpy. No PyTorch needed."""
    
    def __init__(self, folder="reports/vector_memory", dim=4096):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.dim = dim

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
        if norm > 0:
            vec = vec / norm
        return vec

    def write(self, text, agent_name):
        """Store vector as float16 numpy + metadata JSON"""
        vec = self.encode(text)
        content_hash = hashlib.sha256(vec.tobytes()).hexdigest()[:12]
        
        np.save(self.folder / f"{content_hash}.npy", vec.astype(np.float16))
        
        meta = {
            "text": text,
            "agent": agent_name,
            "hash": content_hash,
            "dim": self.dim,
            "dtype": "float16",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        with open(self.folder / f"{content_hash}.json", 'w') as f:
            json.dump(meta, f, indent=2)
        
        print(f"[VECTOR MESH] {agent_name} wrote 4096-dim vector: {content_hash}")
        return content_hash

    def read(self, content_hash):
        """Load vector from float16 numpy, cast to float32 for math"""
        path = self.folder / f"{content_hash}.npy"
        if path.exists():
            return np.load(path).astype(np.float32)
        return None

    def search(self, query_text, top_k=3):
        """Real cosine similarity search across all stored vectors"""
        query_vec = self.encode(query_text)
        results = []
        
        for meta_file in self.folder.glob("*.json"):
            content_hash = meta_file.stem
            vec = self.read(content_hash)
            if vec is None:
                continue
            
            similarity = float(np.dot(query_vec, vec))
            
            with open(meta_file) as f:
                meta = json.load(f)
            
            results.append({
                "hash": content_hash,
                "similarity": similarity,
                "text": meta.get("text", ""),
                "agent": meta.get("agent", "unknown")
            })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def read_all(self):
        """Read all memories (for compatibility with existing agents)"""
        memories = []
        for meta_file in self.folder.glob("*.json"):
            with open(meta_file) as f:
                memories.append(json.load(f))
        return memories
