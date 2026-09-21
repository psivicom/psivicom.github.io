"""
VRAM Mesh Manager for In-Memory PSVC Communication
Handles elastic allocation, atomic operations, and security enforcement
NIST SP 800-218 Compliant | FAIR Open Science | EUPL-1.2 Licensed
"""

import threading
import logging
from typing import Dict, Set, Optional
from dataclasses import dataclass
import ctypes
import time

logger = logging.getLogger(__name__)


@dataclass
class VRAMBlock:
    """Represents an allocated block in VRAM"""
    address: int
    size: int
    agent_id: Optional[str]
    allocated_time: float
    is_paused: bool = False


class VRAMMesh:
    """
    Manages VRAM allocation for the mesh network
    Supports elastic containers with atomic operations
    """
    
    def __init__(self, total_vram_bytes: int = 8 * 1024 * 1024 * 1024):  # 8GB default
        self.total_vram = total_vram_bytes
        self.allocated_blocks: Dict[int, VRAMBlock] = {}
        self.free_blocks = [(0, total_vram_bytes)]  # List of (start, size) tuples
        self.agent_paused: Set[str] = set()
        self.lock = threading.RLock()
        
        # Simulated VRAM (in production, this would interface with CUDA/cuMemAlloc)
        self._vram_simulator = bytearray(total_vram_bytes)
        
        logger.info(f"VRAM Mesh initialized with {total_vram_bytes / (1024**3):.2f} GB")
    
    def allocate(self, size_bytes: int, agent_id: Optional[str] = None) -> int:
        """
        Allocate a block of VRAM
        
        Args:
            size_bytes: Size to allocate in bytes
            agent_id: Optional agent identifier for tracking
            
        Returns:
            VRAM address (offset) of allocated block
            
        Raises:
            MemoryError: If insufficient VRAM available
        """
        with self.lock:
            # Find first-fit block
            for i, (start, free_size) in enumerate(self.free_blocks):
                if free_size >= size_bytes:
                    # Allocate from this block
                    address = start
                    
                    # Update free list
                    remaining = free_size - size_bytes
                    if remaining > 0:
                        self.free_blocks[i] = (start + size_bytes, remaining)
                    else:
                        self.free_blocks.pop(i)
                    
                    # Create block record
                    block = VRAMBlock(
                        address=address,
                        size=size_bytes,
                        agent_id=agent_id,
                        allocated_time=time.time()
                    )
                    self.allocated_blocks[address] = block
                    
                    logger.debug(f"Allocated {size_bytes} bytes at {hex(address)} for {agent_id}")
                    return address
            
            # No suitable block found
            raise MemoryError(f"Insufficient VRAM: requested {size_bytes} bytes, "
                            f"largest free block: {max((s for _, s in self.free_blocks), default=0)} bytes")
    
    def free(self, address: int) -> bool:
        """
        Free a VRAM block
        
        Args:
            address: VRAM address to free
            
        Returns:
            True if freed successfully
        """
        with self.lock:
            if address not in self.allocated_blocks:
                logger.warning(f"Attempted to free unallocated address {hex(address)}")
                return False
            
            block = self.allocated_blocks[address]
            
            # Add to free list (simple coalescing)
            self.free_blocks.append((address, block.size))
            self.free_blocks.sort()  # Keep sorted for better allocation
            
            # Merge adjacent free blocks
            self._coalesce_free_blocks()
            
            del self.allocated_blocks[address]
            
            logger.debug(f"Freed {block.size} bytes at {hex(address)}")
            return True
    
    def migrate_data(self, src_address: int, dst_address: int, size_bytes: int) -> bool:
        """
        Migrate data from one VRAM location to another (atomic operation)
        
        Args:
            src_address: Source VRAM address
            dst_address: Destination VRAM address
            size_bytes: Number of bytes to migrate
            
        Returns:
            True if migration succeeded
        """
        with self.lock:
            if src_address not in self.allocated_blocks:
                logger.error(f"Source address {hex(src_address)} not allocated")
                return False
            
            if dst_address not in self.allocated_blocks:
                logger.error(f"Destination address {hex(dst_address)} not allocated")
                return False
            
            try:
                # Copy data (in production: cudaMemcpy)
                self._vram_simulator[dst_address:dst_address + size_bytes] = \
                    self._vram_simulator[src_address:src_address + size_bytes]
                
                logger.debug(f"Migrated {size_bytes} bytes from {hex(src_address)} to {hex(dst_address)}")
                return True
                
            except Exception as e:
                logger.error(f"Migration failed: {e}")
                return False
    
    def scrub_memory(self, address: int, size_bytes: int) -> bool:
        """
        Securely scrub memory (zero-fill) for security compliance
        
        Args:
            address: VRAM address to scrub
            size_bytes: Number of bytes to scrub
            
        Returns:
            True if scrubbing succeeded
        """
        with self.lock:
            try:
                # Zero-fill memory (security: prevent data leakage)
                self._vram_simulator[address:address + size_bytes] = b'\x00' * size_bytes
                logger.debug(f"Scrubbed {size_bytes} bytes at {hex(address)}")
                return True
            except Exception as e:
                logger.error(f"Scrubbing failed: {e}")
                return False
    
    def pause_agent_writes(self, agent_id: str) -> bool:
        """
        Pause all write operations to an agent's memory (security gate)
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if pause succeeded
        """
        with self.lock:
            self.agent_paused.add(agent_id)
            logger.debug(f"Paused writes for agent {agent_id}")
            return True
    
    def resume_agent_writes(self, agent_id: str) -> bool:
        """
        Resume write operations to an agent's memory
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if resume succeeded
        """
        with self.lock:
            if agent_id in self.agent_paused:
                self.agent_paused.remove(agent_id)
                logger.debug(f"Resumed writes for agent {agent_id}")
            return True
    
    def is_agent_paused(self, agent_id: str) -> bool:
        """Check if an agent's writes are paused"""
        return agent_id in self.agent_paused
    
    def get_block_info(self, address: int) -> Optional[VRAMBlock]:
        """Get information about an allocated block"""
        return self.allocated_blocks.get(address)
    
    def get_stats(self) -> Dict:
        """Get VRAM utilization statistics"""
        with self.lock:
            total_allocated = sum(block.size for block in self.allocated_blocks.values())
            largest_free = max((size for _, size in self.free_blocks), default=0)
            
            return {
                "total_vram": self.total_vram,
                "allocated": total_allocated,
                "free": self.total_vram - total_allocated,
                "utilization_percent": (total_allocated / self.total_vram) * 100,
                "largest_free_block": largest_free,
                "num_allocations": len(self.allocated_blocks),
                "paused_agents": len(self.agent_paused)
            }
    
    def _coalesce_free_blocks(self):
        """Merge adjacent free blocks to reduce fragmentation"""
        if len(self.free_blocks) <= 1:
            return
        
        merged = [self.free_blocks[0]]
        
        for start, size in self.free_blocks[1:]:
            last_start, last_size = merged[-1]
            
            # Check if blocks are adjacent
            if last_start + last_size == start:
                # Merge
                merged[-1] = (last_start, last_size + size)
            else:
                merged.append((start, size))
        
        self.free_blocks = merged


# Compatibility wrapper
class VramMesh(VRAMMesh):
    """Backward-compatible wrapper"""
    pass
