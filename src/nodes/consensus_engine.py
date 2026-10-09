# src/nodes/consensus_engine.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Consensus Engine: The Supreme Court of the Mesh.
Resolves conflicting results from multiple volunteer nodes processing the same data.
Uses cryptographic verification, vector similarity, and reputation-weighted voting
to establish the single, immutable "truth" before sealing it to the Vanguard Ledger.
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from src.core.zulu_clock import get_zulu_timestamp_ms
from src.core.psvc_sovereign import SovereignPSVC

logger = logging.getLogger("CONSENSUS_ENGINE")

class ConsensusEngine:
    def __init__(self, governor, ledger_path: str = "data/vanguard_ledger.jsonl", min_votes: int = 3):
        self.governor = governor
        self.ledger_path = Path(ledger_path)
        self.min_votes = min_votes
        
        # Buffer for incoming proposals: { task_id: [ {node_id, vector, weight, timestamp}, ... ] }
        self.proposals: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.sealed_truths: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"⚖️ Consensus Engine initialized. Quorum: {min_votes} nodes.")

    def submit_proposal(self, task_id: str, node_id: str, result_vector: np.ndarray, signature: str) -> bool:
        """
        Receives a result proposal from a volunteer node.
        Verifies the node's reputation and stores the proposal for consensus.
        """
        if not isinstance(result_vector, np.ndarray) or result_vector.dtype != np.float32:
            logger.error(f"🚫 Rejected proposal from {node_id}: Invalid vector format (must be float32).")
            return False

        # 1. Check Node Reputation (Pheromones)
        weight = self._calculate_reputation_weight(node_id)
        if weight <= 0:
            logger.warning(f"⚠️ Node {node_id} has zero reputation. Proposal ignored.")
            return False

        proposal = {
            "node_id": node_id,
            "vector": result_vector,
            "weight": weight,
            "timestamp": get_zulu_timestamp_ms(),
            "signature": signature # Store for audit, though verification happens at ingress
        }
        
        self.proposals[task_id].append(proposal)
        logger.info(f"🗳️ Proposal received for {task_id} from {node_id} (Weight: {weight:.2f}). Total votes: {len(self.proposals[task_id])}")
        
        # 2. Attempt Consensus if Quorum is Met
        if len(self.proposals[task_id]) >= self.min_votes:
            return self.attempt_consensus(task_id)
            
        return True

    def _calculate_reputation_weight(self, node_id: str) -> float:
        """
        Queries the MeshGovernor for the node's reputation score.
        'Stable' nodes get 1.0, 'Degraded' get 0.1, Unknown get 0.5.
        """
        pheromones = self.governor.pheromones.get(node_id, [])
        
        if "stable" in pheromones:
            return 1.0
        elif "degraded" in pheromones:
            return 0.1
        elif "malicious" in pheromones:
            return 0.0
        else:
            return 0.5 # Default trust for new nodes

    def attempt_consensus(self, task_id: str) -> bool:
        """
        Analyzes all proposals for a task. 
        Groups similar vectors, applies weights, and selects the 'Truth'.
        """
        votes = self.proposals[task_id]
        if len(votes) < self.min_votes:
            return False

        logger.info(f"⚖️ Attempting consensus for {task_id} with {len(votes)} votes...")
        
        # 1. Cluster vectors by similarity (Cosine Similarity > 0.95)
        clusters = self._cluster_vectors(votes)
        
        if not clusters:
            self._flag_fragility_trap(task_id, "No consensus: All vectors are orthogonal/divergent.")
            return False

        # 2. Find the cluster with the highest total weight
        winning_cluster = max(clusters, key=lambda c: c["total_weight"])
        
        # 3. Check if the winning cluster has > 50% of the total weight (Majority Rule)
        total_weight_all = sum(v["weight"] for v in votes)
        confidence = winning_cluster["total_weight"] / total_weight_all
        
        if confidence < 0.51:
            self._flag_fragility_trap(task_id, f"No clear majority. Confidence: {confidence:.2f}")
            return False

        # 4. Seal the Truth
        winning_vector = winning_cluster["centroid"]
        self._seal_truth(task_id, winning_vector, confidence, winning_cluster["members"])
        
        # 5. Clean up buffer
        del self.proposals[task_id]
        return True

    def _cluster_vectors(self, votes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple greedy clustering based on cosine similarity."""
        clusters = []
        used_indices = set()
        
        for i, vote_a in enumerate(votes):
            if i in used_indices:
                continue
                
            cluster_members = [vote_a]
            used_indices.add(i)
            
            for j, vote_b in enumerate(votes):
                if j in used_indices:
                    continue
                    
                    # Calculate Cosine Similarity
                    sim = self._cosine_similarity(vote_a["vector"], vote_b["vector"])
                    if sim > 0.95: # High threshold for "Truth"
                        cluster_members.append(vote_b)
                        used_indices.add(j)
            
            # Calculate cluster metrics
            total_weight = sum(m["weight"] for m in cluster_members)
            centroid = np.mean([m["vector"] for m in cluster_members], axis=0).astype(np.float32)
            
            clusters.append({
                "members": [m["node_id"] for m in cluster_members],
                "total_weight": total_weight,
                "centroid": centroid,
                "size": len(cluster_members)
            })
            
        return clusters

    @staticmethod
    def _cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))

    def _seal_truth(self, task_id: str, vector: np.ndarray, confidence: float, members: List[str]):
        """Writes the final consensus to the immutable Vanguard Ledger."""
        truth_record = {
            "timestamp": get_zulu_timestamp_ms(),
            "action": "CONSENSUS_SEALED",
            "actor": "consensus_engine",
            "task_id": task_id,
            "confidence": float(confidence),
            "vector_hash": self._hash_vector(vector),
            "participating_nodes": members,
            "authority": "Hive Mind Quorum"
        }
        
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(truth_record) + "\n")
            
        self.sealed_truths[task_id] = truth_record
        logger.info(f"✅ TRUTH SEALED for {task_id}. Confidence: {confidence:.2%}. Nodes: {members}")

    def _flag_fragility_trap(self, task_id: str, reason: str):
        """If consensus fails, this data is flagged as a 'Fragility Trap' for the LiteratureAgent."""
        trap_record = {
            "timestamp": get_zulu_timestamp_ms(),
            "action": "FRAGILITY_TRAP_FLAGGED",
            "actor": "consensus_engine",
            "task_id": task_id,
            "reason": reason,
            "resolution_status": "pending_literature_review"
        }
        
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(trap_record) + "\n")
            
        logger.warning(f"⚠️ FRAGILITY TRAP: {task_id} - {reason}. Routing to LiteratureAgent.")

    @staticmethod
    def _hash_vector(vector: np.ndarray) -> str:
        import hashlib
        return hashlib.sha256(vector.tobytes()).hexdigest()[:16]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    # Mock Governor for testing
    class MockGovernor:
        pheromones = {
            "node_alpha": ["stable"],
            "node_beta": ["stable"],
            "node_gamma": ["degraded"],
            "node_delta": ["malicious"]
        }
        
    engine = ConsensusEngine(governor=MockGovernor(), min_votes=3)
    
    # Simulate 3 nodes processing the same task
    task_id = "goldstream_sar_patch_001"
    true_vector = np.random.randn(16).astype(np.float32)
    
    # Alpha and Beta agree (High similarity)
    engine.submit_proposal(task_id, "node_alpha", true_vector, "sig_1")
    engine.submit_proposal(task_id, "node_beta", true_vector + np.float32(0.01), "sig_2") # Slight noise
    
    # Gamma disagrees (Random vector)
    engine.submit_proposal(task_id, "node_gamma", np.random.randn(16).astype(np.float32), "sig_3")
    
    # Consensus should trigger and select Alpha/Beta's truth, ignoring Gamma
