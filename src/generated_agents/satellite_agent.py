# ==============================================================================
# FILE: satellite_agent.py
# PATH: psivicom.github.io/satellite_agent.py
# DESCRIPTION: Evolving Satellite Agent for RADARSAT SAR Processing
#              Demonstrates dynamic VRAM evolution during payload processing.
# LICENSE: EUPL-1.2 | COMPLIANCE: NIST SP 800-218, FAIR Open Science
# ==============================================================================

import logging
import numpy as np
import time
from typing import Optional

# Import the elastic core infrastructure
from vram_mesh import VRAMMesh
from src.orchestrator.psvc_provisioner import ElasticPSVCProvisioner
from mesh_governor import MeshGovernor
from src.core.vector_pixelizer import VectorPixelizer

logger = logging.getLogger(__name__)


class SatelliteAgent:
    """
    An evolving agent specialized in processing RADARSAT SAR and NASA Earthdata.
    It dynamically requests VRAM expansion when processing large or complex payloads.
    """
    
    def __init__(self, agent_id: str, provisioner: ElasticPSVCProvisioner, 
                 governor: MeshGovernor, pixelizer: VectorPixelizer):
        self.agent_id = agent_id
        self.provisioner = provisioner
        self.governor = governor
        self.pixelizer = pixelizer
        
        # Constants for SAR payload processing
        self.bytes_per_pixel = 8  # float64
        self.overhead_factor = 1.2  # 20% overhead for intermediate calculations
        
        logger.info(f"SatelliteAgent {self.agent_id} initialized.")

    def process_sar_payload(self, payload_dimensions: int) -> bool:
        """
        Processes a RADARSAT SAR payload.
        If the payload requires more VRAM than currently allocated, 
        it triggers an elastic evolution before processing.
        
        Args:
            payload_dimensions: The size/complexity of the SAR payload (e.g., number of pixels).
            
        Returns:
            True if processing succeeded, False otherwise.
        """
        logger.info(f"[{self.agent_id}] Starting SAR payload processing. Dimensions: {payload_dimensions}")
        
        # 1. Calculate required VRAM for this payload
        required_vram = self._calculate_required_vram(payload_dimensions)
        
        # 2. Check current allocation
        current_handle = self.provisioner.get_handle(self.agent_id)
        if not current_handle:
            logger.error(f"[{self.agent_id}] No VRAM handle found. Cannot process.")
            return False
            
        current_vram = current_handle.size_bytes
        
        # 3. EVOLUTION CHECK: Do we need to grow?
        if required_vram > current_vram:
            logger.warning(f"[{self.agent_id}] Payload requires {required_vram} bytes, "
                           f"but only {current_vram} allocated. Triggering evolution...")
            
            # Request evolution from the Governor
            # The Governor will enforce security checks (rate limiting, max growth)
            success = self.governor.request_evolution(
                self.agent_id, 
                new_dimensions=payload_dimensions, 
                new_memory=required_vram
            )
            
            if not success:
                logger.error(f"[{self.agent_id}] Evolution FAILED. Payload too large or rate-limited.")
                self.governor.deposit_pheromone(self.agent_id, "evolution_failed:memory_limit")
                return False
                
            logger.info(f"[{self.agent_id}] Evolution SUCCESS. VRAM expanded to {required_vram} bytes.")
            self.governor.deposit_pheromone(self.agent_id, f"evolution_success:{required_vram}")
        else:
            logger.debug(f"[{self.agent_id}] Payload fits in current allocation ({current_vram} bytes).")
            
        # 4. Execute the actual vector math (SAR backscatter fusion)
        # We simulate the payload data here
        simulated_payload = np.random.rand(payload_dimensions).astype(np.float64)
        
        success, result = self.pixelizer.execute_vector_math(
            self.agent_id, 
            operation="transform",  # e.g., SAR backscatter transformation
            input_data=simulated_payload
        )
        
        if not success:
            logger.error(f"[{self.agent_id}] Vector math execution failed.")
            return False
            
        # 5. Deposit final pheromone for FAIR audit trail
        self.governor.deposit_pheromone(self.agent_id, f"sar_processed:{payload_dimensions}")
        logger.info(f"[{self.agent_id}] SAR payload processed successfully.")
        
        return True

    def _calculate_required_vram(self, dimensions: int) -> int:
        """Calculates the VRAM required for a given payload size."""
        base_bytes = dimensions * self.bytes_per_pixel
        return int(base_bytes * self.overhead_factor)


# ==============================================================================
# Example Usage / Test Harness
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 1. Initialize the shared elastic infrastructure
    vram_mesh = VRAMMesh(total_vram_bytes=4 * 1024 * 1024 * 1024) # 4GB
    provisioner = ElasticPSVCProvisioner(vram_mesh)
    governor = MeshGovernor(vram_mesh, provisioner)
    pixelizer = VectorPixelizer(vram_mesh, provisioner, governor)
    
    # 2. Initialize the Satellite Agent
    agent = SatelliteAgent("satellite_agent_01", provisioner, governor, pixelizer)
    
    # 3. Register the agent with a small initial allocation
    initial_dims = 1024
    initial_memory = agent._calculate_required_vram(initial_dims)
    provisioner.allocate(agent.agent_id, initial_memory, growth_margin=0.2)
    governor.register_agent(agent.agent_id, initial_dims, initial_memory)
    
    # 4. Process a small payload (should fit without evolution)
    print("\n--- Processing Small Payload ---")
    agent.process_sar_payload(payload_dimensions=1000)
    
    # 5. Process a MASSIVE payload (should trigger evolution)
    print("\n--- Processing Massive Payload (Triggering Evolution) ---")
    agent.process_sar_payload(payload_dimensions=50000)
    
    # 6. Check final state
    print("\n--- Final Mesh Status ---")
    status = governor.get_mesh_status()
    print(f"Agent Generations: {status['provisioner_stats']['average_generation']}")
    print(f"VRAM Utilization: {status['vram_stats']['utilization_percent']:.2f}%")
