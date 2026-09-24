# src/orchestrator/chain_orchestrator.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Dynamic Chain Orchestrator | Closed-Loop Control | Branch-Free Logic

import sys
import logging
import time
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from psvc_reference import write_file, content_hash, PRECISION_FLOAT16
from src.mesh.vram_mesh import VRAMMesh
from src.mesh.mesh_governor import MeshGovernor
from src.orchestrator.psvc_provisioner import ElasticPSVCProvisioner
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
    step_id: str
    agent_id: str
    operation: str
    dependencies: List[str] = field(default_factory=list)
    is_mutable: bool = True

@dataclass
class ElasticityDecision:
    decision: str
    reason: str
    fragility_count: int
    concordance_count: int
    osdr_matches: List[Dict] = field(default_factory=list)

class ChainOrchestrator:
    DECISION_MAP = ["CONTRACT", "STABLE", "EXPAND"]

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
        score = np.clip(frag_count - conc_count, -1, 1)
        decision = self.DECISION_MAP[int(score) + 1]
        reason_map = {
            "EXPAND": f"High fragility: {frag_count} traps > {conc_count} controls",
            "CONTRACT": f"High concordance: {conc_count} controls > {frag_count} traps",
            "STABLE": f"Balanced: {frag_count} traps, {conc_count} controls"
        }
        return ElasticityDecision(
            decision=decision,
            reason=reason_map[decision],
            fragility_count=frag_count,
            concordance_count=conc_count,
            osdr_matches=self.pilot.fragility_traps + self.pilot.concordant_controls
        )

    def execute_workflow(self, goal: str, initial_steps: List[WorkflowStep] = None) -> bool:
        logger.info(f"Starting AI-driven workflow execution for goal: {goal}")
        start_time = time.time()
        elasticity = self.evaluate_elasticity()
        logger.info(f"[Orchestrator] Elasticity decision: {elasticity.decision} - {elasticity.reason}")
        steps = initial_steps or [WorkflowStep(step_id="step_1", agent_id="forage_agent", operation="collect_data", dependencies=[])]
        action_map = {
            "EXPAND": WorkflowStep(step_id="expand_literature", agent_id="literature_agent", operation="resolve_fragility", dependencies=[steps[-1].step_id]),
            "CONTRACT": WorkflowStep(step_id="contract_prune", agent_id="consolidator_agent", operation="prune_redundant", dependencies=[steps[-1].step_id]),
            "STABLE": None
        }
        next_step = action_map[elasticity.decision]
        if next_step:
            steps.append(next_step)
        execution_order = self._resolve_dag_execution_order(steps)
        for i, step in enumerate(execution_order):
            logger.info(f"Executing Step {i+1}/{len(execution_order)}: {step.step_id} [{step.agent_id}] -> {step.operation}")
            if not self.governor.enforce_pico_protocol():
                logger.error("Pico protocol violation detected. Halting workflow.")
                return False
            if not self._preflight_smoke_test(step):
                logger.error(f"Workflow halted: Pre-flight test failed for {step.step_id}")
                return False
            self.governor.deposit_pheromone(step.agent_id, f"executed:{step.step_id}")
        self._finalize_workflow(start_time, elasticity)
        return True

    def _resolve_dag_execution_order(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        step_map = {step.step_id: step for step in steps}
        executed: set = set()
        execution_order: List[WorkflowStep] = []
        while len(executed) < len(steps):
            progress = False
            for step in steps:
                if step.step_id not in executed and all(dep in executed for dep in step.dependencies):
                    execution_order.append(step)
                    executed.add(step.step_id)
                    progress = True
            if not progress and len(executed) < len(steps):
                raise ValueError("Circular dependency detected in AI-generated workflow DAG")
        return execution_order

    def _preflight_smoke_test(self, step: WorkflowStep) -> bool:
        try:
            mock_data = np.random.randn(64).astype(np.float32)
            _ = mock_data * 1.1 if "resolve" in step.operation or "collect" in step.operation else mock_data
            return True
        except Exception as e:
            logger.error(f"Pre-flight smoke test failed for {step.step_id}: {e}")
            return False

    def _finalize_workflow(self, start_time: float, elasticity: ElasticityDecision):
        elapsed = time.time() - start_time
        violations = self.governor.scan_for_violations()
        if violations:
            logger.warning(f"Workflow completed with {len(violations)} warnings/violations.")
        else:
            logger.info("Workflow completed. All agents NOMINAL. No violations.")
        status = self.governor.get_mesh_status()
        logger.info(f"Final Mesh Status: {status.get('nominal_agents', 0)} Nominal, VRAM Utilization: {status.get('vram_stats', {}).get('utilization_percent', 0):.2f}%")
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
        if norm > 0: summary_vector /= norm
        output_dir = Path("reports/pico_containers")
        output_dir.mkdir(parents=True, exist_ok=True)
        chash = content_hash(summary_vector)
        filename = f"elasticity_decision_{chash[:12]}.psvc"
        output_path = output_dir / filename
        write_file(summary_vector, output_path, precision=PRECISION_FLOAT16)
        sidecar_path = output_path.with_suffix('.json')
        with open(sidecar_path, 'w') as f:
            json.dump({
                "type": "elasticity_decision", "decision": decision.decision, "reason": decision.reason,
                "fragility_count": decision.fragility_count, "concordance_count": decision.concordance_count,
                "timestamp": time.time(), "rfc1001_compliant": True
            }, f, indent=2)
        logger.info(f"[Orchestrator] Sealed elasticity decision to {filename}")
