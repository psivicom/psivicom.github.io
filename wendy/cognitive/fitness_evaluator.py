from typing import Dict, Any

class FitnessEvaluator:
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            "execution_speed": 0.3,
            "memory_efficiency": 0.3,
            "code_complexity": 0.2,
            "robustness": 0.2
        }

    def evaluate(self, metrics: Dict[str, float]) -> float:
        total_score = 0.0
        total_weight = 0.0
        
        for metric, weight in self.weights.items():
            if metric in metrics:
                val = float(metrics[metric])
                total_score += val * weight
                total_weight += weight
                
        if total_weight == 0.0:
            return 0.0
            
        return max(0.0, min(1.0, total_score / total_weight))

    def evaluate_ast_complexity(self, node_count: int, max_allowed_nodes: int = 500) -> float:
        if node_count >= max_allowed_nodes:
            return 0.0
        return 1.0 - (node_count / max_allowed_nodes)
