# src/orchestrator/chain_orchestrator.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# 
# Dynamic Chain Orchestrator for Elastic PSVC Mesh
# Integrates OSDR-FRAG/CTRL ground truth via Pilot Agent for elasticity decisions.
# RFC 1001 Compliant | NIST SP 800-218 | FAIR Open Science
# ==============================================================================

import logging
import time
import json
import numpy as np
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# Ensure project root is in path for imports
# This goes: src/orchestrator → src → root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import Mesh Infrastructure (The "Body")
from src.mesh.vram_mesh import VRAMMesh
from src.mesh.governor import MeshGovernor
from src.mesh.provisioner import ElasticPSVCProvisioner

# Import Core Utilities (Universal)
from src.core.psvc_reference import write_file, content_hash, PRECISION_FLOAT16, read_file, validate_file
from src.core.vector_pixelizer import VectorPixelizer

# Import Cognitive Agents (The "Brain")
from src.agents.forage_agent import ForageAgent
from src.agents.pilot_agent import OSDRPilotAgent  # The OSDR-ground-truth validator

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


@dataclass
class ElasticityDecision:
    """Result of Pilot-informed elasticity analysis"""
    decision: str  # "EXPAND", "CONTRACT", or "STABLE"
    reason: str
    fragility_count: int
    concordance_count: int
    osdr_matches: List[Dict] = field(default_factory=list)


class ChainOrchestrator:
    """
    Manages the execution of multi-agent workflows using the Elastic PSVC system.
    
    Integrates OSDR-FRAG/CTRL ground truth via the Pilot Agent to make
    scientifically-informed elasticity decisions:
    - EXPAND: High fragility → Spawn literature/genesis agents for more data
    - CONTRACT: High concordance → Prune redundant vectors via consolidator
    - STABLE: Balanced → Continue normal operations
    
    Ensures secure, zero-copy data handoffs and RFC 1001 compliance.
    """
    
    def __init__(self, total_vram_gb: float = 8.0, osdr_data_path: str = "data/osdr_ground_truth.jsonl"):
        logger.info("Initializing Chain Orchestrator with Elastic PSVC Core...")
        
        # 1. Initialize the VRAM-Native Infrastructure
        total_vram_bytes = int(total_vram_gb * 1024 * 1024 * 1024)
        self.vram_mesh = VRAMMesh(total_vram_bytes)
        
        # 2. Initialize the Elastic Provisioner & Governor
        self.provisioner = ElasticPSVCProvisioner(self.vram_mesh)
        self.governor = MeshGovernor(self.vram_mesh, self.provisioner)
        
        # 3. Initialize the Vector Math Engine
        self.pixelizer = VectorPixelizer(self.vram_mesh, self.provisioner, self.governor)
        
        # 4. Initialize the OSDR Pilot Agent (for ground-truth validation)
        self.pilot = OSDRPilotAgent(osdr_data_path=osdr_data_path)
        
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

    def evaluate_elasticity(self, container_dir: Path = None) -> ElasticityDecision:
        """
        Runs the Pilot Agent to scan mesh vectors against OSDR ground truth.
        Returns an ElasticityDecision based on fragility/concordance counts.
        """
        if container_dir is None:
            container_dir = Path("reports/pico_containers")
        
        # Run pilot scan
        self.pilot._run_logic()
        
        frag_count = len(self.pilot.fragility_traps)
        conc_count = len(self.pilot.concordant_controls)
        
        # Decision logic (OSDR-inspired)
        if frag_count > conc_count:
            decision = "EXPAND"
            reason = f"High fragility: {frag_count} traps > {conc_count} controls"
        elif conc_count > frag_count * 2:
            decision = "CONTRACT"
            reason = f"High concordance: {conc_count} controls > {frag_count * 2} traps"
        else:
            decision = "STABLE"
            reason = f"Balanced: {frag_count} traps, {conc_count} controls"
        
        return ElasticityDecision(
            decision=decision,
            reason=reason,
            fragility_count=frag_count,
            concordance_count=conc_count,
            osdr_matches=self.pilot.fragility_traps + self.pilot.concordant_controls
        )

    def spawn_agents_for_fragility(self, traps: List[Dict]) -> List[str]:
        """
        Spawns specialized agents to resolve fragility traps.
        Returns list of spawned agent IDs.
        """
        spawned = []
        
        # Analyze trap patterns
        organisms = set()
        tissues = set()
        for trap in traps[:10]:  # Top 10 traps
            if 'organism' in trap:
                organisms.add(trap['organism'])
            if 'tissue' in trap:
                tissues.add(trap['tissue'])
        
        # Spawn literature agent to fetch more context
        if organisms or tissues:
            logger.info(f"[Orchestrator] Spawning literature agent for {organisms}")
            spawned.append("literature_agent")
            self.seal("spawn_literature", {
                "organisms": list(organisms),
                "tissues": list(tissues),
                "reason": "fragility_resolution"
            })
        
        # Spawn genesis agent if fragility is severe
        if len(traps) > 5:
            logger.info(f"[Orchestrator] Spawning genesis agent for novel capabilities")
            spawned.append("genesis_agent")
            self.seal("spawn_genesis", {
                "trap_count": len(traps),
                "reason": "severe_fragility"
            })
        
        return spawned

    def trigger_consolidation(self) -> bool:
        """
        Triggers consolidator agent to prune redundant vectors.
        Returns True if consolidation was triggered.
        """
        logger.info(f"[Orchestrator] Triggering consolidation (high concordance)")
        self.seal("trigger_consolidation", {
            "reason": "high_concordance",
            "concordance_count": len(self.pilot.concordant_controls)
        })
        return True

    def execute_workflow(self, steps: List[WorkflowStep], goal: str = None) -> bool:
        """
        Executes the chain of workflow steps with Pilot-informed elasticity.
        
        Before execution, evaluates mesh health against OSDR ground truth
        and adjusts agent spawning/pruning accordingly.
        """
        logger.info(f"Starting workflow execution with {len(steps)} steps...")
        start_time = time.time()
        
        # 1. Evaluate elasticity BEFORE execution
        elasticity = self.evaluate_elasticity()
        logger.info(f"[Orchestrator] Elasticity decision: {elasticity.decision} - {elasticity.reason}")
        
        # 2. Adjust workflow based on elasticity
        if elasticity.decision == "EXPAND":
            # Spawn agents to resolve fragility
            new_agents = self.spawn_agents_for_fragility(self.pilot.fragility_traps)
            # Add them to the workflow (simplified: append to end)
            for agent_id in new_agents:
                steps.append(WorkflowStep(
                    source_agent_id=steps[-1].target_agent_id if steps else "orchestrator",
                    target_agent_id=agent_id,
                    operation="resolve_fragility",
                    is_mutable=True
                ))
                
        elif elasticity.decision == "CONTRACT":
            # Trigger consolidation to prune redundant data
            self.trigger_consolidation()
            # Add consolidator step
            steps.append(WorkflowStep(
                source_agent_id=steps[-1].target_agent_id if steps else "orchestrator",
                target_agent_id="consolidator_agent",
                operation="prune_redundant",
                is_mutable=False
            ))
        
        # 3. Execute the (possibly modified) workflow
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
        
        # 4. Finalize and audit
        self._finalize_workflow(start_time, elasticity)
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

    def _finalize_workflow(self, start_time: float, elasticity: ElasticityDecision):
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
        
        # Seal elasticity decision as RFC 1001 container
        self._seal_elasticity_decision(elasticity)
    
    def _seal_elasticity_decision(self, decision: ElasticityDecision):
        """Seals the elasticity decision as an RFC 1001 compliant .psvc container."""
        # Create a summary vector encoding the decision
        summary_vector = np.zeros(4096, dtype=np.float32)
        summary_vector[0] = 1.0 if decision.decision == "EXPAND" else 0.0
        summary_vector[1] = 1.0 if decision.decision == "CONTRACT" else 0.0
        summary_vector[2] = 1.0 if decision.decision == "STABLE" else 0.0
        summary_vector[3] = decision.fragility_count / 100.0  # Normalized
        summary_vector[4] = decision.concordance_count / 100.0
        
        # Normalize
        norm = np.linalg.norm(summary_vector)
        if norm > 0:
            summary_vector /= norm
        
        # Write to RFC 1001 container
        output_dir = Path("reports/pico_containers")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        chash = content_hash(summary_vector)
        filename = f"elasticity_decision_{chash[:12]}.psvc"
        output_path = output_dir / filename
        
        write_file(summary_vector, output_path, precision=PRECISION_FLOAT16)
        
        # Write JSON sidecar with full decision metadata
        sidecar_path = output_path.with_suffix('.json')
        with open(sidecar_path, 'w') as f:
            json.dump({
                "type": "elasticity_decision",
                "decision": decision.decision,
                "reason": decision.reason,
                "fragility_count": decision.fragility_count,
                "concordance_count": decision.concordance_count,
                "osdr_matches_count": len(decision.osdr_matches),
                "timestamp": time.time(),
                "rfc1001_compliant": True
            }, f, indent=2)
        
        logger.info(f"[Orchestrator] Sealed elasticity decision to {filename}")

    def seal(self, operation: str, payload: Dict[str, Any]):
        """Deposits a pheromone/receipt for audit trail (simplified)."""
        # In production, this would create a full AgentReceipt chain
        logger.debug(f"[Orchestrator] Sealed: {operation} - {payload}")


# ==============================================================================
# Example Usage / Test Harness
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 1. Initialize the Orchestrator with OSDR data path
    orchestrator = ChainOrchestrator(
        total_vram_gb=4.0,
        osdr_data_path="data/osdr_ground_truth.jsonl"
    )
    
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
    
    # 5. Execute the Workflow (with Pilot-informed elasticity)
    success = orchestrator.execute_workflow(workflow, goal="Analyze Goldstream forage window")
    
    if success:
        print("\n✅ WORKFLOW SUCCESS: Elastic handoff completed without security collapse.")
    else:
        print("\n❌ WORKFLOW FAILED: Check logs for security violations.")
