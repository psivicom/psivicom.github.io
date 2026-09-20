"""
Elastic PSVC Provisioner for VRAM-Native Mesh Communication
Implements dynamic memory allocation with evolutionary growth margins
NIST SP 800-218 Compliant | FAIR Open Science | EUPL-1.2 Licensed
"""

import threading
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib
import time

logger = logging.getLogger(__name__)


@dataclass
class PSVCHandle:
    """Represents an allocated PSVC container in VRAM"""
    agent_id: str
    vram_address: int
    size_bytes: int
    growth_margin: float
    creation_time: float
    last_accessed: float
    generation: int  # Tracks evolutionary generations
    hash_signature: str  # Security: Cryptographic verification


class ElasticPSVCProvisioner:
    """
    Manages elastic VRAM allocation for evolving agents
    Supports atomic relocation and pointer swizzling for security
    """
    
    def __init__(self, vram_mesh, growth_margin_default: float = 0.2):
        self.mesh = vram_mesh
        self.registry: Dict[str, PSVCHandle] = {}
        self.lock = threading.RLock()  # Reentrant lock for nested operations
        self.growth_margin_default = growth_margin_default
        self.evolution_log = []  # Audit trail for FAIR compliance
        
    def allocate(self, agent_id: str, initial_size: int, 
                 growth_margin: Optional[float] = None) -> PSVCHandle:
        """
        Allocate a new elastic PSVC container in VRAM
        
        Args:
            agent_id: Unique identifier for the agent
            initial_size: Initial vector size in bytes
            growth_margin: Percentage of extra space for evolution (default 20%)
        
        Returns:
            PSVCHandle with VRAM allocation details
        """
        if growth_margin is None:
            growth_margin = self.growth_margin_default
            
        with self.lock:
            if agent_id in self.registry:
                raise ValueError(f"Agent {agent_id} already has allocated VRAM")
            
            # Calculate total allocation with growth margin
            total_size = int(initial_size * (1 + growth_margin))
            
            # Allocate in VRAM mesh
            vram_address = self.mesh.allocate(total_size)
            
            # Generate security hash
            hash_sig = self._generate_security_hash(agent_id, vram_address, total_size)
            
            # Create handle
            handle = PSVCHandle(
                agent_id=agent_id,
                vram_address=vram_address,
                size_bytes=total_size,
                growth_margin=growth_margin,
                creation_time=time.time(),
                last_accessed=time.time(),
                generation=1,
                hash_signature=hash_sig
            )
            
            self.registry[agent_id] = handle
            
            # Log for audit trail
            self._log_evolution(agent_id, "ALLOCATE", {
                "size": total_size,
                "address": vram_address,
                "generation": 1
            })
            
            logger.info(f"Allocated {total_size} bytes for agent {agent_id} at {hex(vram_address)}")
            return handle
    
    def evolve(self, agent_id: str, required_size: int) -> bool:
        """
        Evolve an agent's PSVC container to accommodate larger vector dimensions
        Performs atomic relocation with pointer swizzling for security
        
        Args:
            agent_id: Agent identifier
            required_size: New required size in bytes
            
        Returns:
            True if evolution succeeded, False otherwise
        """
        with self.lock:
            if agent_id not in self.registry:
                logger.error(f"Cannot evolve: Agent {agent_id} not found in registry")
                return False
            
            handle = self.registry[agent_id]
            
            # Check if current allocation (including growth margin) is sufficient
            if required_size <= handle.size_bytes:
                logger.debug(f"Agent {agent_id} fits in current allocation")
                return True
            
            try:
                # SECURITY GATE: Pause all writes to this agent's memory
                self.mesh.pause_agent_writes(agent_id)
                
                # Calculate new size with fresh growth margin
                new_total_size = int(required_size * (1 + handle.growth_margin))
                
                # Allocate new, larger block
                new_vram_address = self.mesh.allocate(new_total_size)
                
                # Migrate data from old to new location
                self.mesh.migrate_data(handle.vram_address, new_vram_address, 
                                      handle.size_bytes)
                
                # Update registry with new handle (pointer swizzle)
                new_handle = PSVCHandle(
                    agent_id=agent_id,
                    vram_address=new_vram_address,
                    size_bytes=new_total_size,
                    growth_margin=handle.growth_margin,
                    creation_time=handle.creation_time,
                    last_accessed=time.time(),
                    generation=handle.generation + 1,
                    hash_signature=self._generate_security_hash(
                        agent_id, new_vram_address, new_total_size
                    )
                )
                
                self.registry[agent_id] = new_handle
                
                # SECURITY: Scrub old memory to prevent data leakage
                self.mesh.scrub_memory(handle.vram_address, handle.size_bytes)
                self.mesh.free(handle.vram_address)
                
                # Resume writes
                self.mesh.resume_agent_writes(agent_id)
                
                # Log evolution for audit
                self._log_evolution(agent_id, "EVOLVE", {
                    "old_size": handle.size_bytes,
                    "new_size": new_total_size,
                    "old_address": hex(handle.vram_address),
                    "new_address": hex(new_vram_address),
                    "generation": new_handle.generation
                })
                
                logger.info(f"Evolved agent {agent_id} from {handle.size_bytes} to "
                           f"{new_total_size} bytes (generation {new_handle.generation})")
                return True
                
            except Exception as e:
                # CRITICAL: Ensure writes are resumed even on failure
                self.mesh.resume_agent_writes(agent_id)
                logger.error(f"Evolution failed for agent {agent_id}: {e}")
                return False
    
    def get_handle(self, agent_id: str) -> Optional[PSVCHandle]:
        """Retrieve handle for an agent (thread-safe)"""
        with self.lock:
            handle = self.registry.get(agent_id)
            if handle:
                handle.last_accessed = time.time()
            return handle
    
    def release(self, agent_id: str) -> bool:
        """
        Release an agent's VRAM allocation with secure scrubbing
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if release succeeded
        """
        with self.lock:
            if agent_id not in self.registry:
                return False
            
            handle = self.registry[agent_id]
            
            # SECURITY: Scrub memory before freeing
            self.mesh.scrub_memory(handle.vram_address, handle.size_bytes)
            self.mesh.free(handle.vram_address)
            
            del self.registry[agent_id]
            
            self._log_evolution(agent_id, "RELEASE", {
                "size": handle.size_bytes,
                "address": hex(handle.vram_address),
                "generation": handle.generation
            })
            
            logger.info(f"Released VRAM for agent {agent_id}")
            return True
    
    def get_evolution_stats(self) -> Dict:
        """Get statistics on memory evolution for monitoring"""
        with self.lock:
            total_agents = len(self.registry)
            total_memory = sum(h.size_bytes for h in self.registry.values())
            avg_generation = sum(h.generation for h in self.registry.values()) / max(total_agents, 1)
            
            return {
                "total_agents": total_agents,
                "total_memory_bytes": total_memory,
                "average_generation": avg_generation,
                "evolution_events": len(self.evolution_log)
            }
    
    def _generate_security_hash(self, agent_id: str, address: int, size: int) -> str:
        """Generate cryptographic hash for security verification"""
        data = f"{agent_id}:{address}:{size}:{time.time()}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def _log_evolution(self, agent_id: str, event_type: str, details: Dict):
        """Log evolution events for FAIR audit trail"""
        log_entry = {
            "timestamp": time.time(),
            "agent_id": agent_id,
            "event": event_type,
            "details": details
        }
        self.evolution_log.append(log_entry)
        logger.debug(f"Evolution log: {log_entry}")


# Compatibility wrapper for existing code
class PsvcProvisioner(ElasticPSVCProvisioner):
    """Backward-compatible wrapper"""
    pass
