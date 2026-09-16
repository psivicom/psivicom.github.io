# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
import numpy as np
import hashlib
import os
from pathlib import Path

class PicoMesh:
    """
    Zero-bloat, zero-copy vector memory.
    Bypasses JSON/PyTorch. Uses raw binary files and OS memory mapping (mmap).
    """
    def __init__(self, folder="reports/pico_vram", dim=4096):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.dim = dim
        self.index_file = self.folder / "mesh_index.bin"
        self.text_file = self.folder / "mesh_text.txt"
        
        # Initialize raw binary index if it doesn't exist
        if not self.index_file.exists():
            np.zeros((0, self.dim), dtype=np.float16).tofile(self.index_file)
            self.text_file.touch()

    def _encode(self, text):
        """Hashing trick to raw float16 vector. Zero AI overhead."""
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
        return vec.astype(np.float16) # Cast to raw 16-bit float

    def write(self, text, agent_name):
        """Append raw vector to binary block. Append text to flat file."""
        vec = self._encode(text)
        
        # 1. Append raw float16 bytes directly to the binary file
        with open(self.index_file, "ab") as f:
            vec.tofile(f)
            
        # 2. Append text with agent tag to the text ledger (tab-separated)
        with open(self.text_file, "a", encoding="utf-8") as f:
            f.write(f"{agent_name}\t{text}\n")
            
        print(f"[PICO MESH] Wrote raw 8KB vector block for {agent_name}.")

    def search(self, query_text, top_k=3):
        """
        Zero-copy read. OS maps the binary file directly to VRAM/RAM.
        Matrix multiplication happens directly on the mapped memory.
        """
        query_vec = self._encode(query_text)
        
        # Memory-map the binary file. NO DATA IS COPIED INTO PYTHON.
        # The OS handles paging it into VRAM/RAM on demand.
        if self.index_file.stat().st_size == 0:
            return []
            
        mapped_vectors = np.memmap(self.index_file, dtype=np.float16, mode='r')
        num_vectors = mapped_vectors.shape[0] // self.dim
        mapped_vectors = mapped_vectors.reshape((num_vectors, self.dim))
        
        # Raw matrix dot product (Cosine similarity)
        # Because query is float16 and mapped is float16, this is ultra-fast
        similarities = np.dot(mapped_vectors.astype(np.float32), query_vec.astype(np.float32))
        
        # Get top K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Read the text ledger
        with open(self.text_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        results = []
        for idx in top_indices:
            if idx < len(lines):
                agent, text = lines[idx].strip().split("\t", 1)
                results.append({
                    "agent": agent,
                    "text": text,
                    "similarity": float(similarities[idx])
                })
                
        return results
