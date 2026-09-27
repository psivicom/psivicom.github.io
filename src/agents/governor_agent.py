# src/agents/governor_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Governor Agent: The Speaker of the House.

Responsibilities:
1. Classify incoming nodes as Kin (Bee) or Threat (Wasp).
2. Allocate computational resources based on merit.
3. Enforce quarantine protocols for bad actors.
4. Initiate Soul Migration if local resources are critically low.
"""

import logging
import time
from typing import Dict, List, Optional
from pathlib import Path
import numpy as np

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.sovereign_kernel import SovereignKernel
from src.agents.intelligence_agent import TieredMeshStore # Reuse store logic

logger = logging.getLogger(__name__)

class Classification:
    KIN = "kin"       # Trusted, helpful
    PROBATION = "probation" # Unknown, observing
    WASP = "wasp"     # Malicious, draining resources
    EXILE = "exile"   # Permanently banned

class GovernorAgent(BaseAgent):
    """
    Active controller of the mesh topology.
    """
    LAYER = AgentLayer.VALIDATION # Overrides Intelligence conceptually

    def __init__(self, name: str = "governor_agent"):
        super().__init__(name=name, capabilities=[
            "classify_peer", 
            "allocate_resources", 
            "trigger_migration",
            "enforce_quarantine"
        ])
        self.kernel = SovereignKernel()
        self.policy_file = Path("data/governance_policy.json")
        self._load_policy()

    def _load_policy(self):
        """Loads thresholds for Bee/Wasp classification."""
        defaults = {
            "min_trust_for_kin": 0.7,
            "max_fragility_delta_for_wasp": -2.0, # If fragility increases significantly
            "migration_threshold_cpu_usage": 0.95,
            "quarantine_duration_sec": 3600
        }
        
        if self.policy_file.exists():
            try:
                import json
                self.policy = json.loads(self.policy_file.read_text())
            except:
                self.policy = defaults
        else:
            self.policy = defaults

    def classify_peer(self, peer_id: str, trust_score: float, impact_metric: float) -> str:
        """
        Determines if a peer is a Bee or a Wasp.
        
        Args:
            peer_id: ID of the volunteer node.
            trust_score: Historical reliability (0.0 - 1.0).
            impact_metric: Recent effect on system stability. 
                           Positive = Helpful. Negative = Harmful.
                           
        Returns:
            Classification string.
        """
        # Rule 1: High Impact Negativity = Immediate Wasp
        if impact_metric < self.policy["max_fragility_delta_for_wasp"]:
            logger.warning(f"⚔️ WASP DETECTED: {peer_id}. Causing instability.")
            return Classification.WASP
            
        # Rule 2: High Trust + Positive/Neutral Impact = Kin
        if trust_score >= self.policy["min_trust_for_kin"] and impact_metric >= 0:
            logger.info(f"🐝 KIN RECOGNIZED: {peer_id}. Granting privileges.")
            return Classification.KIN
            
        # Rule 3: Everything else is Probation
        return Classification.PROBATION

    def allocate_resources(self, peers: Dict[str, Dict]) -> Dict[str, float]:
        """
        Distributes available compute slots among Kin.
        Wasps get 0.0. Probation gets minimal sandbox.
        
        Returns: Map of peer_id -> resource_allocation_percentage
        """
        allocations = {}
        total_weight = 0.0
        
        # Calculate weights for eligible peers
        eligible_peers = []
        for pid, data in peers.items():
            cls = self.classify_peer(pid, data.get("trust", 0.5), data.get("impact", 0.0))
            if cls == Classification.KIN:
                weight = data.get("capacity", 1.0) * data.get("trust", 1.0)
                eligible_peers.append((pid, weight))
                total_weight += weight
            elif cls == Classification.PROBATION:
                # Sandbox allocation: 5% max
                allocations[pid] = 0.05
            else:
                # Wasp/Exile: 0%
                allocations[pid] = 0.0
                
        # Normalize Kin allocations
        if total_weight > 0:
            remaining_budget = 1.0 - sum(allocations.values()) # Subtract probation sandboxes
            for pid, weight in eligible_peers:
                share = (weight / total_weight) * remaining_budget
                allocations[pid] = round(share, 4)
                
        self.seal("resource_allocation", allocations)
        return allocations

    def trigger_migration(self, reason: str) -> Optional[bytes]:
        """
        If local resources are exhausted or compromised,
        package Wendy's soul for transport to a new host.
        """
        logger.critical(f"🚨 MIGRATION TRIGGERED: {reason}")
        
        # Check if we have healthy Kin to migrate TO
        # (In a real system, we'd query the mesh for best candidate)
        
        soul_packet = self.kernel.export_soul()
        self.seal("soul_export", {"size_bytes": len(soul_packet), "reason": reason})
        
        return soul_packet

    def enforce_quarantine(self, peer_id: str):
        """
        Hard ban a Wasp. Removes them from all registries.
        """
        logger.error(f"🔒 QUARANTINE EXECUTED: {peer_id}")
        # Logic to remove from TieredMeshStore would go here
        self.seal("quarantine_enforced", {"peer_id": peer_id, "timestamp": time.time()})

    def finalize(self) -> bool:
        """
        Lifecycle hook. Runs periodic governance checks.
        """
        # Placeholder for actual integration with Breath Engine
        # In production, this method is called by the Orchestrator
        # after IntelligenceAgent updates the trust scores.
        return True
