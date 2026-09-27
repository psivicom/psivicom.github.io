# src/core/psvc_containers.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Pico Service Container (PSVC) Implementation.
Handles serialization of PyTorch tensors into binary containers with headers.
"""

import struct
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import numpy as np
import torch

@dataclass
class PSVCHeader:
    """Metadata header for a Pico Service Container."""
    version: str = "1.0"
    content_type: str = "generic_tensor"
    operation: str = "unknown"
    agent_id: str = "system"
    layer: str = "VALIDATION"
    shard_id: str = ""
    checksum: str = ""
    
    def to_bytes(self) -> bytes:
        # Serialize header to JSON then encode UTF-8
        return json.dumps({
            "version": self.version,
            "content_type": self.content_type,
            "operation": self.operation,
            "agent_id": self.agent_id,
            "layer": self.layer,
            "shard_id": self.shard_id,
            "checksum": self.checksum
        }).encode('utf-8')

    @staticmethod
    def from_bytes(data: bytes) -> 'PSVCHeader':
        obj = json.loads(data.decode('utf-8'))
        return PSVCHeader(**obj)

@dataclass
class PicoContainer:
    """A container holding metadata and raw tensor data."""
    header: PSVCHeader
    payload: bytes  # Raw byte representation of the tensor
    
    def get_checksum(self) -> str:
        return hashlib.sha256(self.payload).hexdigest()[:16]

def build_psvc_from_tensor(
    tensor: torch.Tensor, 
    operation: str, 
    agent_id: str, 
    layer: str, 
    shard_id: str,
    content_type: str = "vram_vector"
) -> PicoContainer:
    """Converts a PyTorch tensor into a PicoContainer."""
    # Detach from graph and move to CPU for serialization safety
    cpu_tensor = tensor.detach().cpu()
    
    # Convert to numpy for standard byte serialization
    np_array = cpu_tensor.numpy()
    raw_bytes = np_array.tobytes()
    
    header = PSVCHeader(
        content_type=content_type,
        operation=operation,
        agent_id=agent_id,
        layer=layer,
        shard_id=shard_id
    )
    # Calculate checksum based on payload
    header.checksum = hashlib.sha256(raw_bytes).hexdigest()[:16]
    
    return PicoContainer(header=header, payload=raw_bytes)

def serialize_psvc(container: PicoContainer) -> bytes:
    """Serializes a PicoContainer into a single byte stream."""
    header_bytes = container.header.to_bytes()
    # Format: [4 bytes header length][header json][payload bytes]
    header_len = len(header_bytes)
    packed_header_len = struct.pack('>I', header_len)
    
    return packed_header_len + header_bytes + container.payload

def deserialize_psvc(data: bytes) -> PicoContainer:
    """Deserializes a byte stream back into a PicoContainer."""
    if len(data) < 4:
        raise ValueError("Data too short to contain header length")
        
    header_len = struct.unpack('>I', data[:4])[0]
    
    if len(data) < 4 + header_len:
        raise ValueError("Data truncated during header read")
        
    header_bytes = data[4 : 4 + header_len]
    payload = data[4 + header_len :]
    
    header = PSVCHeader.from_bytes(header_bytes)
    
    # Verify integrity
    calculated_check = hashlib.sha256(payload).hexdigest()[:16]
    if header.checksum != calculated_check:
        raise ValueError(f"Checksum mismatch! Expected {header.checksum}, got {calculated_check}")
        
    return PicoContainer(header=header, payload=payload)

def reconstruct_torch_tensor(container: PicoContainer) -> torch.Tensor:
    """Reconstructs a PyTorch tensor from a PicoContainer."""
    # We assume float32 for now as per typical ML usage. 
    # In production, store dtype in header.
    dtype = torch.float32
    
    # Create a view of the bytes as a numpy array
    # Note: This assumes little-endian architecture compatibility or explicit handling
    arr = np.frombuffer(container.payload, dtype=np.float32)
    
    # Reshape? The current implementation flattens. 
    # To support shapes, we'd need shape info in the header.
    # For this MVP, we return the flat tensor.
    return torch.from_numpy(arr.copy()).to(dtype=dtype)
