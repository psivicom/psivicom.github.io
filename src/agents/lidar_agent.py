# ============================================================
# FILE: lidar_agent.py
# PATH: psivicom.github.io/src/agents/lidar_agent.py
# DESCRIPTION: Evolving Lidar Agent for Canopy Point Clouds
# LICENSE: EUPL-1.2
# ============================================================

import logging
import numpy as np
from typing import Optional, Tuple

from src.mesh.vram_mesh import VRAMMesh
from src.mesh.mesh_governor import MeshGovernor
from src.core.vector_pixelizer import VectorPixelizer
from src.orchestrator.psvc_provisioner import ElasticPSVCProvisioner

logger = logging.getLogger(__name__)

class LidarAgent:
    def __init__(self, agent_id: str, provisioner: ElasticPSVCProvisioner, governor: MeshGovernor, pixelizer: VectorPixelizer):
        self.agent_id = agent_id
        self.provisioner = provisioner
        self.governor = governor
        self.pixelizer = pixelizer
        self.bytes_per_point = 8
        self.cloud_overhead = 1.5
        logger.info(f"LidarAgent {self.agent_id} initialized.")

    def process_canopy_scan(self, point_count: int) -> Tuple[bool, Optional[np.ndarray]]:
        logger.info(f"[{self.agent_id}] Starting canopy scan. Points: {point_count}")
        required_vram = int(point_count * self.bytes_per_point * self.cloud_overhead)
        handle = self.provisioner.get_handle(self.agent_id)
        
        if not handle:
            logger.error(f"[{self.agent_id}] No VRAM handle.")
            return False, None
            
        if required_vram > handle.size_bytes:
            logger.warning(f"[{self.agent_id}] Scan requires {required_vram} bytes. Requesting evolution...")
            self.governor.request_evolution(self.agent_id, new_dimensions=point_count, new_memory=required_vram)
                
        simulated_cloud = np.random.rand(point_count).astype(np.float64)
        
        # FIX: Changed 'input_data' to 'data' to match VectorPixelizer signature
        success, result = self.pixelizer.execute_vector_math(self.agent_id, operation="transform", data=simulated_cloud)
        
        if not success:
            logger.error(f"[{self.agent_id}] Canopy scan failed.")
            return False, None
            
        self.governor.deposit_pheromone(self.agent_id, f"canopy_scan_complete:{point_count}_points")
        logger.info(f"[{self.agent_id}] Canopy scan complete.")
        return True, result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mesh = VRAMMesh(total_vram_bytes=4 * 1024 * 1024 * 1024)
    provisioner = ElasticPSVCProvisioner(mesh)
    governor = MeshGovernor(mesh, provisioner)
    pixelizer = VectorPixelizer(mesh, provisioner, governor)
    
    agent = LidarAgent("lidar_01", provisioner, governor, pixelizer)
    provisioner.allocate(agent.agent_id, 15600, growth_margin=0.3)
    governor.register_agent(agent.agent_id, 1000, 12000)
    
    agent.process_canopy_scan(point_count=1000)
