# src/agents/license_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Production LicenseAgent: Final governance step that stamps FAIR metadata
and validates RFC 1001 compliance on all outputs.

Responsibilities:
- Stamp FAIR metadata on all outputs
- Validate final compliance before release
- Generate FAIR compliance reports
- Seal final governance receipts
"""

import logging
import time
import hashlib
import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from src.base.base_agent import BaseAgent, AgentLayer
from psvc_containers import (
    PicoContainer,
    deserialize_psvc,
    verify_container,
    serialize_psvc
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FAIRMetadata:
    """Immutable FAIR metadata stamp."""
    license: str = "CC-BY-4.0"
    author: str = "Louis-Philippe Audette"
    project: str = "psivicom.github.io"
    findable: bool = True
    accessible: bool = True
    interoperable: bool = True
    reusable: bool = True
    rfc1001_compliant: bool = True
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "psivi_license": self.license,
            "author": self.author,
            "project": self.project,
            "findable": self.findable,
            "accessible": self.accessible,
            "interoperable": self.interoperable,
            "reusable": self.reusable,
            "rfc1001_compliant": self.rfc1001_compliant,
            "timestamp": self.timestamp
        }


@dataclass(frozen=True)
class ComplianceReport:
    """Immutable compliance report."""
    report_id: str
    container_id: str
    fair_valid: bool
    rfc1001_valid: bool
    all_checks_passed: bool
    checks: Dict[str, bool]
    fair_metadata: FAIRMetadata
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "container_id": self.container_id,
            "fair_valid": self.fair_valid,
            "rfc1001_valid": self.rfc1001_valid,
            "all_checks_passed": self.all_checks_passed,
            "checks": self.checks,
            "fair_metadata": self.fair_metadata.to_dict(),
            "timestamp": self.timestamp
        }


class LicenseAgent(BaseAgent):
    """
    Production LicenseAgent for governance layer.
    """
    LAYER = AgentLayer.GOVERNANCE

    def __init__(
        self,
        name: str = "license_agent",
        fair_metadata: Optional[FAIRMetadata] = None,
        require_full_compliance: bool = True
    ):
        super().__init__(
            name=name,
            capabilities=["stamp_fair", "validate_fair", "generate_compliance_report"]
        )
        self.fair_metadata = fair_metadata or FAIRMetadata()
        self.require_full_compliance = require_full_compliance
        self._stats = {
            "total_stamped": 0,
            "total_validated": 0,
            "compliance_passed": 0,
            "compliance_failed": 0
        }
        logger.info(
            f"LicenseAgent initialized: {self.agent_id} | "
            f"license={self.fair_metadata.license}"
        )

    def stamp_fair(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stamp FAIR metadata onto a report dictionary.
        """
        stamped_report = report.copy()
        stamped_report["_psivi_fair_metadata"] = self.fair_metadata.to_dict()

        self._stats["total_stamped"] += 1

        self.seal("stamp_fair", {
            "license": self.fair_metadata.license,
            "author": self.fair_metadata.author,
            "project": self.fair_metadata.project,
            "report_keys": list(report.keys())
        })

        logger.info(f"FAIR metadata stamped on report with {len(report)} keys")
        return stamped_report

    def validate_fair(self, payload: Dict[str, Any]) -> bool:
        """
        Validate that a payload contains required FAIR metadata.
        """
        self._stats["total_validated"] += 1

        if "_psivi_fair_metadata" not in payload:
            logger.warning("Missing _psivi_fair_metadata")
            self.seal("validate_fair_failed", {"reason": "missing_metadata"})
            return False

        meta = payload["_psivi_fair_metadata"]
        required_fields = ["psivi_license", "author", "project"]

        for field_name in required_fields:
            if field_name not in meta or not meta[field_name]:
                logger.warning(f"Missing required FAIR field: {field_name}")
                self.seal("validate_fair_failed", {"reason": f"missing_{field_name}"})
                return False

        # Check FAIR principles
        fair_principles = ["findable", "accessible", "interoperable", "reusable"]
        for principle in fair_principles:
            if not meta.get(principle, False):
                logger.warning(f"FAIR principle not satisfied: {principle}")
                self.seal("validate_fair_failed", {"reason": f"principle_{principle}_false"})
                if self.require_full_compliance:
                    return False

        self.seal("validate_fair_passed", {"metadata_hash": hashlib.sha256(
            json.dumps(meta, sort_keys=True).encode()
        ).hexdigest()})

        logger.info("FAIR validation passed")
        return True

    def validate_container_compliance(self, container_bytes: bytes) -> ComplianceReport:
        """
        Validate a .psvc container for full RFC 1001 + FAIR compliance.
        """
        try:
            container = deserialize_psvc(container_bytes)
        except Exception as e:
            self._stats["compliance_failed"] += 1
            return ComplianceReport(
                report_id=f"compliance-{int(time.time())}",
                container_id="unknown",
                fair_valid=False,
                rfc1001_valid=False,
                all_checks_passed=False,
                checks={"deserialization": False},
                fair_metadata=self.fair_metadata
            )

        container_id = container.header.shard_id

        # Run all verification checks
        verification = verify_container(container)

        # FAIR check
        fair_valid = container.header.fair_license == "CC-BY-4.0" and container.header.author

        # RFC 1001 check
        rfc1001_valid = (
            container.receipt.rfc1001_compliant and
            verification.get("receipt_signature", False) and
            verification.get("tensor_integrity", False)
        )

        all_passed = all(verification.values()) and fair_valid and rfc1001_valid

        if all_passed:
            self._stats["compliance_passed"] += 1
        else:
            self._stats["compliance_failed"] += 1

        report_id = f"compliance-{hashlib.sha256(container_id.encode()).hexdigest()[:12]}"

        report = ComplianceReport(
            report_id=report_id,
            container_id=container_id,
            fair_valid=fair_valid,
            rfc1001_valid=rfc1001_valid,
            all_checks_passed=all_passed,
            checks=verification,
            fair_metadata=self.fair_metadata
        )

        self.seal("validate_container_compliance", {
            "report_id": report_id,
            "container_id": container_id,
            "all_passed": all_passed
        })

        logger.info(
            f"Compliance report {report_id}: "
            f"fair={fair_valid}, rfc1001={rfc1001_valid}, all={all_passed}"
        )

        return report

    def generate_compliance_report(self, container_bytes: bytes) -> Dict[str, Any]:
        """Generate a human-readable compliance report."""
        report = self.validate_container_compliance(container_bytes)
        return report.to_dict()

    def get_stats(self) -> Dict[str, int]:
        return self._stats.copy()

    def execute(self, container_bytes: bytes) -> Dict[str, Any]:
        """Main execution entry point."""
        return self.generate_compliance_report(container_bytes)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create a sample container
    import torch
    from psvc_containers import build_psvc_from_tensor

    tensor = torch.randn(100, dtype=torch.float32)
    container = build_psvc_from_tensor(
        tensor=tensor,
        operation="test_operation",
        agent_id="test_agent",
        layer="INGESTION"
    )
    container_bytes = serialize_psvc(container)

    # Run license agent
    licensor = LicenseAgent()

    # Stamp a report
    report = {"summary": "Test report", "data": [1, 2, 3]}
    stamped = licensor.stamp_fair(report)
    print(f"\n=== Stamped Report ===")
    print(f"License: {stamped['_psivi_fair_metadata']['psivi_license']}")
    print(f"Author: {stamped['_psivi_fair_metadata']['author']}")

    # Validate the stamp
    is_valid = licensor.validate_fair(stamped)
    print(f"\nFAIR validation: {is_valid}")

    # Container compliance
    compliance = licensor.generate_compliance_report(container_bytes)
    print(f"\n=== Compliance Report ===")
    print(f"Report ID: {compliance['report_id']}")
    print(f"FAIR valid: {compliance['fair_valid']}")
    print(f"RFC 1001 valid: {compliance['rfc1001_valid']}")
    print(f"All checks passed: {compliance['all_checks_passed']}")
    print(f"\nStats: {licensor.get_stats()}")
