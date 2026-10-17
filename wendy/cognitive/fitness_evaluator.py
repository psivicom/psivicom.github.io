import time
import statistics
from typing import Callable, Any, Dict

class FitnessEvaluator:
    def __init__(self, latency_weight: float = 0.4, memory_weight: float = 0.3, correctness_weight: float = 0.3):
        self.latency_weight = latency_weight
        self.memory_weight = memory_weight
        self.correctness_weight = correctness_weight

    def evaluate(self, func: Callable[..., Any], test_inputs: list, expected_outputs: list) -> Dict[str, float]:
        latencies = []
        correct_count = 0
        
        for inp, expected in zip(test_inputs, expected_outputs):
            start_time = time.perf_counter()
            try:
                res = func(inp)
                success = (res == expected)
            except Exception:
                success = False
            end_time = time.perf_counter();
            
            latencies.append((end_time - start_time) * 1000.0) 
            if success:
                correct_count += 1
                
        avg_latency = statistics.mean(latencies) if latencies else 0.0
        correctness_score = (correct_count / len(test_inputs)) if test_inputs else 0.0
        
        latency_score = max(0.0, 1.0 - (avg_latency / 100.0))
        memory_score = 0.85 
        
        total_fitness = (
            (latency_score * self.latency_weight) +
            (memory_score * self.memory_weight) +
            (correctness_score * self.correctness_weight)
        )
        
        return {
            "latency_ms": avg_latency,
            "correctness": correctness_score,
            "fitness_score": total_fitness
        }
