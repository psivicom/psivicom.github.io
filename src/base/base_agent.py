# src/base/base_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# RFC 1001 Compliant | OSDR-Inspired Provenance

"""
Layer 0 Foundation: BaseAgent with receipt chaining, safe capability resolution,
and OSDR-inspired Fragility/Concordance detection.
"""

import uuid
import hashlib
import time
import json
import logging
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable, Tuple
from enum import Enum
from pathlib import Path

# Ensure root path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.psvc_reference import write_file, content_hash, PRECISION_FLOAT16

logger = logging.getLogger(__name__)


class AgentLayer(Enum):
    """OSDR-Inspired Layer Classification"""
    FOUNDATION = 0      # Base logic
    INGESTION = 1       # Data collection (Forage, Literature)
    VALIDATION = 2      # Error checking (Critic, Governor)
    SYNTHESIS = 3       # Clustering/Merging (Consolidator)
    ORCHESTRATION = 4   # Chaining (Chain Orchestrator)
    GOVERNANCE = 5      # Security/Compliance (Mesh Governor)


@dataclass(frozen=True)
class AgentReceipt:
    """
    Immutable receipt for every agent operation.
    Mirrors OSDR 'provenance' field for FAIR compliance.
    """
    agent_id: str
    layer: str
    operation: str
    payload_hash: str
    timestamp: float = field(default_factory=time.time)
    rfc1001_compliant: bool = True
    parent_receipt_hash: Optional[str] = None
    fragility_detected: bool = False  # OSDR Concept: Contradiction found
    concordance_verified: bool = False # OSDR Concept: Agreement found

    def sign(self, secret: str = "psivicom-public") -> str:
        raw = f"{self.agent_id}|{self.layer}|{self.operation}|{self.payload_hash}|{self.timestamp}"
        return hashlib.sha256(f"{raw}|{secret}".encode()).hexdigest()

    def verify_signature(self, signature: str, secret: str = "psivicom-public") -> bool:
        return self.sign(secret) == signature

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentReceipt':
        return cls(**data)


class BaseAgent:
    """
    The atomic unit of the PSIVI Mesh.
    Every agent inherits from this to ensure uniform logging, security, and evolution.
    """
    LAYER: AgentLayer = AgentLayer.FOUNDATION

    def __init__(self, name: str, capabilities: Optional[List[str]] = None):
        self.agent_id = f"{name}-{uuid.uuid4().hex[:8]}"
        self.name = name
        self.capabilities = capabilities or []
        self.memory: Dict[str, Any] = {}
        self.children: List['BaseAgent'] = []
        self.last_receipt: Optional[AgentReceipt] = None
        self.receipt_chain: List[AgentReceipt] = []

    def seal(self, operation: str, payload: Any, parent_hash: Optional[str] = None, 
             fragility: bool = False, concordance: bool = False) -> AgentReceipt:
        """
        Seals an operation with a cryptographic receipt.
        Flags OSDR-style Fragility (contradiction) or Concordance (agreement).
        """
        payload_str = json.dumps(payload, sort_keys=True) if isinstance(payload, dict) else str(payload)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()

        self.last_receipt = AgentReceipt(
            agent_id=self.agent_id,
            layer=self.LAYER.name,
            operation=operation,
            payload_hash=payload_hash,
            parent_receipt_hash=parent_hash or (
                self.last_receipt.payload_hash if self.last_receipt else None
            ),
            fragility_detected=fragility,
            concordance_verified=concordance
        )
        self.receipt_chain.append(self.last_receipt)
        return self.last_receipt

    def resolve_capability(self, capability: str, *args, **kwargs) -> Any:
        """
        Self-Healing Logic:
        1. Try local method.
        2. If missing, spawn a new agent via LLM (if available).
        3. If LLM unavailable, raise clear error.
        """
        if capability in self.capabilities:
            method = getattr(self, f"execute_{capability}", None)
            if method:
                return method(*args, **kwargs)
            raise AttributeError(f"Capability '{capability}' listed but no execute_{capability} method found")

        # Safe import with fallback
        try:
            from src.automation.llm_agent_generator import LLMAgentGenerator
            generator = LLMAgentGenerator()

            input_schema = {f"arg_{i}": type(a).__name__ for i, a in enumerate(args)}
            input_schema.update({k: type(v).__name__ for k, v in kwargs.items()})

            new_agent_class = generator.generate_agent(
                capability=capability,
                problem_description=f"Cannot solve {capability}",
                input_schema=input_schema,
                output_schema={"result": "Any"},
                parent_agent_id=self.agent_id
            )

            if new_agent_class is None:
                raise ValueError(f"LLM failed to generate agent for: {capability}")

            new_agent = new_agent_class()
            self.children.append(new_agent)
            self.seal(f"llm_spawn_{capability}", {"agent": new_agent.agent_id}, fragility=True) # Spawning implies a gap was found
            return new_agent.execute(*args, **kwargs)

        except ImportError:
            logger.error(f"Automation layer unavailable. Cannot resolve capability: {capability}")
            raise RuntimeError(
                f"Capability '{capability}' not found and automation layer "
                f"(src.automation.llm_agent_generator) is not installed."
            )
        except Exception as e:
            logger.error(f"Capability resolution failed for '{capability}': {e}")
            raise

    def detect_fragility(self, vector_a: np.ndarray, vector_b: np.ndarray, threshold: float = 0.40) -> bool:
        """
        OSDR-Inspired Fragility Detection.
        Returns True if vectors are contradictory (low similarity).
        """
        sim = np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
        is_fragile = sim < threshold
        if is_fragile:
            self.seal("fragility_detected", {"similarity": float(sim), "threshold": threshold}, fragility=True)
        return is_fragile

    def verify_concordance(self, vector_a: np.ndarray, vector_b: np.ndarray, threshold: float = 0.85) -> bool:
        """
        OSDR-Inspired Concordance Verification.
        Returns True if vectors agree (high similarity).
        """
        sim = np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
        is_concordant = sim > threshold
        if is_concordant:
            self.seal("concordance_verified", {"similarity": float(sim), "threshold": threshold}, concordance=True)
        return is_concordant

    def export_receipts_to_psvc(self, output_dir: Path):
        """
        Exports the full receipt chain as an RFC 1001 compliant .psvc container.
        Ensures FAIR reproducibility.
        """
        if not self.receipt_chain:
            logger.warning("No receipts to export.")
            return

        # Serialize chain
        chain_data = [r.to_dict() for r in self.receipt_chain]
        chain_json = json.dumps(chain_data, sort_keys=True)
        
        # Create a dummy vector representing the chain hash (for RFC 1001 compliance)
        chain_hash = hashlib.sha256(chain_json.encode()).hexdigest()
        # Map hex hash to float vector (simple mapping for demonstration)
        vector = np.array([int(c, 16) / 15.0 for c in chain_hash] * 256, dtype=np.float32) # 4096 dims
        vector /= np.linalg.norm(vector)

        output_path = output_dir / f"receipts_{self.agent_id}_{chain_hash[:12]}.psvc"
        write_file(vector, output_path, precision=PRECISION_FLOAT16)
        
        # Write sidecar
        sidecar_path = output_path.with_suffix('.json')
        with open(sidecar_path, 'w') as f:
            json.dump({
                "type": "agent_receipt_chain",
                "agent_id": self.agent_id,
                "layer": self.LAYER.name,
                "receipt_count": len(self.receipt_chain),
                "rfc1001_compliant": True
            }, f, indent=2)
            
        logger.info(f"Exported {len(self.receipt_chain)} receipts to {output_path.name}")
