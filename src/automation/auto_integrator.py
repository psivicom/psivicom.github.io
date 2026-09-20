# src/automation/auto_integrator.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette
# RFC 1001 Compliant — PSIVI Open Science Hub

"""
Auto-Integrator: Production-grade runtime automation layer that dynamically wires
the Mesh Factory, Router, Governor, and Provisioner together.

Automatically resolves:
1. Agent registration when dynamically spawned
2. Zero-trust routing through Governor audit
3. Intelligent provisioning based on mathematical state
"""

import logging
import functools
import threading
from typing import Callable, Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import time

from psvc_containers import PicoContainer, deserialize_psvc, verify_container

logger = logging.getLogger(__name__)


# ============================================================================
# AUTOMATION 1: Auto-Registration Registry
# ============================================================================

@dataclass
class AgentMetadata:
    """Metadata for registered agents."""
    agent_id: str
    capabilities: List[str]
    endpoint: str
    registered_at: float = field(default_factory=time.time)
    status: str = "active"
    last_seen: float = field(default_factory=time.time)
    request_count: int = 0


class MeshRegistry:
    """
    Thread-safe singleton registry that automatically bridges Agent Factory and Mesh Router.
    """
    _instance = None
    _lock = threading.Lock()
    _agents: Dict[str, AgentMetadata] = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MeshRegistry, cls).__new__(cls)
        return cls._instance

    def register_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        endpoint: str = "local"
    ) -> None:
        """Register a dynamically spawned agent."""
        with self._lock:
            self._agents[agent_id] = AgentMetadata(
                agent_id=agent_id,
                capabilities=capabilities,
                endpoint=endpoint
            )
            logger.info(
                f"[Auto-Register] Agent {agent_id} registered | "
                f"Capabilities: {capabilities} | Endpoint: {endpoint}"
            )

    def deregister_agent(self, agent_id: str) -> None:
        """Mark an agent as inactive."""
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id].status = "inactive"
                logger.info(f"[Auto-Deregister] Agent {agent_id} marked inactive")

    def update_heartbeat(self, agent_id: str) -> None:
        """Update agent's last seen timestamp."""
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id].last_seen = time.time()

    def increment_request_count(self, agent_id: str) -> None:
        """Increment request counter for an agent."""
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id].request_count += 1

    def get_available_agents(self, required_capability: str) -> List[str]:
        """Get all active agents with the required capability."""
        with self._lock:
            return [
                agent_id for agent_id, meta in self._agents.items()
                if required_capability in meta.capabilities and meta.status == "active"
            ]

    def get_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        """Get metadata for a specific agent."""
        with self._lock:
            return self._agents.get(agent_id)

    def get_all_agents(self) -> Dict[str, AgentMetadata]:
        """Get all registered agents."""
        with self._lock:
            return self._agents.copy()

    def cleanup_stale_agents(self, timeout_seconds: float = 300.0) -> int:
        """Remove agents that haven't been seen recently."""
        with self._lock:
            now = time.time()
            stale_agents = [
                agent_id for agent_id, meta in self._agents.items()
                if now - meta.last_seen > timeout_seconds
            ]
            for agent_id in stale_agents:
                self._agents[agent_id].status = "stale"
                logger.warning(f"[Cleanup] Agent {agent_id} marked stale (no heartbeat for {timeout_seconds}s)")
            return len(stale_agents)

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            total = len(self._agents)
            active = sum(1 for m in self._agents.values() if m.status == "active")
            inactive = sum(1 for m in self._agents.values() if m.status == "inactive")
            stale = sum(1 for m in self._agents.values() if m.status == "stale")
            total_requests = sum(m.request_count for m in self._agents.values())
            
            return {
                "total_agents": total,
                "active_agents": active,
                "inactive_agents": inactive,
                "stale_agents": stale,
                "total_requests": total_requests
            }


# ============================================================================
# AUTOMATION 2: Governor Middleware
# ============================================================================

class GovernorAuditError(Exception):
    """Raised when Governor audit fails."""
    pass


def audit_by_governor(route_func: Callable) -> Callable:
    """
    Decorator that automatically intercepts routing functions and enforces
    Mesh Governor audit before execution. Zero-trust automation.
    """
    @functools.wraps(route_func)
    def wrapper(container_bytes: bytes, *args, **kwargs) -> bytes:
        try:
            # Import here to avoid circular dependencies
            from src.orchestrator.mesh_governor import audit_psvc_container
            
            # Audit the payload
            audit_result = audit_psvc_container(container_bytes)
            
            if not audit_result.is_valid:
                error_msg = f"RFC 1001 Violation: {', '.join(audit_result.checks_failed)}"
                logger.error(f"[Governor Block] {error_msg}")
                raise GovernorAuditError(error_msg)
            
            logger.debug(
                f"[Governor Pass] Container {audit_result.container_id} | "
                f"Checks passed: {len(audit_result.checks_passed)}"
            )
            
            # Execute the actual routing
            return route_func(container_bytes, *args, **kwargs)
            
        except GovernorAuditError:
            raise
        except Exception as e:
            logger.error(f"[Governor] Unexpected error during audit: {e}")
            raise GovernorAuditError(f"Audit failed: {e}")
    
    return wrapper


def audit_and_track(route_func: Callable) -> Callable:
    """
    Enhanced decorator that audits AND tracks the routing in the registry.
    """
    @functools.wraps(route_func)
    def wrapper(container_bytes: bytes, target_agent_id: str, *args, **kwargs) -> bytes:
        # 1. Audit
        from src.orchestrator.mesh_governor import audit_psvc_container
        audit_result = audit_psvc_container(container_bytes)
        
        if not audit_result.is_valid:
            raise GovernorAuditError(f"RFC 1001 Violation: {', '.join(audit_result.checks_failed)}")
        
        # 2. Track in registry
        registry = MeshRegistry()
        registry.update_heartbeat(target_agent_id)
        registry.increment_request_count(target_agent_id)
        
        # 3. Route
        return route_func(container_bytes, target_agent_id, *args, **kwargs)
    
    return wrapper


# ============================================================================
# AUTOMATION 3: Dynamic Provisioner
# ============================================================================

@dataclass
class ProvisioningDecision:
    """Result of automated provisioning evaluation."""
    target_tier: str
    confidence: float
    reason: str
    timestamp: float = field(default_factory=time.time)


class AutoProvisioner:
    """
    Automatically evaluates .psvc mathematical state and routes to the
    optimal storage tier based on data-driven rules.
    """
    
    # Thresholds (can be loaded from config)
    HIGH_FLOPS_THRESHOLD = 1_000_000
    LARGE_TENSOR_THRESHOLD = 524_288  # 512KB
    SMALL_TENSOR_THRESHOLD = 10_240   # 10KB
    
    @staticmethod
    def evaluate(container: PicoContainer) -> ProvisioningDecision:
        """
        Evaluate container and determine optimal storage tier.
        
        Returns:
            ProvisioningDecision with tier, confidence, and reason
        """
        math_state = container.payload.math_state
        tensor_size_bytes = len(container.payload.tensor_bytes)
        content_type = container.header.content_type
        has_parent = container.receipt.parent_receipt_hash is not None
        
        # Rule 1: Hot compute path (High FLOPs + Small Size)
        if (math_state.flops_estimate > AutoProvisioner.HIGH_FLOPS_THRESHOLD and
            tensor_size_bytes < AutoProvisioner.LARGE_TENSOR_THRESHOLD):
            return ProvisioningDecision(
                target_tier="vram",
                confidence=0.95,
                reason=f"High FLOPs ({math_state.flops_estimate}) + Small size ({tensor_size_bytes}B) = Active compute"
            )
        
        # Rule 2: Distributed cache (Sharded + Medium-Large Size)
        if ("shard" in content_type and
            tensor_size_bytes > AutoProvisioner.SMALL_TENSOR_THRESHOLD):
            return ProvisioningDecision(
                target_tier="pico",
                confidence=0.85,
                reason=f"Sharded content ({content_type}) + Size {tensor_size_bytes}B = Distributed cache"
            )
        
        # Rule 3: Persistent storage (Synthesis or large persistent data)
        if content_type in ["synthesized_report", "persistent_vector", "aggregated_result"]:
            return ProvisioningDecision(
                target_tier="vector",
                confidence=0.90,
                reason=f"Content type {content_type} = Persistent storage"
            )
        
        # Rule 4: Immutable archive (Root operations with complete provenance)
        if (not has_parent and
            content_type in ["root_archive", "immutable_snapshot", "seed_data"]):
            return ProvisioningDecision(
                target_tier="seed",
                confidence=0.98,
                reason="Root operation with complete provenance = Immutable archive"
            )
        
        # Rule 5: VRAM for active attention operations
        if "attention" in content_type.lower() or "embedding" in content_type.lower():
            return ProvisioningDecision(
                target_tier="vram",
                confidence=0.88,
                reason=f"Active operation ({content_type}) = VRAM for low-latency access"
            )
        
        # Default fallback
        logger.warning(
            f"[Auto-Provision] No specific rule matched for {container.header.shard_id}. "
            f"Defaulting to vector mesh."
        )
        return ProvisioningDecision(
            target_tier="vector",
            confidence=0.50,
            reason="Default fallback - no specific rule matched"
        )
    
    @staticmethod
    def route_container(container: PicoContainer, mesh_tiers: Dict[str, Any]) -> str:
        """
        Evaluate and route container to appropriate tier.
        
        Args:
            container: The .psvc container to route
            mesh_tiers: Dictionary of tier handlers (vram, pico, vector, seed)
            
        Returns:
            The tier where the container was stored
        """
        decision = AutoProvisioner.evaluate(container)
        
        logger.info(
            f"[Auto-Provision] {container.header.shard_id} -> {decision.target_tier} | "
            f"Confidence: {decision.confidence:.2f} | Reason: {decision.reason}"
        )
        
        # Route to the appropriate tier handler
        tier_handler = mesh_tiers.get(decision.target_tier)
        if tier_handler:
            tier_handler.store(container)
        else:
            logger.error(f"[Auto-Provision] No handler for tier: {decision.target_tier}")
            raise ValueError(f"No handler registered for tier: {decision.target_tier}")
        
        return decision.target_tier


# ============================================================================
# SYSTEM WIRING
# ============================================================================

class AutoIntegrator:
    """
    Main integrator that wires all automation components together.
    Call auto_wire_system() once at startup.
    """
    
    _wired = False
    _lock = threading.Lock()
    
    @classmethod
    def auto_wire_system(
        cls,
        router_instance: Any,
        factory_instance: Any,
        mesh_tiers: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Wire the entire system with automation. Call once at startup.
        
        Args:
            router_instance: MeshRouter instance
            factory_instance: LLMAgentGenerator instance
            mesh_tiers: Optional dictionary of tier handlers for AutoProvisioner
        """
        with cls._lock:
            if cls._wired:
                logger.warning("[Auto-Integrator] System already wired. Skipping.")
                return
            
            logger.info("🔌 [Auto-Integrator] Wiring system components...")
            
            # 1. Patch Mesh Router with Governor middleware
            if hasattr(router_instance, 'route_container'):
                original_route = router_instance.route_container
                router_instance.route_container = audit_and_track(original_route)
                logger.info("  ✓ Mesh Router patched with Governor Audit + Tracking")
            
            # 2. Patch Agent Factory with auto-registration
            if hasattr(factory_instance, 'generate_agent'):
                original_generate = factory_instance.generate_agent
                
                @functools.wraps(original_generate)
                def auto_registering_generate(*args, **kwargs):
                    agent_class = original_generate(*args, **kwargs)
                    if agent_class:
                        try:
                            # Instantiate to get ID and capabilities
                            temp_agent = agent_class()
                            MeshRegistry().register_agent(
                                agent_id=temp_agent.agent_id,
                                capabilities=temp_agent.capabilities,
                                endpoint="local"
                            )
                        except Exception as e:
                            logger.error(f"[Auto-Register] Failed to register agent: {e}")
                    return agent_class
                
                factory_instance.generate_agent = auto_registering_generate
                logger.info("  ✓ Agent Factory patched with Auto-Registration")
            
            # 3. Store mesh tiers for provisioning
            if mesh_tiers:
                cls._mesh_tiers = mesh_tiers
                logger.info(f"  ✓ Mesh tiers registered: {list(mesh_tiers.keys())}")
            
            cls._wired = True
            logger.info("✅ [Auto-Integrator] System wiring complete. Zero-trust and auto-routing enabled.")
    
    @classmethod
    def is_wired(cls) -> bool:
        """Check if system has been wired."""
        return cls._wired
    
    @classmethod
    def get_system_status(cls) -> Dict[str, Any]:
        """Get comprehensive system status."""
        registry = MeshRegistry()
        
        return {
            "wired": cls._wired,
            "registry_stats": registry.get_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def auto_wire_system(
    router_instance: Any,
    factory_instance: Any,
    mesh_tiers: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convenience function to wire the system.
    Equivalent to AutoIntegrator.auto_wire_system()
    """
    AutoIntegrator.auto_wire_system(router_instance, factory_instance, mesh_tiers)


def get_registry() -> MeshRegistry:
    """Get the singleton MeshRegistry instance."""
    return MeshRegistry()


def provision_container(container: PicoContainer, mesh_tiers: Dict[str, Any]) -> str:
    """
    Convenience function to provision a container.
    """
    return AutoProvisioner.route_container(container, mesh_tiers)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the Auto-Integrator.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Mock instances for demonstration
    class MockRouter:
        def route_container(self, container_bytes: bytes, target_agent_id: str) -> bytes:
            logger.info(f"Routing to {target_agent_id}")
            return container_bytes
    
    class MockFactory:
        def generate_agent(self, capability: str, problem: str, inputs: dict, outputs: dict, parent: str):
            logger.info(f"Generating agent for {capability}")
            
            # Mock agent class
            class MockAgent:
                def __init__(self):
                    self.agent_id = f"mock_agent_{capability}"
                    self.capabilities = [capability]
            
            return MockAgent
    
    # Initialize
    router = MockRouter()
    factory = MockFactory()
    
    # Wire the system
    auto_wire_system(router, factory)
    
    # Test auto-registration
    logger.info("\n--- Testing Auto-Registration ---")
    agent_class = factory.generate_agent("parse_radar", "Parse radar data", {}, {}, "root")
    
    # Check registry
    registry = get_registry()
    available = registry.get_available_agents("parse_radar")
    logger.info(f"Available agents for 'parse_radar': {available}")
    
    # Test system status
    status = AutoIntegrator.get_system_status()
    logger.info(f"\nSystem Status: {status}")
    
    logger.info("\n✅ Auto-Integrator demonstration complete!")
