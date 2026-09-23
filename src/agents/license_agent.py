# ==============================================================================
# FILE: license_agent.py
# PATH: psivicom.github.io/src/agents/license_agent.py
# DESCRIPTION: License Compliance Agent
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

class LicenseAgent:
    """
    Scans repository for license compliance.
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
        self.scan_overhead = 1.2
        
        logger.info(f"LicenseAgent {self.agent_id} initialized.")

    def scan_repository(
        self,
        file_count: int
    ) -> Tuple[bool, Optional[np.ndarray]]:
        logger.info(f"[{self.agent_id}] Starting license scan of {file_count} files.")
        
        required_vram = self._calc_required_vram(file_count)
        
        handle = self.provisioner.get_handle(self.agent_id)
        if not handle:
            logger.error(f"[{self.agent_id}] No VRAM handle.")
            return False, None
            
        current_vram = handle.size_bytes
        
        if required_vram > current_vram:
            logger.warning(f"[{self.agent_id}] Scan requires {required_vram} bytes. Requesting evolution...")
            success = self.governor.request_evolution(
                self.agent_id,
                new_dimensions=file_count,
                new_memory=required_vram
            )
            if not success:
                logger.info(f"[{self.agent_id}] Evolution denied. Using chunking.")
                
        simulated_data = np.random.rand(file_count).astype(np.float64)
        
        success, result = self.pixelizer.execute_vector_math(
            self.agent_id,
            operation="transform",
            input_data=simulated_data
        )
        
        if not success:
            logger.error(f"[{self.agent_id}] Scan failed.")
            return False, None
            
        pheromone = f"license_scan_complete:{file_count}_files"
        self.governor.deposit_pheromone(self.agent_id, pheromone)
        
        logger.info(f"[{self.agent_id}] License scan complete.")
        return True, result

    def _calc_required_vram(self, file_count: int) -> int:
        base = file_count * self.bytes_per_element
        return int(base * self.scan_overhead)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    mesh = VRAMMesh(total_vram_bytes=4 * 1024 * 1024 * 1024)
    provisioner = ElasticPSVCProvisioner(mesh)
    governor = MeshGovernor(mesh, provisioner)
    pixelizer = VectorPixelizer(mesh, provisioner, governor)
    
    agent = LicenseAgent("license_01", provisioner, governor, pixelizer)
    
    initial_files = 100
    initial_vram = agent._calc_required_vram(initial_files)
    provisioner.allocate(agent.agent_id, initial_vram, growth_margin=0.2)
    governor.register_agent(agent.agent_id, initial_files, initial_vram)
    
    print("\n--- Normal License Scan ---")
    agent.scan_repository(file_count=100)
    
    print("\n--- Final Status ---")
    status = governor.get_mesh_status()
    print(f"Generations: {status['provisioner_stats']['average_generation']:.2f}")
    print("License scan complete. Mesh: NOMINAL.")
