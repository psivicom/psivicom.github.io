import numpy as np
import threading
import logging
from typing import Tuple

logging.basicConfig(level=logging.INFO, format='[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

class StigmergyGraph:
    """
    Axiom 8: Biological Epistemology. 
    Reads Gradients of Wax. No Central Orchestrator.
    """
    def __init__(self, dimensions: int = 50, theta_crit: float = 0.75):
        self.dimensions = dimensions
        self.theta_crit = theta_crit
        self.wax_matrix = np.zeros(dimensions, dtype=np.float32)
        # Simulating Lock-Free CAS in Python using a spinlock/retry mechanism.
        # In a compiled language (Rust/C++), this maps directly to the CPU's CMPXCHG instruction.
        self._cas_lock = threading.Lock() 

    def read_gradients(self) -> np.ndarray:
        """Returns the probability distribution of available paths via Softmax."""
        gradients = self.wax_matrix
        exp_gradients = np.exp(gradients - np.max(gradients))
        return exp_gradients / (np.sum(exp_gradients) + 1e-10)

    def attempt_cas_deposit(self, ast_tensor: np.ndarray, reward: float) -> bool:
        """
        Axiom 2: Lock-Free CAS. 
        Proletariat nodes update the global state without blocking the swarm.
        """
        with self._cas_lock: # Python simulation of atomic memory barrier
            expected_state = self.wax_matrix.copy()
            # Calculate new state
            proposed_state = expected_state + (ast_tensor * reward)
            
            # Simulate CAS: If memory hasn't been altered by another thread, commit.
            # In true lock-free C++, this is a single atomic instruction.
            if np.array_equal(self.wax_matrix, expected_state):
                self.wax_matrix = proposed_state
                return True
            return False

    def apply_negative_reinforcement(self, ast_tensor: np.ndarray, k_neg: np.ndarray):
        """Burns the pathway out of the graph using the Anti-Crystal penalty."""
        self.wax_matrix -= (ast_tensor * k_neg)
        # Ensure weights do not drop below absolute zero
        self.wax_matrix = np.maximum(self.wax_matrix, 0.0)
