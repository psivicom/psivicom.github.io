# src/core/psvc_builder.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Union
from src.core.vector_math import MathState
from src.base.base_agent import AgentReceipt

@dataclass(frozen=True)
class PSVCHeader:
    schema_version: str = "1.0"
    content_type: str = "vector_shard"
    fair_license: str = "CC-BY-4.0"
    author: str = "Louis-Philippe Audette"
    project: str = "psivicom.github.io"

@dataclass(frozen=True)
class PSVCPayload:
    tensor_bytes: bytes
    tensor_shape: tuple
    tensor_dtype: str
    math_state: MathState

@dataclass(frozen=True)
class PicoContainer:
    header: PSVCHeader
    payload: PSVCPayload
    receipt: AgentReceipt
    state_verification: Dict[str, str]

def build_psvc_container(
    tensor: 'torch.Tensor',
    math_state: MathState,
    receipt: AgentReceipt,
    content_type: str = "vector_shard"
) -> PicoContainer:
    """
    Pure function: Constructs an immutable .psvc container from mathematical state.
    """
    header = PSVCHeader(content_type=content_type)
    
    payload = PSVCPayload(
        tensor_bytes=tensor.cpu().detach().numpy().tobytes(),
        tensor_shape=math_state.tensor_shape,
        tensor_dtype=str(tensor.dtype),
        math_state=math_state
    )
    
    verification = {
        "tensor_hash": math_state.output_hash,
        "receipt_hash": receipt.payload_hash,
        "vram_verified": math_state.vram_address > 0
    }
    
    return PicoContainer(
        header=header,
        payload=payload,
        receipt=receipt,
        state_verification=verification
    )

def serialize_psvc(container: PicoContainer) -> bytes:
    """Pure function: Serializes the immutable container to bytes for mesh transmission."""
    h = json.dumps(asdict(container.header)).encode('utf-8')
    p = json.dumps({
        "shape": container.payload.tensor_shape,
        "dtype": container.payload.tensor_dtype,
        "state": asdict(container.payload.math_state)
    }).encode('utf-8')
    r = json.dumps(container.receipt.to_dict()).encode('utf-8')
    s = json.dumps(container.state_verification).encode('utf-8')
    
    return (
        len(h).to_bytes(4, 'big') + h +
        len(p).to_bytes(4, 'big') + p +
        len(r).to_bytes(4, 'big') + r +
        len(s).to_bytes(4, 'big') + s +
        container.payload.tensor_bytes
    )
