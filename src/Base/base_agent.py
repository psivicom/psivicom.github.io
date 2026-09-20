# src/base/base_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

import uuid
import hashlib
import time
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BaseAgent:
    """
    Functional Agent Base: Holds immutable state and composes pure capabilities.
    """
    LAYER: AgentLayer = AgentLayer.FOUNDATION

    def __init__(self, name: str, capabilities: Optional[Dict[str, Callable]] = None):
        self.agent_id = f"{name}-{uuid.uuid4().hex[:8]}"
        self.name = name
        # Capabilities are a dictionary of pure functions
        self.capabilities = capabilities or {}
        self.children: List['BaseAgent'] = []
        self.last_receipt: Optional[AgentReceipt] = None

    def seal(self, operation: str, payload: Any, parent_hash: Optional[str] = None) -> AgentReceipt:
        """Pure function: Generates an immutable receipt for an operation."""
        payload_str = json.dumps(payload, sort_keys=True) if isinstance(payload, dict) else str(payload)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        
        self.last_receipt = AgentReceipt(
            agent_id=self.agent_id,
            layer=self.LAYER.name,
            operation=operation,
            payload_hash=payload_hash,
            parent_receipt_hash=parent_hash or (self.last_receipt.payload_hash if self.last_receipt else None)
        )
        return self.last_receipt

    def execute_capability(self, capability: str, *args, **kwargs) -> Any:
        """
        Functional execution: Attempts to run a capability. 
        If missing, functionally resolves it via the automation pipeline.
        """
        if capability in self.capabilities:
            return self.capabilities[capability](*args, **kwargs)
        
        # Functional resolution: Delegate to the spawner pipeline
        from src.automation.capability_resolver import resolve_missing_capability
        return resolve_missing_capability(self, capability, *args, **kwargs)
