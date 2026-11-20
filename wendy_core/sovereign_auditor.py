import ast
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
        """Converts Python source code into a mathematical tensor."""
        try:
            tree = ast.parse(file_content)
        except SyntaxError:
            return np.zeros(self.graph.dimensions, dtype=np.float32)
        node_counts = np.zeros(self.graph.dimensions, dtype=np.float32)
        for node in ast.walk(tree):
            node_counts[hash(type(node).__name__) % self.graph.dimensions] += 1
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