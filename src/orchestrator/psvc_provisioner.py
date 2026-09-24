# src/orchestrator/psvc_provisioner.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import logging
from typing import Dict, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PSVCHandle:
    agent_id: str
    vram_address: int
    size_bytes: int
    growth_margin: float

class ElasticPSVCProvisioner:
    def __init__(self, vram_mesh, growth_margin_default: float = 0.2):
        self.mesh = vram_mesh
        self.registry: Dict[str, PSVCHandle] = {}
        self.growth_margin_default = growth_margin_default

    def allocate(self, agent_id: str, initial_size: int, growth_margin: Optional[float] = None) -> PSVCHandle:
        if growth_margin is None:
            growth_margin = self.growth_margin_default
        if agent_id in self.registry:
            raise ValueError(f"Agent {agent_id} already allocated")
        total_size = int(initial_size * (1 + growth_margin))
        vram_address = self.mesh.allocate(total_size)
        handle = PSVCHandle(agent_id=agent_id, vram_address=vram_address, size_bytes=total_size, growth_margin=growth_margin)
        self.registry[agent_id] = handle
        logger.info(f"Allocated {total_size} bytes for {agent_id}")
        return handle

    def get_handle(self, agent_id: str) -> Optional[PSVCHandle]:
        return self.registry.get(agent_id)
