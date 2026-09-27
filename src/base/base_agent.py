# src/base/base_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Base Agent Framework for PSIVI.

Defines the contract every agent must fulfill:
- identity
- capability declaration
- cryptographic sealing / audit trail
- result persistence
- Zulu millisecond time law

This version fixes the PilotAgent contract by exposing:
- self.creation_time
- self.created_at
- self.started_at

All timestamps are formatted as:
YYYY-MM-DDTHH:MM:SS.sssZ
"""

import json
import hashlib
import time
from enum import Enum
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone

import numpy as np


def _zulu_ms(dt: Optional[datetime] = None) -> str:
    """
    Returns a strict Zulu UTC timestamp with milliseconds:
    2026-09-27T06:11:07.538Z
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    ms = dt.microsecond // 1000
    return f"{dt.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}Z"


def _zulu_compact(dt: Optional[datetime] = None) -> str:
    """
    Returns a filesystem-safe compact Zulu timestamp:
    20260927T061107538Z
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    ms = dt.microsecond // 1000
    return f"{dt.strftime('%Y%m%dT%H%M%S')}{ms:03d}Z"


class AgentLayer(Enum):
    """
    Cognitive Layers of the PSIVI Hive Mind.

    INGESTION:    Raw data intake (Pilot, Instruction agents).
    VALIDATION:   Memory integrity & peer evaluation (Intelligence agent).
    OPTIMIZATION: Weight adaptation & evolution (Neuroplasticity agent).
    METAPHYSICS:  Observation of invisible forces / dark matter (Void Observer).
                  This layer measures what is NOT happening but IS influencing.
    """
    INGESTION = "ingestion"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    METAPHYSICS = "metaphysics"


class BaseAgent:
    """
    Abstract base for all PSIVI agents.

    Provides:
    - deterministic-ish unique agent identity
    - capability registry
    - cryptographic seal chain
    - result persistence
    - Zulu millisecond timestamps
    """

    LAYER: AgentLayer = AgentLayer.INGESTION  # Override in subclasses

    def __init__(self, name: str, capabilities: Optional[List[str]] = None):
        self.name = name
        self.capabilities = capabilities or []
        self.agent_id = self._generate_agent_id()

        now = datetime.now(timezone.utc)

        # Canonical creation timestamp.
        # PilotAgent and other organs may expect this exact attribute.
        self.creation_time = _zulu_ms(now)

        # Safe aliases for backward/forward compatibility.
        self.created_at = self.creation_time
        self.started_at = self.creation_time
        self.start_time = self.creation_time

        self._seals: List[Dict[str, Any]] = []

        # Ensure required directories exist.
        Path("reports").mkdir(parents=True, exist_ok=True)
        Path("reports/seals").mkdir(parents=True, exist_ok=True)
        Path("data").mkdir(parents=True, exist_ok=True)

    def _generate_agent_id(self) -> str:
        """
        Creates a deterministic-ish unique ID based on:
        name + layer + nanosecond timestamp.
        """
        seed = f"{self.name}:{self.LAYER.value}:{time.time_ns()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]

    def seal(
        self,
        operation: str,
        payload: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        """
        Cryptographically seals an operation into the audit trail.

        Supports both styles:

            self.seal("event", {"key": "value"})

        and extended metadata:

            self.seal("event", {"key": "value"}, fragility=True, score=0.8)

        Extra keyword arguments are merged into payload.
        Each seal is immutable and timestamped in Zulu UTC milliseconds.
        """
        sealed_payload: Dict[str, Any] = dict(payload) if payload is not None else {}

        if kwargs:
            sealed_payload.update(kwargs)

        seal_record = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "layer": self.LAYER.value,
            "operation": operation,
            "payload": sealed_payload,
            "sealed_at": _zulu_ms(),
            "epoch": time.time()
        }

        # Compute integrity hash over the canonical record.
        canonical = json.dumps(seal_record, sort_keys=True, default=str)
        seal_record["integrity_hash"] = hashlib.sha256(canonical.encode()).hexdigest()

        self._seals.append(seal_record)

    def seal_result(
        self,
        vector: Any,
        output_dir: Path,
        meta: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Persists the agent's final result vector + metadata to disk.

        Returns the path to the written result file.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = _zulu_compact()
        filename = f"{self.name}_{timestamp}.json"
        filepath = output_dir / filename

        # Safely normalize vector-like output.
        try:
            if vector is None:
                arr = np.zeros(0, dtype=np.float32)
            else:
                arr = np.asarray(vector)

            # If object dtype sneaks in, try to coerce to float32.
            if arr.dtype == object:
                arr = arr.astype(np.float32)

        except Exception:
            arr = np.zeros(0, dtype=np.float32)

        vector_shape = list(arr.shape)
        vector_dtype = str(arr.dtype)

        try:
            vector_preview = arr.tobytes().hex()[:256] if arr.size else ""
        except Exception:
            vector_preview = ""

        result_payload = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "layer": self.LAYER.value,
            "creation_time": self.creation_time,
            "started_at": self.started_at,
            "completed_at": _zulu_ms(),
            "capabilities": self.capabilities,
            "result_vector_shape": vector_shape,
            "result_vector_dtype": vector_dtype,
            "result_vector_bytes_hex_preview": vector_preview,
            "metadata": meta or {},
            "seals_count": len(self._seals),
            "seals_preview": self._seals[-5:] if self._seals else []
        }

        filepath.write_text(
            json.dumps(result_payload, indent=2, default=str),
            encoding="utf-8"
        )

        # Append full seal chain to dedicated audit file.
        seals_path = Path("reports/seals") / f"{self.name}_seals.jsonl"
        with open(seals_path, "a", encoding="utf-8") as f:
            for seal in self._seals:
                f.write(json.dumps(seal, default=str) + "\n")

        return filepath

    def get_identity(self) -> Dict[str, Any]:
        """
        Returns the agent's public identity card.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "layer": self.LAYER.value,
            "capabilities": self.capabilities,
            "creation_time": self.creation_time,
            "started_at": self.started_at
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"id={self.agent_id} "
            f"layer={self.LAYER.value} "
            f"created={self.creation_time}>"
        )
