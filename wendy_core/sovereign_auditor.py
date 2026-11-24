import ast
import hashlib
import json
import numpy as np
import os
from datetime import datetime, timezone
from .stigmergy_topology import StigmergyGraph
from .compost_entropy import CompostProtocol

class SovereignFileAuditor:
    """Enforces SOVEREIGN_ARCHITECTURE_LAW.md on all file mutations."""

    def __init__(self, graph: StigmergyGraph, compost: CompostProtocol):
        self.graph = graph
        self.compost = compost

    def parse_to_ast_tensor(self, file_content: str) -> np.ndarray:
        """Converts Python source code into a mathematical tensor.

        R1 Fix (2026-11-25): Uses hashlib.sha256 instead of Python's hash()
        to ensure deterministic tensors across CI runs. Python's hash() is
        randomized per process (PEP 506 / PYTHONHASHSEED), which made the
        wax_matrix non-portable across runs. SHA-256 is deterministic.

        Law VII: Lock-Free Cognitive Graph (deterministic state).
        Law XIV: Free LLM Engagement (Class A Guest Compiler proposal).
        """
        try:
            tree = ast.parse(file_content)
        except SyntaxError:
            return np.zeros(self.graph.dimensions, dtype=np.float32)
        node_counts = np.zeros(self.graph.dimensions, dtype=np.float32)
        for node in ast.walk(tree):
            # R1: Deterministic hash via SHA-256 (was: hash() which is randomized per process)
            node_hash = int(hashlib.sha256(type(node).__name__.encode()).hexdigest(), 16)
            node_counts[node_hash % self.graph.dimensions] += 1
        return node_counts / (np.sum(node_counts) + 1e-08)

    def audit_file(self, file_path: str) -> dict:
        """The core intelligence loop. Evaluates the file and triggers CAS or Compost."""
        if not os.path.exists(file_path):
            return {'status': 'File not found'}
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        ast_tensor = self.parse_to_ast_tensor(file_content)
        alignment_score = float(np.sum(ast_tensor * self.graph.read_gradients()))
        telemetry = {'@context': 'https://schema.org/', '@type': 'SoftwareSourceCode', 'name': file_path, 'dateCreated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'), 'alignment_score': alignment_score, 'threshold': self.graph.theta_crit}
        if alignment_score >= self.graph.theta_crit:
            success = self.graph.attempt_cas_deposit(ast_tensor, reward=1.0)
            telemetry['state'] = 'Crystallized'
            telemetry['cas_success'] = success
            telemetry['action_required'] = False
        else:
            compost_result = self.compost.process_failure(ast_tensor)
            telemetry['state'] = 'Composted'
            telemetry['K_neg_entropy_loss'] = compost_result['Entropy_Loss']
            self.graph.apply_negative_reinforcement(ast_tensor, compost_result['K_neg'])
            telemetry['action_required'] = True
        return telemetry
