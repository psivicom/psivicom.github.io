# src/core/psvc_containers.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Pico Service Container (PSVC) Implementation v3.
Pure NumPy implementation for lightweight portability.
No Torch dependency.
"""

import struct
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import numpy as np

@dataclass
class PSVCHeader:
    """Metadata header for a Pico Service Container."""
    version: str = "3.0"
    content_type: str = "generic_tensor" 
    operation: str = "unknown"
    agent_id: str = "system"
    sender_id: str = ""      
    layer: str = "VALIDATION"
    shard_id: str = ""
    checksum: str = ""
    
    def to_bytes(self) -> bytes:
        return json.dumps({
            "version": self.version,
            "content_type": self.content_type,
            "operation": self.operation,
            "agent_id": self.agent_id,
            "sender_id": self.sender_id,
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
    payload: bytes  # Raw byte representation of the numpy array
    
    def get_checksum(self) -> str:
        return hashlib.sha256(self.payload).hexdigest()[:16]

def build_psvc_from_array(
    array: np.ndarray, 
    operation: str, 
    agent_id: str, 
    layer: str, 
    shard_id: str,
    content_type: str = "vram_vector",
    sender_id: str = "internal_wendy" 
) -> PicoContainer:
    """Converts a NumPy array into a PicoContainer."""
    # Ensure contiguous memory layout for safe serialization
    if not array.flags['C_CONTIGUOUS']:
        array = np.ascontiguousarray(array)
        
    raw_bytes = array.tobytes()
    
    header = PSVCHeader(
        content_type=content_type,
        operation=operation,
        agent_id=agent_id,
        sender_id=sender_id,
        layer=layer,
        shard_id=shard_id
    )
    header.checksum = hashlib.sha256(raw_bytes).hexdigest()[:16]
    
    return PicoContainer(header=header, payload=raw_bytes)

def serialize_psvc(container: PicoContainer) -> bytes:
    """Serializes a PicoContainer into a single byte stream."""
    header_bytes = container.header.to_bytes()
    header_len = len(header_bytes)
    packed_header_len = struct.pack('>I', header_len)
    return packed_header_len + header_bytes + container.payload

def deserialize_psvc(data: bytes) -> PicoContainer:
    """Deserializes a byte stream back into a PicoContainer."""
    if len(data) < 4:
        raise ValueError("Data too short")
        
    header_len = struct.unpack('>I', data[:4])[0]
    if len(data) < 4 + header_len:
        raise ValueError("Truncated header")
        
    header_bytes = data[4 : 4 + header_len]
    payload = data[4 + header_len :]
    
    header = PSVCHeader.from_bytes(header_bytes)
    
    calculated_check = hashlib.sha256(payload).hexdigest()[:16]
    if header.checksum != calculated_check:
        raise ValueError(f"Checksum mismatch! Expected {header.checksum}, got {calculated_check}")
        
    return PicoContainer(header=header, payload=payload)

def reconstruct_numpy_array(container: PicoContainer) -> np.ndarray:
    """Reconstructs a NumPy array from a PicoContainer."""
    # Assume float32 as per typical ML/vector usage
    arr = np.frombuffer(container.payload, dtype=np.float32)
    return arr.copy()
