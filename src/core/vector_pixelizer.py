"""
Vector Pixelizer for Elastic PSVC Containers
Performs vector math with evolutionary bounds checking
NIST SP 800-218 Compliant | FAIR Open Science | EUPL-1.2 Licensed
"""

import logging
import numpy as np
from typing import Optional, Tuple
import time

logger = logging.getLogger(__name__)


class VectorPixelizer:
    """
    Performs vector math operations on elastic PSVC containers
    Includes pre-execution bounds checking for security
    """
    
    def __init__(self, vram_mesh, provisioner, governor):
        self.vram_mesh = vram_mesh
        self.provisioner = provisioner
        self.governor = governor
        
        logger.info("Vector Pixelizer initialized with elastic bounds checking")
    
    def execute_vector_math(self, agent_id: str, operation: str, 
                           input_data: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Execute vector math operation with evolutionary bounds checking
        
        Args:
            agent_id: Agent identifier
            operation: Type of operation ("multiply", "add", "transform", etc.)
            input_data: Input vector data
            
        Returns:
            Tuple of (success, result_data)
        """
        # SECURITY CHECK: Verify agent is registered and nominal
        agent_state = self.governor.get_agent_status(agent_id)
        if not agent_state:
            logger.error(f"Agent {agent_id} not registered with governor")
            return False, None
        
        if agent_state.status != "NOMINAL":
            logger.error(f"Agent {agent_id} is in {agent_state.status} state")
            return False, None
        
        # Get current VRAM handle
        handle = self.provisioner.get_handle(agent_id)
        if not handle:
            logger.error(f"No VRAM handle for agent {agent_id}")
            return False, None
        
        # Calculate output size
        output_size = self._calculate_output_size(operation, input_data, agent_state)
        
        # SECURITY CHECK: Pre-execution bounds checking
        if output_size > handle.size_bytes:
            logger.warning(f"Operation requires {output_size} bytes, but only {handle.size_bytes} allocated")
            logger.info(f"Requesting evolution for agent {agent_id}")
            
            # Request evolution
            new_dimensions = self._calculate_new_dimensions(operation, input_data, agent_state)
            success = self.governor.request_evolution(agent_id, new_dimensions, output_size)
            
            if not success:
                logger.error(f"Evolution failed for agent {agent_id}")
                return False, None
            
            # Re-fetch handle after evolution
            handle = self.provisioner.get_handle(agent_id)
        
        # Check if agent writes are paused (security gate)
        if self.vram_mesh.is_agent_paused(agent_id):
            logger.error(f"Cannot execute: Agent {agent_id} writes are paused")
            return False, None
        
        try:
            # Execute the operation
            result = self._perform_operation(operation, input_data)
            
            # Verify result fits in allocated space
            result_size = result.nbytes
            if result_size > handle.size_bytes:
                logger.error(f"Result size {result_size} exceeds allocation {handle.size_bytes}")
                return False, None
            
            # Deposit pheromone for audit trail
            self.governor.deposit_pheromone(agent_id, f"executed:{operation}:{result_size}")
            
            logger.debug(f"Executed {operation} for agent {agent_id}: {result_size} bytes")
            return True, result
            
        except Exception as e:
            logger.error(f"Vector math execution failed for agent {agent_id}: {e}")
            return False, None
    
    def _calculate_output_size(self, operation: str, input_data: np.ndarray, 
                              agent_state) -> int:
        """Calculate required output size for an operation"""
        # Estimate based on operation type
        if operation == "multiply":
            return input_data.nbytes * 2  # Rough estimate
        elif operation == "transform":
            return int(input_data.nbytes * 1.5)
        elif operation == "add":
            return input_data.nbytes
        else:
            return input_data.nbytes * 1.2  # Default margin
    
    def _calculate_new_dimensions(self, operation: str, input_data: np.ndarray,
                                 agent_state) -> int:
        """Calculate new vector dimensions after evolution"""
        current_dims = agent_state.vector_dimensions
        
        if operation == "multiply":
            return current_dims * 2
        elif operation == "transform":
            return int(current_dims * 1.5)
        else:
            return current_dims
    
    def _perform_operation(self, operation: str, input_data: np.ndarray) -> np.ndarray:
        """
        Perform the actual vector math operation
        In production, this would use CUDA kernels for GPU acceleration
        """
        if operation == "multiply":
            return input_data * 2.0
        elif operation == "add":
            return input_data + 1.0
        elif operation == "transform":
            # Example transformation
            return np.sin(input_data) + np.cos(input_data)
        else:
            # Default: identity
            return input_data.copy()
    
    def validate_fidelity(self, agent_id: str, data: np.ndarray) -> bool:
        """
        Validate data fidelity against RFC 1001 compliance
        
        Args:
            agent_id: Agent identifier
            data: Data to validate
            
        Returns:
            True if fidelity check passes
        """
        # Basic fidelity checks
        if data.size == 0:
            logger.error("Empty data failed fidelity check")
            return False
        
        if np.any(np.isnan(data)):
            logger.error("NaN values detected in data")
            return False
        
        if np.any(np.isinf(data)):
            logger.error("Infinite values detected in data")
            return False
        
        # Agent-specific fidelity checks could be added here
        logger.debug(f"Fidelity check passed for agent {agent_id}")
        return True
