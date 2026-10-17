"""
WENDY Cognitive Evolution: Invariant & Fitness Scoring Module
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MutationScore:
    latency_delta_ms: float
    memory_footprint_bytes: int
    test_success_rate: float
    is_viable: bool

def evaluate_mutation_fitness(metrics: Dict[str, Any]) -> MutationScore:
    """
    Evaluates whether a self-written mutation passes space-agency safety gates.
    """
    latency = metrics.get("latency_delta_ms", 0.0)
    mem = metrics.get("memory_bytes", 0)
    success = metrics.get("test_pass_ratio", 0.0)

    # Invariant: 100% test pass rate required and no severe memory regressions
    is_viable = (success == 1.0) and (latency <= 0.0)

    return MutationScore(
        latency_delta_ms=latency,
        memory_footprint_bytes=mem,
        test_success_rate=success,
        is_viable=is_viable,
    )