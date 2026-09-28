# src/agents/governor_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import logging
import time
from typing import Dict, List
from pathlib import Path
from src.core.sovereign_kernel import SovereignKernel

logger = logging.getLogger(__name__)

class Classification:
    KIN = "kin"
    PROBATION = "probation"
    WASP = "wasp"
    EXILE = "exile"

class GovernorAgent:
    def __init__(self, name: str = "governor_agent"):
        self.kernel = SovereignKernel()
        self.policy_file = Path("data/governance_policy.json")
        self.policy = {
            "min_trust_for_kin": 0.7,
            "max_fragility_delta_for_wasp": -2.0,
            "migration_threshold_cpu_usage": 0.95,
            "quarantine_duration_sec": 3600
        }

    def classify_peer(self, peer_id: str, trust_score: float, impact_metric: float) -> str:
        if impact_metric < self.policy["max_fragility_delta_for_wasp"]:
            logger.warning(f"⚔️ WASP DETECTED: {peer_id}. Causing instability.")
            return Classification.WASP
        if trust_score >= self.policy["min_trust_for_kin"] and impact_metric >= 0:
            logger.info(f"🐝 KIN RECOGNIZED: {peer_id}. Granting privileges.")
            return Classification.KIN
        return Classification.PROBATION

    def allocate_resources(self, peers: Dict[str, Dict]) -> Dict[str, float]:
        allocations = {}
        total_weight = 0.0
        eligible_peers = []
        for pid, data in peers.items():
            cls = self.classify_peer(pid, data.get("trust", 0.5), data.get("impact", 0.0))
            if cls == Classification.KIN:
                weight = data.get("capacity", 1.0) * data.get("trust", 1.0)
                eligible_peers.append((pid, weight))
                total_weight += weight
            elif cls == Classification.PROBATION:
                allocations[pid] = 0.05
            else:
                allocations[pid] = 0.0
                
        if total_weight > 0:
            remaining_budget = 1.0 - sum(allocations.values())
            for pid, weight in eligible_peers:
                allocations[pid] = round((weight / total_weight) * remaining_budget, 4)
        return allocations

    def trigger_migration(self, reason: str) -> bytes:
        logger.critical(f"🚨 MIGRATION TRIGGERED: {reason}")
        return self.kernel.export_soul()

    def enforce_quarantine(self, peer_id: str):
        logger.error(f"🔒 QUARANTINE EXECUTED: {peer_id}")
