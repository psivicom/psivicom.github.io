# src/mesh/vram_mesh.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import logging
from typing import Dict, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class VRAMBlock:
    address: int
    size: int
    agent_id: Optional[str]
    allocated_time: float

class VRAMMesh:
    def __init__(self, total_vram_bytes: int = 8 * 1024 * 1024 * 1024):
        self.total_vram = total_vram_bytes
        self.allocated_blocks: Dict[int, VRAMBlock] = {}
        self.free_blocks = [(0, total_vram_bytes)]
        self.next_address = 0x1000
        logger.info(f"VRAM Mesh initialized with {total_vram_bytes / (1024**3):.2f} GB")
    
    def allocate(self, size_bytes: int, agent_id: Optional[str] = None) -> int:
        address = self.next_address
        self.next_address += size_bytes
        self.allocated_blocks[address] = VRAMBlock(address=address, size=size_bytes, agent_id=agent_id, allocated_time=time.time())
        return address
    
    def free(self, address: int) -> bool:
        if address in self.allocated_blocks:
            del self.allocated_blocks[address]
            return True
        return False
    
    def get_stats(self) -> Dict:
        total_allocated = sum(block.size for block in self.allocated_blocks.values())
        return {
            "total_vram": self.total_vram,
            "allocated": total_allocated,
            "free": self.total_vram - total_allocated,
            "utilization_percent": (total_allocated / self.total_vram) * 100,
            "num_allocations": len(self.allocated_blocks)
        }
