"""
AETHER VANGUARD - Pico Worker Node (Volunteer Sidecar)
License: EUPL 1.2
Purpose: Manages local VRAM, receives vector shards, and performs distributed attention.
"""
import asyncio
import websockets
import json
import torch
import psutil

class PicoWorker:
    def __init__(self, orchestrator_url: str, worker_id: str):
        self.orchestrator_url = orchestrator_url
        self.worker_id = worker_id
        self.vram_capacity = self._get_vram_capacity()
        self.local_vram_store = {} # Simulating VRAM allocation
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _get_vram_capacity(self) -> int:
        """Queries host hardware to report available VRAM/RAM to the mesh."""
        if torch.cuda.is_available():
            return torch.cuda.get_device_properties(0).total_memory / (1024 * 1024) # MB
        return psutil.virtual_memory().total / (1024 * 1024) # Fallback to RAM

    async def listen_for_pixels(self):
        """Connects to the AETHER mesh protocol and listens for tensor assignments."""
        print(f"[{self.worker_id}] Booting AetherCore Sidecar. VRAM Capacity: {self.vram_capacity:.0f}MB")
        
        async with websockets.connect(self.orchestrator_url) as websocket:
            await websocket.send(json.dumps({
                "action": "REGISTER_NODE",
                "worker_id": self.worker_id,
                "vram_dim_mb": self.vram_capacity
            }))
            
            async for message in websocket:
                data = json.loads(message)
                if data["action"] == "ASSIGN_PIXEL_SHARD":
                    self._load_shard_to_vram(data)
                elif data["action"] == "CROSS_ATTENTION_REQUEST":
                    await self._compute_dot_product(websocket, data)

    def _load_shard_to_vram(self, payload: dict):
        """Deserializes the vector pixel and pins it to local memory."""
        pixel_id = payload["pixel_id"]
        # In production, this uses torch.load or custom binary deserialization
        shard_tensor = torch.tensor(payload["tensor_data"]).to(self.device)
        self.local_vram_store[pixel_id] = shard_tensor
        print(f"[{self.worker_id}] Loaded Vector Pixel {pixel_id} into VRAM. Shape: {shard_tensor.shape}")

    async def _compute_dot_product(self, websocket, request: dict):
        """
        Bypasses text entirely. Computes mathematical similarity against 
        another node's vector pixel in pure latent space.
        """
        pixel_id = request["target_pixel_id"]
        query_vector = torch.tensor(request["query_tensor"]).to(self.device)
        
        if pixel_id in self.local_vram_store:
            stored_pixel = self.local_vram_store[pixel_id]
            # Distributed Attention: Local dot product
            attention_score = torch.dot(query_vector.flatten(), stored_pixel.flatten())
            
            await websocket.send(json.dumps({
                "action": "ATTENTION_RESULT",
                "pixel_id": pixel_id,
                "score": attention_score.item(),
                "worker_id": self.worker_id
            }))

if __name__ == "__main__":
    asyncio.run(PicoWorker("ws://orchestrator:8765", "NODE_GOLDSTREAM_01").listen_for_pixels())
