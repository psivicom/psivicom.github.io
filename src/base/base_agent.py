# src/base/base_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Layer 0 Foundation: BaseAgent with receipt chaining and safe capability resolution.
"""

import uuid
import hashlib
import time
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class AgentLayer(Enum):
    FOUNDATION = 0
    INGESTION = 1
    VALIDATION = 2
    SYNTHESIS = 3
    ORCHESTRATION = 4
    GOVERNANCE = 5


@dataclass(frozen=True)
class AgentReceipt:
    agent_id: str
    layer: str
    operation: str
    payload_hash: str
    timestamp: float = field(default_factory=time.time)
    rfc1001_compliant: bool = True
    parent_receipt_hash: Optional[str] = None

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
    LAYER: AgentLayer = AgentLayer.FOUNDATION

    def __init__(self, name: str, capabilities: Optional[List[str]] = None):
        self.agent_id = f"{name}-{uuid.uuid4().hex[:8]}"
        self.name = name
        self.capabilities = capabilities or []
        self.memory: Dict[str, Any] = {}
        self.children: List['BaseAgent'] = []
        self.last_receipt: Optional[AgentReceipt] = None

    def seal(self, operation: str, payload: Any, parent_hash: Optional[str] = None) -> AgentReceipt:
        payload_str = json.dumps(payload, sort_keys=True) if isinstance(payload, dict) else str(payload)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()

        self.last_receipt = AgentReceipt(
            agent_id=self.agent_id,
            layer=self.LAYER.name,
            operation=operation,
            payload_hash=payload_hash,
            parent_receipt_hash=parent_hash or (
                self.last_receipt.payload_hash if self.last_receipt else None
            )
        )
        return self.last_receipt

    def resolve_capability(self, capability: str, *args, **kwargs) -> Any:
        """
        Attempt to resolve a capability. If missing, safely attempt LLM generation.
        Falls back gracefully if automation layer is unavailable.
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
            self.seal(f"llm_spawn_{capability}", {"agent": new_agent.agent_id})
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
