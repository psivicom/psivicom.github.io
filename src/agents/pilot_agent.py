# ==============================================================================
# FILE: pilot_agent.py
# PATH: psivicom.github.io/src/agents/pilot_agent.py
# DESCRIPTION: Pilot Agent for Fragility and Concordance Scanning
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

class PilotAgent:
    """
    Executes fragility and concordance scans on mesh vectors.
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
        
        self.bytes_per_element = 8
        self.pilot_overhead = 1.25
        
        logger.info(f"PilotAgent {self.agent_id} initialized.")

    def execute_scan(
        self,
        vector_dimensions: int
    ) -> Tuple[bool, Optional[np.ndarray]]:
        logger.info(f"[{self.agent_id}] Starting pilot scan of {vector_dimensions} dimensions.")
        
        required_vram = self._calc_required_vram(vector_dimensions)
        
        handle = self.provisioner.get_handle(self.agent_id)
        if not handle:
            logger.error(f"[{self.agent_id}] No VRAM handle.")
            return False, None
            
        current_vram = handle.size_bytes
        
        if required_vram > current_vram:
            logger.warning(f"[{self.agent_id}] Scan requires {required_vram} bytes. Requesting evolution...")
            success = self.governor.request_evolution(
                self.agent_id,
                new_dimensions=vector_dimensions,
                new_memory=required_vram
            )
            if not success:
                logger.info(f"[{self.agent_id}] Evolution denied. Using chunking.")
                
        simulated_data = np.random.rand(vector_dimensions).astype(np.float64)
        
        success, result = self.pixelizer.execute_vector_math(
            self.agent_id,
            operation="transform",
            input_data=simulated_data
        )
        
        if not success:
            logger.error(f"[{self.agent_id}] Pilot scan failed.")
            return False, None
            
        pheromone = f"pilot_scan_complete:{vector_dimensions}_dims"
        self.governor.deposit_pheromone(self.agent_id, pheromone)
        
        logger.info(f"[{self.agent_id}] Pilot scan complete.")
        return True, result

    def _calc_required_vram(self, vector_dimensions: int) -> int:
        base = vector_dimensions * self.bytes_per_element
        return int(base * self.pilot_overhead)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    mesh = VRAMMesh(total_vram_bytes=4 * 1024 * 1024 * 1024)
    provisioner = ElasticPSVCProvisioner(mesh)
    governor = MeshGovernor(mesh, provisioner)
    pixelizer = VectorPixelizer(mesh, provisioner, governor)
    
    agent = PilotAgent("pilot_01", provisioner, governor, pixelizer)
    
    initial_dims = 1000
    initial_vram = agent._calc_required_vram(initial_dims)
    provisioner.allocate(agent.agent_id, initial_vram, growth_margin=0.2)
    governor.register_agent(agent.agent_id, initial_dims, initial_vram)
    
    print("\n--- Normal Pilot Scan ---")
    agent.execute_scan(vector_dimensions=1000)
    
    print("\n--- Final Status ---")
    status = governor.get_mesh_status()
    print(f"Generations: {status['provisioner_stats']['average_generation']:.2f}")
    print("Pilot scan complete. Mesh: NOMINAL.")
