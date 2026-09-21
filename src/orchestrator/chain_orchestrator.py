# ==============================================================================
# FILE: chain_orchestrator.py
# PATH: psivicom.github.io/chain_orchestrator.py
# DESCRIPTION: Dynamic Chain Orchestrator for Elastic PSVC Mesh
#              Updated to import agents from src/agents/ directory.
# LICENSE: EUPL-1.2 | COMPLIANCE: NIST SP 800-218, FAIR Open Science
# ==============================================================================

import logging
import time
import json
import numpy as np
import sys
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# Ensure root directory is in path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the elastic core infrastructure
from vram_mesh import VRAMMesh
from src.orchestrator.psvc_provisioner import ElasticPSVCProvisioner
from mesh_governor import MeshGovernor
from src.core.vector_pixelizer import VectorPixelizer

# Import agents from their new location
from src.agents.satellite_agent import SatelliteAgent
from src.agents.forage_agent import ForageAgent

logger = logging.getLogger(__name__)


@dataclass
class AgentProfile:
    """Defines the characteristics of an agent in the chain"""
    agent_id: str
    agent_type: str  # "legacy" or "evolving"
    initial_dimensions: int
    initial_memory_bytes: int
    growth_margin: float = 0.2  # Evolving agents get higher margins


@dataclass
class WorkflowStep:
    """A single step in the processing chain"""
    source_agent_id: str
    target_agent_id: str
    operation: str  # e.g., "transform", "multiply", "fuse"
    is_mutable: bool  # Does the target need to mutate/expand the data?


class ChainOrchestrator:
    """
    Manages the execution of multi-agent workflows using the Elastic PSVC system.
    Ensures secure, zero-copy data handoffs between old (legacy) and new (evolving) agents.
    """
    
    def __init__(self, total_vram_gb: float = 8.0):
        logger.info("Initializing Chain Orchestrator with Elastic PSVC Core...")
        
        # 1. Initialize the VRAM-Native Infrastructure
        total_vram_bytes = int(total_vram_gb * 1024 * 1024 * 1024)
        self.vram_mesh = VRAMMesh(total_vram_bytes)
        
        # 2. Initialize the Elastic Provisioner & Governor
        self.provisioner = ElasticPSVCProvisioner(self.vram_mesh)
        self.governor = MeshGovernor(self.vram_mesh, self.provisioner)
        
        # 3. Initialize the Vector Math Engine
        self.pixelizer = VectorPixelizer(self.vram_mesh, self.provisioner, self.governor)
        
        # Registry of active agents in this chain
        self.agents: Dict[str, AgentProfile] = {}
        
        logger.info("Chain Orchestrator initialized. Mesh status: NOMINAL")

    def register_agent(self, profile: AgentProfile) -> bool:
        """Registers an agent and allocates its initial elastic VRAM container"""
        try:
            # Legacy agents get tight margins; evolving agents get elastic margins
            margin = profile.growth_margin if profile.agent_type == "evolving" else 0.05
            
            # Allocate elastic container in VRAM
            self.provisioner.allocate(profile.agent_id, profile.initial_memory_bytes, margin)
            
            # Register with governor for state tracking
            self.governor.register_agent(
                profile.agent_id, 
                profile.initial_dimensions, 
                profile.initial_memory_bytes
            )
            
            self.agents[profile.agent_id] = profile
            logger.info(f"Registered {profile.agent_type} agent: {profile.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {profile.agent_id}: {e}")
            return False

    def execute_workflow(self, steps: List[WorkflowStep]) -> bool:
        """
        Executes the chain of workflow steps.
        Handles the zero-copy handoffs and evolutionary triggers.
        """
        logger.info(f"Starting workflow execution with {len(steps)} steps...")
        start_time = time.time()
        
        for i, step in enumerate(steps):
            logger.info(f"Executing Step {i+1}: {step.source_agent_id} -> {step.target_agent_id} [{step.operation}]")
            
            # SECURITY GATE: Enforce pico protocol before handoff
            if not self.governor.enforce_pico_protocol():
                logger.error("Pico protocol violation detected. Halting workflow.")
                return False
            
            # Perform the zero-copy handoff and vector math
            success = self._execute_handoff(step)
            
            if not success:
                logger.error(f"Workflow failed at step {i+1}.")
                return False
                
        # Finalize and audit
        self._finalize_workflow(start_time)
        return True

    def _execute_handoff(self, step: WorkflowStep) -> bool:
        """
        The core innovation: Zero-copy handoff with elastic evolution.
        """
        source_id = step.source_agent_id
        target_id = step.target_agent_id
        
        # 1. Get source data handle (VRAM pointer)
        source_handle = self.provisioner.get_handle(source_id)
        if not source_handle:
            logger.error(f"Source agent {source_id} has no VRAM handle.")
            return False
            
        # 2. Simulate reading the source vector data from VRAM
        simulated_source_data = np.ones(source_handle.size_bytes // 8, dtype=np.float64)
        
        # 3. Execute vector math on the target agent
        success, result_data = self.pixelizer.execute_vector_math(
            target_id, step.operation, simulated_source_data
        )
        
        if not success:
            logger.error(f"Vector math failed for target {target_id}")
            return False
            
        # 4. Deposit pheromone for the handoff (FAIR audit trail)
        handoff_pheromone = f"handoff:{source_id}->{target_id}:{step.operation}"
        self.governor.deposit_pheromone(target_id, handoff_pheromone)
        
        return True

    def _finalize_workflow(self, start_time: float):
        """Finalizes the workflow, ensuring all agents are NOMINAL and logging the audit trail."""
        elapsed = time.time() - start_time
        
        # Check for any lingering errors
        violations = self.governor.scan_for_violations()
        if violations:
            logger.warning(f"Workflow completed with {len(violations)} warnings/violations.")
        else:
            logger.info("Workflow completed. All agents NOMINAL. No violations.")
            
        # Log final mesh status
        status = self.governor.get_mesh_status()
        logger.info(f"Final Mesh Status: {status['nominal_agents']} Nominal, "
                    f"{status['evolving_agents']} Evolving, "
                    f"VRAM Utilization: {status['vram_stats']['utilization_percent']:.2f}%")
        logger.info(f"Total execution time: {elapsed:.4f} seconds")


# ==============================================================================
# Example Usage / Test Harness
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 1. Initialize the Orchestrator
    orchestrator = ChainOrchestrator(total_vram_gb=4.0)
    
    # 2. Register a Legacy Agent
    legacy_profile = AgentProfile(
        agent_id="legacy_sar_agent",
        agent_type="legacy",
        initial_dimensions=1024,
        initial_memory_bytes=8192,
        growth_margin=0.05
    )
    orchestrator.register_agent(legacy_profile)
    
    # 3. Register an Evolving Agent
    evolving_profile = AgentProfile(
        agent_id="evolving_fusion_agent",
        agent_type="evolving",
        initial_dimensions=2048,
        initial_memory_bytes=16384,
        growth_margin=0.50
    )
    orchestrator.register_agent(evolving_profile)
    
    # 4. Define the Workflow Chain
    workflow = [
        WorkflowStep(
            source_agent_id="legacy_sar_agent",
            target_agent_id="evolving_fusion_agent",
            operation="transform",
            is_mutable=True
        )
    ]
    
    # 5. Execute the Workflow
    success = orchestrator.execute_workflow(workflow)
    
    if success:
        print("\n✅ WORKFLOW SUCCESS: Elastic handoff completed without security collapse.")
    else:
        print("\n❌ WORKFLOW FAILED: Check logs for security violations.")
