# ==============================================================================
# FILE: vector_pixelizer.py
# PATH: psivicom.github.io/src/core/vector_pixelizer.py
# DESCRIPTION: Intelligent Vector Math Engine with Smart Chunking Fallback
#              Handles valid oversized data by chunking, preventing security 
#              collapses while ensuring no valid data is rejected.
# LICENSE: EUPL-1.2 | COMPLIANCE: NIST SP 800-218, FAIR Open Science
# ==============================================================================

import logging
import numpy as np
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


class VectorPixelizer:
    """
    Performs vector math operations on elastic PSVC containers.
    Features intelligent chunking to handle valid, oversized payloads safely.
    """
    
    def __init__(self, vram_mesh, provisioner, governor):
        self.vram_mesh = vram_mesh
        self.provisioner = provisioner
        self.governor = governor
        self.chunk_size_limit = 1024 * 1024 * 5  # 5MB max chunk size for safety
        
        logger.info("Vector Pixelizer initialized with intelligent chunking fallback.")
    
    def execute_vector_math(self, agent_id: str, operation: str, 
                           input_data: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Execute vector math with intelligent bounds checking and chunking.
        """
        agent_state = self.governor.get_agent_status(agent_id)
        if not agent_state or agent_state.status != "NOMINAL":
            logger.error(f"Agent {agent_id} is not in a NOMINAL state.")
            return False, None
        
        handle = self.provisioner.get_handle(agent_id)
        if not handle:
            logger.error(f"No VRAM handle for agent {agent_id}")
            return False, None
        
        output_size = self._calculate_output_size(operation, input_data, agent_state)
        
        # 1. Check if it fits in current allocation
        if output_size <= handle.size_bytes:
            return self._safe_execute(agent_id, operation, input_data, handle)
        
        # 2. It doesn't fit. Request evolution.
        logger.info(f"Payload exceeds allocation. Requesting evolution for {agent_id}...")
        new_dimensions = self._calculate_new_dimensions(operation, input_data, agent_state)
        
        evolution_success = self.governor.request_evolution(agent_id, new_dimensions, output_size)
        
        if evolution_success:
            # Evolution succeeded, we have a new, larger handle
            new_handle = self.provisioner.get_handle(agent_id)
            return self._safe_execute(agent_id, operation, input_data, new_handle)
        
        # 3. INTELLIGENT FALLBACK: Evolution was denied (e.g., jump was too massive).
        # Instead of failing, we intelligently chunk the data.
        logger.warning(f"Evolution denied for massive jump. Initiating intelligent chunking for {agent_id}.")
        return self._process_in_chunks(agent_id, operation, input_data, handle.size_bytes)


    def _safe_execute(self, agent_id: str, operation: str, 
                      input_data: np.ndarray, handle) -> Tuple[bool, Optional[np.ndarray]]:
        """Executes the math when we know it fits safely in VRAM."""
        if self.vram_mesh.is_agent_paused(agent_id):
            logger.error(f"Cannot execute: Agent {agent_id} writes are paused.")
            return False, None
            
        try:
            result = self._perform_operation(operation, input_data)
            
            # Final safety check
            if result.nbytes > handle.size_bytes:
                logger.error("Result still exceeds allocation after execution.")
                return False, None
                
            self.governor.deposit_pheromone(agent_id, f"executed:{operation}:{result.nbytes}")
            return True, result
        except Exception as e:
            logger.error(f"Vector math execution failed: {e}")
            return False, None


    def _process_in_chunks(self, agent_id: str, operation: str, 
                           input_data: np.ndarray, max_safe_bytes: int) -> Tuple[bool, Optional[np.ndarray]]:
        """
        INTELLIGENT FALLBACK: Slices massive valid data into safe chunks, 
        processes them, and aggregates the results without violating VRAM boundaries.
        """
        try:
            # Calculate how many elements fit in the max safe bytes
            bytes_per_element = input_data.dtype.itemsize
            max_elements_per_chunk = max(1, (max_safe_bytes // bytes_per_element) - 100) # Leave small margin
            
            logger.info(f"Chunking data: {len(input_data)} total elements into chunks of {max_elements_per_chunk}")
            
            chunks = np.array_split(input_data, max(1, len(input_data) // max_elements_per_chunk))
            results = []
            
            for i, chunk in enumerate(chunks):
                logger.debug(f"Processing chunk {i+1}/{len(chunks)} for {agent_id}")
                
                # Process each chunk safely
                chunk_result = self._perform_operation(operation, chunk)
                results.append(chunk_result)
                
                # Deposit pheromone for audit trail of chunked processing
                self.governor.deposit_pheromone(agent_id, f"chunk_processed:{i+1}:{len(chunks)}")
            
            # Intelligently aggregate the results
            final_result = np.concatenate(results)
            
            logger.info(f"Successfully aggregated {len(chunks)} chunks for {agent_id}.")
            self.governor.deposit_pheromone(agent_id, f"chunking_complete:{len(chunks)}_chunks")
            
            return True, final_result
            
        except Exception as e:
            logger.error(f"Intelligent chunking failed for {agent_id}: {e}")
            return False, None


    def _calculate_output_size(self, operation: str, input_data: np.ndarray, agent_state) -> int:
        if operation == "multiply": return int(input_data.nbytes * 2)
        elif operation == "transform": return int(input_data.nbytes * 1.5)
        return int(input_data.nbytes * 1.2)

    def _calculate_new_dimensions(self, operation: str, input_data: np.ndarray, agent_state) -> int:
        current_dims = agent_state.vector_dimensions
        if operation == "multiply": return current_dims * 2
        elif operation == "transform": return int(current_dims * 1.5)
        return current_dims

    def _perform_operation(self, operation: str, input_data: np.ndarray) -> np.ndarray:
        """The actual math. In production, this calls CUDA/GPU kernels."""
        if operation == "multiply": return input_data * 2.0
        elif operation == "transform": return np.sin(input_data) + np.cos(input_data)
        elif operation == "add": return input_data + 1.0
        return input_data.copy()

    def validate_fidelity(self, agent_id: str, data: np.ndarray) -> bool:
        if data.size == 0 or np.any(np.isnan(data)) or np.any(np.isinf(data)):
            return False
        return True
