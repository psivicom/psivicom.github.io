# src/base/base_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import sys
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@dataclass(frozen=True)
class AgentReceipt:
    agent_id: str
    layer: str
    operation: str
    payload_hash: str
    timestamp: float = field(default_factory=time.time)
    rfc1001_compliant: bool = True
    parent_receipt_hash: Optional[str] = None
    fragility_detected: bool = False
    concordance_verified: bool = False

    def sign(self, secret: str = "psivicom-public") -> str:
        raw = f"{self.agent_id}|{self.layer}|{self.operation}|{self.payload_hash}|{self.timestamp}"
        return hashlib.sha256(f"{raw}|{secret}".encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BaseAgent:
    LAYER = "FOUNDATION"

    def __init__(self, name: str, capabilities: Optional[List[str]] = None):
        import uuid
        self.agent_id = f"{name}-{uuid.uuid4().hex[:8]}"
        self.name = name
        self.capabilities = capabilities or []
        self.memory: Dict[str, Any] = {}
        self.children: List['BaseAgent'] = []
        self.last_receipt: Optional[AgentReceipt] = None
        self.receipt_chain: List[AgentReceipt] = []
        self.creation_time = time.time()

    def seal(self, operation: str, payload: Any, parent_hash: Optional[str] = None, fragility: bool = False, concordance: bool = False) -> AgentReceipt:
        payload_str = json.dumps(payload, sort_keys=True) if isinstance(payload, dict) else str(payload)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        self.last_receipt = AgentReceipt(
            agent_id=self.agent_id,
            layer=self.LAYER if isinstance(self.LAYER, str) else self.LAYER.name,
            operation=operation,
            payload_hash=payload_hash,
            parent_receipt_hash=parent_hash or (self.last_receipt.payload_hash if self.last_receipt else None),
            fragility_detected=fragility,
            concordance_verified=concordance
        )
        self.receipt_chain.append(self.last_receipt)
        return self.last_receipt

    def seal_result(self, vector: Any, output_dir: Path, meta: Dict[str, Any] = None):
        from psvc_reference import write_file, content_hash, PRECISION_FLOAT16
        if meta is None:
            meta = {}
        meta.update({
            "agent": self.agent_id,
            "timestamp": time.time(),
            "receipt_count": len(self.receipt_chain)
        })
        chash = content_hash(vector)
        filename = f"{self.agent_id}_{chash}.psvc"
        output_path = output_dir / filename
        write_file(vector, output_path, precision=PRECISION_FLOAT16)
        sidecar_path = output_path.with_suffix('.json')
        with open(sidecar_path, 'w') as f:
            json.dump(meta, f, indent=2)

    def execute(self, input_vector: Any = None) -> Any:
        raise NotImplementedError("Subclasses must implement execute()")
