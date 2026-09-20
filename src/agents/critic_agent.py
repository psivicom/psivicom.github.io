# src/agents/critic_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Production CriticAgent: Validates .psvc containers before synthesis.

Responsibilities:
- Cryptographic tensor integrity verification
- Receipt chain validation
- FAIR compliance enforcement
- Anomaly detection via statistical analysis
- RFC 1001 audit enforcement
"""

import logging
import time
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field

import numpy as np
import torch

from src.base.base_agent import BaseAgent, AgentLayer
from psvc_containers import (
    PicoContainer,
    deserialize_psvc,
    verify_container,
    verify_tensor_integrity,
    verify_receipt_signature,
    reconstruct_torch_tensor
)
from src.orchestrator.mesh_governor import audit_psvc_container

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CritiqueResult:
    """Immutable result of a container critique."""
    container_id: str
    is_valid: bool
    integrity_passed: bool
    receipt_valid: bool
    fair_compliant: bool
    anomaly_score: float
    anomalies_detected: List[str]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "container_id": self.container_id,
            "is_valid": self.is_valid,
            "integrity_passed": self.integrity_passed,
            "receipt_valid": self.receipt_valid,
            "fair_compliant": self.fair_compliant,
            "anomaly_score": self.anomaly_score,
            "anomalies_detected": self.anomalies_detected,
            "timestamp": self.timestamp
        }


class CriticAgent(BaseAgent):
    """
    Production CriticAgent for validation layer.
    """
    LAYER = AgentLayer.VALIDATION

    def __init__(
        self,
        name: str = "critic_agent",
        anomaly_threshold: float = 0.95,
        require_fair_compliance: bool = True,
        require_receipt_chain: bool = True
    ):
        super().__init__(
            name=name,
            capabilities=[
                "check_tensor_integrity",
                "check_receipt_chain",
                "check_fair_compliance",
                "detect_anomalies",
                "critique_container"
            ]
        )
        self.anomaly_threshold = anomaly_threshold
        self.require_fair_compliance = require_fair_compliance
        self.require_receipt_chain = require_receipt_chain
        self._stats = {
            "total_critiqued": 0,
            "passed": 0,
            "rejected": 0,
            "anomalies_flagged": 0
        }
        logger.info(
            f"CriticAgent initialized: {self.agent_id} | "
            f"anomaly_threshold={anomaly_threshold}"
        )

    def check_tensor_integrity(self, container: PicoContainer) -> Tuple[bool, str]:
        """Verify tensor bytes match the cryptographic hash."""
        try:
            is_valid = verify_tensor_integrity(container)
            if is_valid:
                return True, "tensor_integrity_ok"
            return False, "tensor_hash_mismatch"
        except Exception as e:
            return False, f"integrity_check_error: {e}"

    def check_receipt_chain(self, container: PicoContainer) -> Tuple[bool, str]:
        """Verify receipt signature and chain linkage."""
        try:
            sig_valid = verify_receipt_signature(container)
            if not sig_valid:
                return False, "receipt_signature_invalid"

            if self.require_receipt_chain:
                if container.receipt.parent_receipt_hash is None:
                    # Root operations are allowed
                    if container.receipt.operation.startswith("root"):
                        return True, "root_operation_verified"
                    return False, "missing_parent_receipt"

            return True, "receipt_chain_ok"
        except Exception as e:
            return False, f"receipt_check_error: {e}"

    def check_fair_compliance(self, container: PicoContainer) -> Tuple[bool, str]:
        """Verify FAIR metadata is present and valid."""
        try:
            header = container.header
            if header.fair_license != "CC-BY-4.0":
                return False, f"invalid_license: {header.fair_license}"
            if not header.author:
                return False, "missing_author"
            if not header.project:
                return False, "missing_project"
            return True, "fair_compliant"
        except Exception as e:
            return False, f"fair_check_error: {e}"

    def detect_anomalies(self, container: PicoContainer) -> Tuple[float, List[str]]:
        """
        Statistical anomaly detection on tensor values.
        Returns anomaly score (0-1) and list of detected anomalies.
        """
        anomalies = []
        score = 0.0

        try:
            tensor = reconstruct_torch_tensor(container)
            tensor_np = tensor.cpu().numpy().astype(np.float32)

            # Check 1: NaN or Inf values
            if np.isnan(tensor_np).any():
                anomalies.append("contains_nan")
                score += 0.4
            if np.isinf(tensor_np).any():
                anomalies.append("contains_inf")
                score += 0.4

            # Check 2: All zeros (suspicious)
            if np.all(tensor_np == 0):
                anomalies.append("all_zeros")
                score += 0.3

            # Check 3: Extreme values (outside 6-sigma)
            mean = np.mean(tensor_np)
            std = np.std(tensor_np)
            if std > 0:
                z_scores = np.abs((tensor_np - mean) / std)
                extreme_count = np.sum(z_scores > 6)
                if extreme_count > 0:
                    anomalies.append(f"extreme_values_count={extreme_count}")
                    score += min(0.3, extreme_count / tensor_np.size * 10)

            # Check 4: Unexpected tensor shape
            expected_dims = container.payload.tensor_shape
            actual_dims = tuple(tensor_np.shape)
            if expected_dims != actual_dims:
                anomalies.append(f"shape_mismatch: expected={expected_dims}, actual={actual_dims}")
                score += 0.5

            score = min(1.0, score)
            return score, anomalies

        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return 1.0, [f"anomaly_detection_error: {e}"]

    def critique_container(self, container_bytes: bytes) -> CritiqueResult:
        """
        Full critique pipeline: integrity + receipt + FAIR + anomalies.
        """
        self._stats["total_critiqued"] += 1

        # 1. Deserialize
        try:
            container = deserialize_psvc(container_bytes)
        except Exception as e:
            self._stats["rejected"] += 1
            self.seal("critique_deserialize_failed", {"error": str(e)})
            return CritiqueResult(
                container_id="unknown",
                is_valid=False,
                integrity_passed=False,
                receipt_valid=False,
                fair_compliant=False,
                anomaly_score=1.0,
                anomalies_detected=[f"deserialization_failed: {e}"]
            )

        container_id = container.header.shard_id

        # 2. Governor-level audit (RFC 1001)
        try:
            audit_result = audit_psvc_container(container_bytes)
            if not audit_result.is_valid:
                self._stats["rejected"] += 1
                self.seal("critique_governor_reject", {
                    "container_id": container_id,
                    "failures": audit_result.checks_failed
                })
                return CritiqueResult(
                    container_id=container_id,
                    is_valid=False,
                    integrity_passed=False,
                    receipt_valid=False,
                    fair_compliant=False,
                    anomaly_score=1.0,
                    anomalies_detected=audit_result.checks_failed
                )
        except Exception as e:
            logger.error(f"Governor audit failed: {e}")

        # 3. Individual checks
        integrity_ok, integrity_msg = self.check_tensor_integrity(container)
        receipt_ok, receipt_msg = self.check_receipt_chain(container)
        fair_ok, fair_msg = self.check_fair_compliance(container)
        anomaly_score, anomalies = self.detect_anomalies(container)

        # 4. Decision
        is_valid = (
            integrity_ok and
            receipt_ok and
            (not self.require_fair_compliance or fair_ok) and
            anomaly_score < self.anomaly_threshold
        )

        if is_valid:
            self._stats["passed"] += 1
        else:
            self._stats["rejected"] += 1
            if anomalies:
                self._stats["anomalies_flagged"] += 1

        # 5. Seal the critique
        self.seal("critique_complete", {
            "container_id": container_id,
            "is_valid": is_valid,
            "integrity": integrity_msg,
            "receipt": receipt_msg,
            "fair": fair_msg,
            "anomaly_score": anomaly_score,
            "anomalies": anomalies
        })

        result = CritiqueResult(
            container_id=container_id,
            is_valid=is_valid,
            integrity_passed=integrity_ok,
            receipt_valid=receipt_ok,
            fair_compliant=fair_ok,
            anomaly_score=anomaly_score,
            anomalies_detected=anomalies
        )

        logger.info(
            f"Critique {container_id}: valid={is_valid}, "
            f"anomaly_score={anomaly_score:.3f}, anomalies={len(anomalies)}"
        )

        return result

    def critique_batch(self, container_bytes_list: List[bytes]) -> List[CritiqueResult]:
        """Critique a batch of containers."""
        results = []
        for cb in container_bytes_list:
            results.append(self.critique_container(cb))
        return results

    def get_stats(self) -> Dict[str, int]:
        return self._stats.copy()

    def execute(self, container_bytes: bytes) -> Dict[str, Any]:
        """Main execution entry point."""
        result = self.critique_container(container_bytes)
        return result.to_dict()


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create a valid container to test against
    import torch
    from psvc_containers import build_psvc_from_tensor, serialize_psvc

    tensor = torch.randn(100, dtype=torch.float32)
    container = build_psvc_from_tensor(
        tensor=tensor,
        operation="test_operation",
        agent_id="test_agent",
        layer="INGESTION"
    )
    container_bytes = serialize_psvc(container)

    # Run critic
    critic = CriticAgent()
    result = critic.critique_container(container_bytes)

    print(f"\n=== Critique Result ===")
    print(f"Container ID: {result.container_id}")
    print(f"Valid: {result.is_valid}")
    print(f"Integrity: {result.integrity_passed}")
    print(f"Receipt: {result.receipt_valid}")
    print(f"FAIR: {result.fair_compliant}")
    print(f"Anomaly Score: {result.anomaly_score:.3f}")
    print(f"Anomalies: {result.anomalies_detected}")
    print(f"\nStats: {critic.get_stats()}")
