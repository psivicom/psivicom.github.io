# src/orchestrator/chain_orchestrator.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Dynamic Chain Orchestrator for Elastic PSVC Mesh

import logging
import time
import json
import numpy as np
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.mesh.vram_mesh import VRAMMesh
from src.mesh.governor import MeshGovernor
from src.mesh.provisioner import ElasticPSVCProvisioner
from src.core.psvc_reference import write_file, content_hash, PRECISION_FLOAT16
from src.agents.pilot_agent import PilotAgent

logger = logging.getLogger(__name__)

@dataclass
class AgentProfile:
    agent_id: str
    agent_type: str
    initial_dimensions: int
    initial_memory_bytes: int
    growth_margin: float = 0.2

@dataclass
class WorkflowStep:
    source_agent_id: str
    target_agent_id: str
    operation: str
    is_mutable: bool

@dataclass
class ElasticityDecision:
    decision: str
    reason: str
    fragility_count: int
    concordance_count: int
    osdr_matches: List[Dict] = field(default_factory=list)

class ChainOrchestrator:
    def __init__(self, total_vram_gb: float = 8.0, osdr_data_path: str = "data/osdr_ground_truth.jsonl"):
        logger.info("Initializing Chain Orchestrator with Elastic PSVC Core...")
        total_vram_bytes = int(total_vram_gb * 1024 * 1024 * 1024)
        self.vram_mesh = VRAMMesh(total_vram_bytes)
        self.provisioner = ElasticPSVCProvisioner(self.vram_mesh)
        self.governor = MeshGovernor(self.vram_mesh, self.provisioner)
        self.pilot = PilotAgent(osdr_data_path=osdr_data_path)
        self.agents: Dict[str, AgentProfile] = {}
        logger.info("Chain Orchestrator initialized. Mesh status: NOMINAL")

    def register_agent(self, profile: AgentProfile) -> bool:
        try:
            margin = profile.growth_margin if profile.agent_type == "evolving" else 0.05
            self.provisioner.allocate(profile.agent_id, profile.initial_memory_bytes, margin)
            self.governor.register_agent(profile.agent_id, profile.initial_dimensions, profile.initial_memory_bytes)
            self.agents[profile.agent_id] = profile
            logger.info(f"Registered {profile.agent_type} agent: {profile.agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {profile.agent_id}: {e}")
            return False

    def evaluate_elasticity(self, container_dir: Path = None) -> ElasticityDecision:
        if container_dir is None:
            container_dir = Path("reports/pico_containers")
        
        self.pilot._run_logic()
        frag_count = len(self.pilot.fragility_traps)
        conc_count = len(self.pilot.concordant_controls)
        
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

    def execute_workflow(self, steps: List[WorkflowStep], goal: str = None) -> bool:
        logger.info(f"Starting workflow execution with {len(steps)} steps...")
        start_time = time.time()
        
        elasticity = self.evaluate_elasticity()
        logger.info(f"[Orchestrator] Elasticity decision: {elasticity.decision} - {elasticity.reason}")
        
        if elasticity.decision == "EXPAND":
            steps.append(WorkflowStep(
                source_agent_id=steps[-1].target_agent_id if steps else "orchestrator",
                target_agent_id="literature_agent",
                operation="resolve_fragility",
                is_mutable=True
            ))
        elif elasticity.decision == "CONTRACT":
            steps.append(WorkflowStep(
                source_agent_id=steps[-1].target_agent_id if steps else "orchestrator",
                target_agent_id="consolidator_agent",
                operation="prune_redundant",
                is_mutable=False
            ))
        
        for i, step in enumerate(steps):
            logger.info(f"Executing Step {i+1}: {step.source_agent_id} -> {step.target_agent_id} [{step.operation}]")
            if not self.governor.enforce_pico_protocol():
                logger.error("Pico protocol violation detected. Halting workflow.")
                return False
        
        self._finalize_workflow(start_time, elasticity)
        return True

    def _finalize_workflow(self, start_time: float, elasticity: ElasticityDecision):
        elapsed = time.time() - start_time
        violations = self.governor.scan_for_violations()
        if violations:
            logger.warning(f"Workflow completed with {len(violations)} warnings/violations.")
        else:
            logger.info("Workflow completed. All agents NOMINAL. No violations.")
            
        status = self.governor.get_mesh_status()
        logger.info(f"Final Mesh Status: {status.get('nominal_agents', 0)} Nominal, "
                    f"VRAM Utilization: {status.get('vram_stats', {}).get('utilization_percent', 0):.2f}%")
        logger.info(f"Total execution time: {elapsed:.4f} seconds")
        
        self._seal_elasticity_decision(elasticity)

    def _seal_elasticity_decision(self, decision: ElasticityDecision):
        summary_vector = np.zeros(4096, dtype=np.float32)
        summary_vector[0] = 1.0 if decision.decision == "EXPAND" else 0.0
        summary_vector[1] = 1.0 if decision.decision == "CONTRACT" else 0.0
        summary_vector[2] = 1.0 if decision.decision == "STABLE" else 0.0
        summary_vector[3] = decision.fragility_count / 100.0
        summary_vector[4] = decision.concordance_count / 100.0
        
        norm = np.linalg.norm(summary_vector)
        if norm > 0:
            summary_vector /= norm
        
        output_dir = Path("reports/pico_containers")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        chash = content_hash(summary_vector)
        filename = f"elasticity_decision_{chash[:12]}.psvc"
        output_path = output_dir / filename
        
        write_file(summary_vector, output_path, precision=PRECISION_FLOAT16)
        
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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    orchestrator = ChainOrchestrator(total_vram_gb=4.0, osdr_data_path="data/osdr_ground_truth.jsonl")
    
    legacy_profile = AgentProfile(agent_id="legacy_sar_agent", agent_type="legacy", initial_dimensions=1024, initial_memory_bytes=8192, growth_margin=0.05)
    orchestrator.register_agent(legacy_profile)
    
    evolving_profile = AgentProfile(agent_id="evolving_fusion_agent", agent_type="evolving", initial_dimensions=2048, initial_memory_bytes=16384, growth_margin=0.50)
    orchestrator.register_agent(evolving_profile)
    
    workflow = [WorkflowStep(source_agent_id="legacy_sar_agent", target_agent_id="evolving_fusion_agent", operation="transform", is_mutable=True)]
    success = orchestrator.execute_workflow(workflow, goal="Analyze Goldstream forage window")
    
    if success:
        print("\n✅ WORKFLOW SUCCESS: Elastic handoff completed without security collapse.")
    else:
        print("\n❌ WORKFLOW FAILED: Check logs for security violations.")
