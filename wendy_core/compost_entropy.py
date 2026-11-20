import numpy as np
import logging

class CompostProtocol:
    """
    Axiom 4: T(H_fail) -> {K_neg, S_valid}.
    Axiom 5: NASA Open Science: H(Psi_W|E_export)=0.
    """

    def __init__(self):
        self.k_neg_archive = []

    def calculate_shannon_entropy(self, probability_distribution: np.ndarray) -> float:
        """Measures the thermodynamic entropy of the current state."""
        p = probability_distribution + 1e-10
        return float(-np.sum(p * np.log2(p)))

    def process_failure(self, h_fail_state: np.ndarray) -> dict:
        """Composts high-entropy failures into negative constraints (K_neg)."""
        entropy = self.calculate_shannon_entropy(h_fail_state)
        k_neg = 1.0 - h_fail_state
        self.k_neg_archive.append(k_neg)
        logging.info(f'Compost Protocol: H_fail detected. Entropy={entropy:.4f}. K_neg extracted.')
        return {'K_neg': k_neg, 'Entropy_Loss': entropy, 'S_valid': True}