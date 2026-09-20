# src/core/vector_math.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

import hashlib
import time
from dataclasses import dataclass
from typing import Tuple, Dict, Any
import torch
import torch.nn.functional as F

@dataclass(frozen=True)
class MathState:
    """Immutable mathematical state of a tensor operation."""
    operation: str
    input_hash: str
    output_hash: str
    vram_address: int
    tensor_shape: tuple
    flops_estimate: int
    timestamp: float

def _hash_tensor(t: torch.Tensor) -> str:
    """Pure function to hash tensor contents."""
    return hashlib.sha256(t.cpu().detach().numpy().tobytes()).hexdigest()

def embed_tokens(token_ids: torch.Tensor, embedding_matrix: torch.Tensor) -> Tuple[torch.Tensor, MathState]:
    """
    Pure functional embedding: Token IDs -> High-dimensional vectors in VRAM.
    """
    vectors = embedding_matrix[token_ids]
    
    state = MathState(
        operation="embedding_lookup",
        input_hash=_hash_tensor(token_ids),
        output_hash=_hash_tensor(vectors),
        vram_address=vectors.data_ptr(),
        tensor_shape=tuple(vectors.shape),
        flops_estimate=token_ids.numel() * embedding_matrix.shape[1],
        timestamp=time.time()
    )
    return vectors, state

def compute_attention(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, head_dim: int) -> Tuple[torch.Tensor, MathState]:
    """
    Pure functional attention mechanism: Q × K^T × V.
    """
    scores = torch.matmul(q, k.transpose(-2, -1)) / (head_dim ** 0.5)
    weights = F.softmax(scores, dim=-1)
    context = torch.matmul(weights, v)
    
    state = MathState(
        operation="multi_head_attention",
        input_hash=f"{_hash_tensor(q)}|{_hash_tensor(k)}|{_hash_tensor(v)}",
        output_hash=_hash_tensor(context),
        vram_address=context.data_ptr(),
        tensor_shape=tuple(context.shape),
        flops_estimate=4 * q.shape[0] * q.shape[1] * q.shape[2] * q.shape[3],
        timestamp=time.time()
    )
    return context, state
