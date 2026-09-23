# ==============================================================================
# FILE: consolidator_agent.py
# PATH: psivicom.github.io/src/agents/consolidator_agent.py
# DESCRIPTION: Evolving Consolidator Agent for Multi-Source Data Clustering
# LICENSE: EUPL-1.2 | COMPLIANCE: NIST SP 800-218, FAIR Open Science
# ==============================================================================

import logging
import numpy as np
import time
from typing import Optional, Tuple, List

# CORRECT absolute imports from the repository root (PYTHONPATH)
from src.mesh.vram_mesh import VRAMMesh
from src.mesh.mesh_governor import MeshGovernor
from src.core.vector_pixelizer import VectorPixelizer
from src.orchestrator.psvc_provisioner import ElasticPSVCProvisioner

logger = logging.getLogger(__name__)

class ConsolidatorAgent:
    """
    Clusters and merges data from multiple agents into unified vectors.
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
        self.cluster_overhead = 1.3
        
        logger.info(f"ConsolidatorAgent {self.agent_id} initialized.")

    def consolidate_batch(
        self,
        source_vectors: List[np.ndarray]
    ) -> Tuple[bool, Optional[np.ndarray]]:
        logger.info(f"[{self.agent_id}] Starting consolidation of {len(source_vectors)} vectors.")
        
        total_elements = sum(v.size for v in source_vectors)
        required_vram = self._calc_required_vram(total_elements)
        
        handle = self.provisioner.get_handle(self.agent_id)
        if not handle:
            logger.error(f"[{self.agent_id}] No VRAM handle.")
            return False, None
            
        current_vram = handle.size_bytes
        
        if required_vram > current_vram:
            logger.warning(f"[{self.agent_id}] Consolidation requires {required_vram} bytes. Requesting evolution...")
            success = self.governor.request_evolution(
                self.agent_id,
                new_dimensions=total_elements,
                new_memory=required_vram
            )
            if not success:
                logger.info(f"[{self.agent_id}] Evolution denied. Using chunking.")
                
        fused_input = np.concatenate(source_vectors)
        
        success, result = self.pixelizer.execute_vector_math(
            self.agent_id,
            operation="transform",
            input_data=fused_input
        )
        
        if not success:
            logger.error(f"[{self.agent_id}] Consolidation failed.")
            return False, None
            
        pheromone = f"consolidation_complete:{len(source_vectors)}_vectors:{total_elements}_elements"
        self.governor.deposit_pheromone(self.agent_id, pheromone)
        
        logger.info(f"[{self.agent_id}] Consolidation complete.")
        return True, result

    def _calc_required_vram(self, total_elements: int) -> int:
        base = total_elements * self.bytes_per_element
        return int(base * self.cluster_overhead)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    mesh = VRAMMesh(total_vram_bytes=4 * 1024 * 1024 * 1024)
    provisioner = ElasticPSVCProvisioner(mesh)
    governor = MeshGovernor(mesh, provisioner)
    pixelizer = VectorPixelizer(mesh, provisioner, governor)
    
    agent = ConsolidatorAgent("consolidator_01", provisioner, governor, pixelizer)
    
    initial_elements = 1000
    initial_vram = agent._calc_required_vram(initial_elements)
    provisioner.allocate(agent.agent_id, initial_vram, growth_margin=0.2)
    governor.register_agent(agent.agent_id, initial_elements, initial_vram)
    
    print("\n--- Normal Consolidation ---")
    vectors = [np.random.rand(500).astype(np.float64) for _ in range(3)]
    agent.consolidate_batch(vectors)
    
    print("\n--- Final Status ---")
    status = governor.get_mesh_status()
    print(f"Generations: {status['provisioner_stats']['average_generation']:.2f}")
    print("Consolidator complete. Mesh: NOMINAL.")
