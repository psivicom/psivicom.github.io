# src/automation/auto_integrator.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette
# RFC 1001 Compliant — PSIVI Open Science Hub

"""
Auto-Integrator: Runtime automation layer that dynamically wires the 
Mesh Factory, Router, Governor, and Provisioner together.

Resolves architectural gaps automatically:
1. Auto-registers dynamically spawned agents into the Mesh Router.
2. Auto-intercepts all routed .psvc containers through the Mesh Governor.
3. Auto-provisions .psvc shards to the correct tiered mesh based on mathematical state.
"""

import logging
import functools
from typing import Callable, Any, Dict, Optional
from psvc_containers import PicoContainer, deserialize_psvc

logger = logging.getLogger(__name__)


# ============================================================================
# AUTOMATION 1: Auto-Registration Registry (Resolves Focus Area 1)
# ============================================================================

class MeshRegistry:
    """
    Singleton registry that automatically bridges the Agent Factory and Mesh Router.
    When the Factory spawns an agent, it registers here. The Router polls here.
    """
    _instance = None
    _agents: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MeshRegistry, cls).__new__(cls)
        return cls._instance

    def register_agent(self, agent_id: str, capabilities: list, endpoint: str = "local"):
        """Automatically called by AgentFactory upon successful generation."""
        self._agents[agent_id] = {
            "capabilities": capabilities,
            "endpoint": endpoint,
            "status": "active"
        }
        logger.info(f"[Auto-Register] Agent {agent_id} registered with capabilities: {capabilities}")

    def get_available_agents(self, required_capability: str) -> list:
        """Mesh Router calls this to find who can handle a task."""
        return [
            agent_id for agent_id, meta in self._agents.items()
            if required_capability in meta["capabilities"] and meta["status"] == "active"
        ]

    def deregister_agent(self, agent_id: str):
        if agent_id in self._agents:
            self._agents[agent_id]["status"] = "inactive"
            logger.info(f"[Auto-Deregister] Agent {agent_id} marked inactive")


# ============================================================================
# AUTOMATION 2: Governor Middleware Decorator (Resolves Focus Area 2)
# ============================================================================

def audit_by_governor(route_func: Callable) -> Callable:
    """
    Decorator that automatically intercepts ANY routing function and forces 
    Mesh Governor audit before execution. Zero-trust automation.
    """
    @functools.wraps(route_func)
    def wrapper(container_bytes: bytes, *args, **kwargs) -> bytes:
        # 1. Import here to avoid circular dependencies
        from src.orchestrator.mesh_governor import audit_psvc_container
        
        # 2. AUTOMATED INTERCEPTION: Audit the payload before it moves
        audit_result = audit_psvc_container(container_bytes)
        
        if not audit_result.is_valid:
            logger.error(f"[Governor Block] Routing rejected. Failures: {audit_result.checks_failed}")
            raise PermissionError(
                f"RFC 1001 Violation: Container failed audit. "
                f"Details: {', '.join(audit_result.checks_failed)}"
            )
        
        logger.debug(f"[Governor Pass] Container {audit_result.container_id} cleared for routing.")
        
        # 3. Execute the actual routing
        return route_func(container_bytes, *args, **kwargs)
        
    return wrapper


# ============================================================================
# AUTOMATION 3: Dynamic Provisioner Logic (Resolves Focus Area 3)
# ============================================================================

class AutoProvisioner:
    """
    Automatically evaluates .psvc mathematical state and routes to the 
    optimal storage tier without hardcoded rules.
    """
    
    @staticmethod
    def evaluate_and_route(container: PicoContainer) -> str:
        """
        Reads the .psvc container's mathematical state and automatically 
        determines the optimal mesh tier.
        
        Returns: "vram", "pico", "vector", or "seed"
        """
        math_state = container.payload.math_state
        tensor_size_bytes = len(container.payload.tensor_bytes)
        
        # Automation Rule 1: High FLOPs + Small Size = Hot VRAM (Active Compute)
        if math_state.flops_estimate > 1_000_000 and tensor_size_bytes < 1_048_576:  # < 1MB
            logger.debug(f"[Auto-Provision] Routing {container.header.shard_id} to VRAM Mesh (High FLOPs)")
            return "vram"
            
        # Automation Rule 2: Large Tensor + Distributed Shard ID = Pico Mesh (Distributed Cache)
        if "shard" in container.header.content_type and tensor_size_bytes > 524_288:  # > 512KB
            logger.debug(f"[Auto-Provision] Routing {container.header.shard_id} to Pico Mesh (Distributed)")
            return "pico"
            
        # Automation Rule 3: Final Synthesis or Large Persistent Data = Vector Mesh
        if container.header.content_type in ["synthesized_report", "persistent_vector"]:
            logger.debug(f"[Auto-Provision] Routing {container.header.shard_id} to Vector Mesh (Persistent)")
            return "vector"
            
        # Automation Rule 4: Root operations with complete provenance = Seed Mesh
        if container.receipt.parent_receipt_hash is None and container.header.content_type == "root_archive":
            logger.debug(f"[Auto-Provision] Routing {container.header.shard_id} to Seed Mesh (Immutable)")
            return "seed"
            
        # Fallback: Default to persistent vector mesh
        logger.warning(f"[Auto-Provision] No specific rule matched for {container.header.shard_id}. Defaulting to Vector Mesh.")
        return "vector"


# ============================================================================
# INITIALIZATION HOOK
# ============================================================================

def auto_wire_system(router_instance: Any, factory_instance: Any):
    """
    Call this once at system startup. It dynamically patches the router 
    and factory to use the automation layer.
    """
    logger.info("🔌 Auto-Integrator: Wiring system components...")
    
    # 1. Patch Mesh Router to use Governor Middleware
    if hasattr(router_instance, 'route_container'):
        original_route = router_instance.route_container
        router_instance.route_container = audit_by_governor(original_route)
        logger.info("  ✓ Mesh Router patched with Governor Audit Middleware")
    
    # 2. Link Factory to Registry (Assuming factory has a hook or we monkey-patch)
    if hasattr(factory_instance, 'generate_agent'):
        original_generate = factory_instance.generate_agent
        
        @functools.wraps(original_generate)
        def auto_registering_generate(*args, **kwargs):
            agent_class = original_generate(*args, **kwargs)
            if agent_class:
                # Instantiate to get ID and capabilities
                temp_agent = agent_class()
                MeshRegistry().register_agent(
                    agent_id=temp_agent.agent_id,
                    capabilities=temp_agent.capabilities
                )
            return agent_class
            
        factory_instance.generate_agent = auto_registering_generate
        logger.info("  ✓ Agent Factory patched with Auto-Registration")
    
    logger.info("✅ Auto-Integrator: System wiring complete. Zero-trust and auto-routing enabled.")
