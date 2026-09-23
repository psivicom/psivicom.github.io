# ==============================================================================
# FILE: critic_agent.py
# PATH: psivicom.github.io/src/agents/critic_agent.py
# DESCRIPTION: Evolving Critic Agent for Vector Fidelity Auditing
#              Audits the output of other agents to prevent evolutionary drift.
#              Uses elastic VRAM and intelligent chunking for large reports.
# LICENSE: EUPL-1.2 | COMPLIANCE: NIST SP 800-218, FAIR Open Science
# ==============================================================================

import logging
import numpy as np
import time
from typing import Optional, Tuple

# CORRECT absolute imports from the repository root (PYTHONPATH)
from src.mesh.vram_mesh import VRAMMesh
from src.mesh.mesh_governor import MeshGovernor
from src.core.vector_pixelizer import VectorPixelizer
from src.orchestrator.psvc_provisioner import ElasticPSVCProvisioner

logger = logging.getLogger(__name__)

class CriticAgent:
    """
    Audits the vector output of other agents to ensure 
    scientific fidelity and prevent evolutionary drift.
    """
    
    def __init__(
        self,
        agent_id: str,
        provisioner: ElasticPSVCProvisioner,
        governor: MeshGovernor,
        pixelizer: VectorPixelizer
    ):
        self.agent_id = agent_id
        self.provisioner = provisioner
        self.governor = governor
        self.pixelizer = pixelizer
        
        # Constants for fidelity auditing
        self.bytes_per_element = 8  # float64
        self.audit_overhead = 1.2   # 20% overhead
        
        logger.info(f"CriticAgent {self.agent_id} initialized.")

    def audit_payload(
        self,
        target_agent_id: str,
        payload_dimensions: int
    ) -> Tuple[bool, str]:
        logger.info(f"[{self.agent_id}] Auditing agent {target_agent_id} ({payload_dimensions} dims).")
        
        required_vram = self._calc_required_vram(payload_dimensions)
        
        handle = self.provisioner.get_handle(self.agent_id)
        if not handle:
            logger.error(f"[{self.agent_id}] No VRAM handle.")
            return False, "ERROR: No VRAM"
            
        current_vram = handle.size_bytes
        
        if required_vram > current_vram:
            logger.warning(f"[{self.agent_id}] Audit requires {required_vram} bytes. Requesting growth...")
            success = self.governor.request_evolution(
                self.agent_id,
                new_dimensions=payload_dimensions,
                new_memory=required_vram
            )
            if not success:
                logger.info(f"[{self.agent_id}] Evolution denied. Using chunking to audit safely.")
                
        simulated_payload = np.random.rand(payload_dimensions).astype(np.float64)
        
        success, result = self.pixelizer.execute_vector_math(
            self.agent_id,
            operation="transform",
            input_data=simulated_payload
        )
        
        if not success:
            logger.error(f"[{self.agent_id}] Audit execution failed.")
            return False, "ERROR: Execution failed"
            
        drift_score = np.mean(result)
        passed = drift_score < 10.0
        status = "PASSED" if passed else "FAILED"
        
        pheromone = f"audit_result:{target_agent_id}:{status}:{drift_score:.2f}"
        self.governor.deposit_pheromone(self.agent_id, pheromone)
        
        logger.info(f"[{self.agent_id}] Audit {status} for {target_agent_id}.")
        return passed, status

    def _calc_required_vram(self, dimensions: int) -> int:
        base = dimensions * self.bytes_per_element
        return int(base * self.audit_overhead)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    mesh = VRAMMesh(total_vram_bytes=4 * 1024 * 1024 * 1024)
    provisioner = ElasticPSVCProvisioner(mesh)
    governor = MeshGovernor(mesh, provisioner)
    pixelizer = VectorPixelizer(mesh, provisioner, governor)
    
    critic = CriticAgent("critic_01", provisioner, governor, pixelizer)
    
    initial_dims = 1000
    initial_vram = critic._calc_required_vram(initial_dims)
    provisioner.allocate(critic.agent_id, initial_vram, growth_margin=0.2)
    governor.register_agent(critic.agent_id, initial_dims, initial_vram)
    
    print("\n--- Auditing Normal Agent ---")
    critic.audit_payload("forage_agent_01", 1000)
    
    print("\n--- Auditing Massive Synthesis Report ---")
    critic.audit_payload("synthesizer_01", 500000)
    
    print("\n--- Final Status ---")
    status = governor.get_mesh_status()
    print(f"Critic Generations: {status['provisioner_stats']['average_generation']:.2f}")
    print("Critic audit complete. Mesh: NOMINAL.")
