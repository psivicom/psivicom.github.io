# src/agents/forage_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

import torch
import numpy as np
from src.base.base_agent import BaseAgent, AgentLayer
from src.core.vector_math import embed_tokens, MathState
from src.core.psvc_builder import build_psvc_container, serialize_psvc

class ForageAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "forage_agent"):
        # Inject pure functions as capabilities
        super().__init__(name=name, capabilities={
            "fetch_weather": self._fetch_weather,
            "embed_weather_data": self._embed_weather_data
        })
        # Simulated embedding matrix for demonstration
        self.embedding_matrix = torch.randn(1000, 512, dtype=torch.float16)

    def _fetch_weather(self, location: str) -> dict:
        return {"location": location, "temp": 22.5, "tokens": [12, 45, 99]}

    def _embed_weather_data(self, data: dict) -> bytes:
        """Functional pipeline: Data -> Math -> .psvc Container"""
        tokens = torch.tensor([data["tokens"]])
        
        # 1. Pure Math Operation (VRAM)
        vectors, math_state = embed_tokens(tokens, self.embedding_matrix)
        
        # 2. Seal the operation
        receipt = self.seal("embed_weather", {"location": data["location"]})
        
        # 3. Build Immutable .psvc Container
        container = build_psvc_container(
            tensor=vectors,
            math_state=math_state,
            receipt=receipt,
            content_type="weather_vector_shard"
        )
        
        # 4. Serialize for Mesh Transmission
        return serialize_psvc(container)

    def execute(self, location: str) -> bytes:
        data = self.execute_capability("fetch_weather", location)
        return self.execute_capability("embed_weather_data", data)
