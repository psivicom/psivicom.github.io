# ==============================================================================
# FILE: forage_agent.py
# PATH: psivicom.github.io/src/agents/forage_agent.py
# DESCRIPTION: Evolving Forage Agent for Pollinator & RADARSAT Data Fusion
# Utilizes intelligent chunking and elastic VRAM provisioning.
# LICENSE: EUPL-1.2 | COMPLIANCE: NIST SP 800-218, FAIR Open Science
# ==============================================================================

import logging
import numpy as np
import time
from typing import Optional, Tuple

# CORRECT absolute imports from the repository root (PYTHONPATH)
from src.mesh.vram_mesh import VRAMMesh
from src.orchestrator.psvc_provisioner import ElasticPSVCProvisioner
from src.mesh.mesh_governor import MeshGovernor
from src.core.vector_pixelizer import VectorPixelizer

logger = logging.getLogger(__name__)

class ForageAgent:
    """
    An evolving agent specialized in fusing pollinator telemetry with 
    RADARSAT SAR soil moisture data. Dynamically handles data bursts.
    """
    
    def __init__(self, agent_id: str, provisioner: ElasticPSVCProvisioner, 
                 governor: MeshGovernor, pixelizer: VectorPixelizer):
        self.agent_id = agent_id
        self.provisioner = provisioner
        self.governor = governor
        self.pixelizer = pixelizer
        
        # Constants for ecological data processing
        self.bytes_per_sample = 8  # float64 for high-precision sensor data
        self.fusion_overhead = 1.3  # 30% overhead for SAR-optical fusion math
        
        logger.info(f"ForageAgent {self.agent_id} initialized and ready for telemetry.")

    def process_fusion_batch(self, sample_count: int) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Processes a batch of pollinator and RADARSAT fusion data.
        Automatically handles elastic evolution or intelligent chunking 
        if the data burst exceeds current VRAM boundaries.
        """
        logger.info(f"[{self.agent_id}] Starting fusion batch. Samples: {sample_count}")
        
        # 1. Calculate required VRAM for this specific data burst
        required_vram = self._calculate_required_vram(sample_count)
        
        # 2. Check current allocation
        current_handle = self.provisioner.get_handle(self.agent_id)
        if not current_handle:
            logger.error(f"[{self.agent_id}] No VRAM handle found. Cannot process.")
            return False, None
            
        current_vram = current_handle.size_bytes
        
        # 3. EVOLUTION CHECK: Do we need to grow?
        if required_vram > current_vram:
            logger.warning(f"[{self.agent_id}] Burst requires {required_vram} bytes, "
                           f"but only {current_vram} allocated. Requesting evolution...")
            
            # Request evolution from the Governor
            success = self.governor.request_evolution(
                self.agent_id, 
                new_dimensions=sample_count, 
                new_memory=required_vram
            )
            
            if not success:
                logger.info(f"[{self.agent_id}] Evolution denied. "
                            f"VectorPixelizer will automatically initiate intelligent chunking.")
                
        # 4. Execute the vector math (SAR-optical fusion)
        simulated_fusion_data = np.random.rand(sample_count).astype(np.float64)
        
        success, result = self.pixelizer.execute_vector_math(
            self.agent_id, 
            operation="transform",  # Represents the SAR-optical fusion algorithm
            input_data=simulated_fusion_data
        )
        
        if not success:
            logger.error(f"[{self.agent_id}] Fusion execution failed.")
            return False, None
            
        # 5. Deposit final pheromone for FAIR audit trail
        self.governor.deposit_pheromone(self.agent_id, f"fusion_complete:{sample_count}_samples")
        logger.info(f"[{self.agent_id}] Fusion batch processed successfully.")
        
        return True, result

    def _calculate_required_vram(self, sample_count: int) -> int:
        """Calculates the VRAM required for a given batch size."""
        base_bytes = sample_count * self.bytes_per_sample
        return int(base_bytes * self.fusion_overhead)

# ==============================================================================
# Example Usage / Local Test Harness
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 1. Initialize the shared elastic infrastructure
    vram_mesh = VRAMMesh(total_vram_bytes=4 * 1024 * 1024 * 1024) # 4GB
    provisioner = ElasticPSVCProvisioner(vram_mesh)
    governor = MeshGovernor(vram_mesh, provisioner)
    pixelizer = VectorPixelizer(vram_mesh, provisioner, governor)
    
    # 2. Initialize the Forage Agent
    agent = ForageAgent("forage_agent_01", provisioner, governor, pixelizer)
    
    # 3. Register the agent with a small initial allocation
    initial_samples = 1000
    initial_memory = agent._calculate_required_vram(initial_samples)
    provisioner.allocate(agent.agent_id, initial_memory, growth_margin=0.2)
    governor.register_agent(agent.agent_id, initial_samples, initial_memory)
    
    # 4. Process a normal, expected batch
    print("\n--- Processing Normal Forage Batch ---")
    agent.process_fusion_batch(sample_count=1000)
    
    # 5. Process a MASSIVE data burst
    print("\n--- Processing Massive Data Burst ---")
    agent.process_fusion_batch(sample_count=500000)
    
    # 6. Check final state
    print("\n--- Final Mesh Status ---")
    status = governor.get_mesh_status()
    print(f"Agent Generations: {status['provisioner_stats']['average_generation']:.2f}")
    print(f"VRAM Utilization: {status['vram_stats']['utilization_percent']:.2f}%")
