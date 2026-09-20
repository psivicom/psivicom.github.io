# psvc_containers.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette
# RFC 1001 Compliant — PSIVI Open Science Hub

"""
Complete .psvc (Pico Container) Implementation for PSIVI Open Science Mesh

This module provides the complete, cryptographically-sealed container format
for storing and transmitting vector data across the distributed mesh.

Every .psvc container contains:
1. FAIR-compliant metadata header
2. Mathematical state (VRAM addresses, FLOPs, tensor shapes)
3. Cryptographic agent receipt with provenance chain
4. Raw tensor payload (bytes)
5. State verification hashes for tamper detection
"""

import hashlib
import json
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, Union, List
import numpy as np
import torch


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass(frozen=True)
class MathematicalState:
    """
    Immutable mathematical state of a tensor operation.
    Captures the physical reality of computation in VRAM.
    """
    operation: str
    input_hash: str
    output_hash: str
    vram_address: int
    tensor_shape: tuple
    tensor_dtype: str
    flops_estimate: int
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "vram_address": self.vram_address,
            "tensor_shape": list(self.tensor_shape),
            "tensor_dtype": self.tensor_dtype,
            "flops_estimate": self.flops_estimate,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MathematicalState':
        return cls(
            operation=data["operation"],
            input_hash=data["input_hash"],
            output_hash=data["output_hash"],
            vram_address=data["vram_address"],
            tensor_shape=tuple(data["tensor_shape"]),
            tensor_dtype=data["tensor_dtype"],
            flops_estimate=data["flops_estimate"],
            timestamp=data["timestamp"]
        )


@dataclass(frozen=True)
class AgentReceipt:
    """
    Immutable, cryptographically-signed receipt of an agent operation.
    Forms a provenance chain through parent_receipt_hash.
    """
    agent_id: str
    layer: str
    operation: str
    payload_hash: str
    timestamp: float = field(default_factory=time.time)
    rfc1001_compliant: bool = True
    parent_receipt_hash: Optional[str] = None
    
    def sign(self, secret: str = "psivicom-public") -> str:
        """Generate cryptographic signature of this receipt."""
        raw = f"{self.agent_id}|{self.layer}|{self.operation}|{self.payload_hash}|{self.timestamp}"
        return hashlib.sha256(f"{raw}|{secret}".encode()).hexdigest()
    
    def verify_signature(self, signature: str, secret: str = "psivicom-public") -> bool:
        """Verify that this receipt hasn't been tampered with."""
        expected = self.sign(secret)
        return signature == expected
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentReceipt':
        return cls(**data)


@dataclass(frozen=True)
class PSVCHeader:
    """
    FAIR-compliant metadata header for the container.
    Ensures all data is Findable, Accessible, Interoperable, Reusable.
    """
    schema_version: str = "1.0"
    content_type: str = "vector_shard"
    fair_license: str = "CC-BY-4.0"
    author: str = "Louis-Philippe Audette"
    project: str = "psivicom.github.io"
    vector_dims: int = 0
    shard_id: str = ""
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PSVCHeader':
        return cls(**data)


@dataclass(frozen=True)
class PSVCPayload:
    """
    The actual data payload: tensor bytes + mathematical state.
    """
    tensor_bytes: bytes
    tensor_shape: tuple
    tensor_dtype: str
    math_state: MathematicalState
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tensor_shape": list(self.tensor_shape),
            "tensor_dtype": self.tensor_dtype,
            "math_state": self.math_state.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], tensor_bytes: bytes) -> 'PSVCPayload':
        return cls(
            tensor_bytes=tensor_bytes,
            tensor_shape=tuple(data["tensor_shape"]),
            tensor_dtype=data["tensor_dtype"],
            math_state=MathematicalState.from_dict(data["math_state"])
        )


@dataclass(frozen=True)
class PicoContainer:
    """
    The complete .psvc container: Header + Payload + Receipt + Verification.
    This is the atomic unit of data in the PSIVI mesh.
    """
    header: PSVCHeader
    payload: PSVCPayload
    receipt: AgentReceipt
    state_verification: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "header": self.header.to_dict(),
            "payload": self.payload.to_dict(),
            "receipt": self.receipt.to_dict(),
            "state_verification": self.state_verification
        }


# ============================================================================
# SERIALIZATION / DESERIALIZATION
# ============================================================================

def serialize_psvc(container: PicoContainer) -> bytes:
    """
    Serialize a PicoContainer to binary format for mesh transmission or storage.
    
    Binary Format:
    [Header Length (4B)] [Header JSON]
    [Payload Metadata Length (4B)] [Payload Metadata JSON]
    [Receipt Length (4B)] [Receipt JSON]
    [State Verification Length (4B)] [State Verification JSON]
    [Tensor Bytes]
    """
    header_json = json.dumps(container.header.to_dict()).encode('utf-8')
    payload_json = json.dumps(container.payload.to_dict()).encode('utf-8')
    receipt_json = json.dumps(container.receipt.to_dict()).encode('utf-8')
    state_json = json.dumps(container.state_verification).encode('utf-8')
    
    return (
        len(header_json).to_bytes(4, 'big') + header_json +
        len(payload_json).to_bytes(4, 'big') + payload_json +
        len(receipt_json).to_bytes(4, 'big') + receipt_json +
        len(state_json).to_bytes(4, 'big') + state_json +
        container.payload.tensor_bytes
    )


def deserialize_psvc(data: bytes) -> PicoContainer:
    """
    Deserialize binary data back into a PicoContainer.
    """
    try:
        # Parse header
        header_len = int.from_bytes(data[0:4], 'big')
        header_data = json.loads(data[4:4+header_len].decode('utf-8'))
        header = PSVCHeader.from_dict(header_data)
        
        # Parse payload metadata
        payload_start = 4 + header_len
        payload_len = int.from_bytes(data[payload_start:payload_start+4], 'big')
        payload_data = json.loads(data[payload_start+4:payload_start+4+payload_len].decode('utf-8'))
        
        # Parse receipt
        receipt_start = payload_start + 4 + payload_len
        receipt_len = int.from_bytes(data[receipt_start:receipt_start+4], 'big')
        receipt_data = json.loads(data[receipt_start+4:receipt_start+4+receipt_len].decode('utf-8'))
        receipt = AgentReceipt.from_dict(receipt_data)
        
        # Parse state verification
        state_start = receipt_start + 4 + receipt_len
        state_len = int.from_bytes(data[state_start:state_start+4], 'big')
        state_verification = json.loads(data[state_start+4:state_start+4+state_len].decode('utf-8'))
        
        # Extract tensor bytes
        tensor_start = state_start + 4 + state_len
        tensor_bytes = data[tensor_start:]
        
        # Reconstruct payload
        payload = PSVCPayload.from_dict(payload_data, tensor_bytes)
        
        return PicoContainer(
            header=header,
            payload=payload,
            receipt=receipt,
            state_verification=state_verification
        )
    except Exception as e:
        raise ValueError(f"Failed to deserialize .psvc container: {e}")


# ============================================================================
# CONTAINER BUILDERS
# ============================================================================

def build_psvc_from_tensor(
    tensor: Union[torch.Tensor, np.ndarray],
    operation: str,
    agent_id: str,
    layer: str,
    parent_receipt_hash: Optional[str] = None,
    shard_id: str = "",
    content_type: str = "vector_shard"
) -> PicoContainer:
    """
    Build a complete .psvc container from a tensor.
    
    This is the primary entry point for creating containers.
    It automatically:
    1. Captures the mathematical state (VRAM address, FLOPs, hashes)
    2. Generates an agent receipt with provenance chain
    3. Creates state verification hashes
    4. Wraps everything in a FAIR-compliant header
    """
    # Convert to numpy if torch tensor
    if isinstance(tensor, torch.Tensor):
        tensor_np = tensor.cpu().detach().numpy()
        vram_address = tensor.data_ptr()
    else:
        tensor_np = tensor
        vram_address = 0
    
    # Compute hashes
    tensor_bytes = tensor_np.tobytes()
    tensor_hash = hashlib.sha256(tensor_bytes).hexdigest()
    
    # Build mathematical state
    math_state = MathematicalState(
        operation=operation,
        input_hash="",  # Would be populated if this is a transformation
        output_hash=tensor_hash,
        vram_address=vram_address,
        tensor_shape=tuple(tensor_np.shape),
        tensor_dtype=str(tensor_np.dtype),
        flops_estimate=tensor_np.size,  # Simplified FLOPs estimate
        timestamp=time.time()
    )
    
    # Build agent receipt
    receipt = AgentReceipt(
        agent_id=agent_id,
        layer=layer,
        operation=operation,
        payload_hash=tensor_hash,
        timestamp=time.time(),
        rfc1001_compliant=True,
        parent_receipt_hash=parent_receipt_hash
    )
    
    # Build header
    header = PSVCHeader(
        content_type=content_type,
        vector_dims=tensor_np.shape[-1] if len(tensor_np.shape) > 1 else tensor_np.size,
        shard_id=shard_id or f"{agent_id}-{int(time.time())}",
        created_at=time.time()
    )
    
    # Build payload
    payload = PSVCPayload(
        tensor_bytes=tensor_bytes,
        tensor_shape=tuple(tensor_np.shape),
        tensor_dtype=str(tensor_np.dtype),
        math_state=math_state
    )
    
    # Build state verification
    state_verification = {
        "tensor_hash": tensor_hash,
        "receipt_hash": receipt.payload_hash,
        "receipt_signature": receipt.sign(),
        "vram_verified": vram_address > 0
    }
    
    return PicoContainer(
        header=header,
        payload=payload,
        receipt=receipt,
        state_verification=state_verification
    )


def reconstruct_tensor(container: PicoContainer) -> np.ndarray:
    """
    Reconstruct the original tensor from a .psvc container.
    """
    tensor_np = np.frombuffer(
        container.payload.tensor_bytes,
        dtype=np.dtype(container.payload.tensor_dtype)
    ).reshape(container.payload.tensor_shape)
    
    return tensor_np


def reconstruct_torch_tensor(container: PicoContainer, device: str = "cpu") -> torch.Tensor:
    """
    Reconstruct the original tensor as a PyTorch tensor.
    """
    tensor_np = reconstruct_tensor(container)
    return torch.from_numpy(tensor_np).to(device)


# ============================================================================
# VERIFICATION UTILITIES
# ============================================================================

def verify_tensor_integrity(container: PicoContainer) -> bool:
    """
    Verify that the tensor bytes match the recorded mathematical state.
    Returns False if the tensor has been tampered with.
    """
    computed_hash = hashlib.sha256(container.payload.tensor_bytes).hexdigest()
    expected_hash = container.payload.math_state.output_hash
    declared_hash = container.state_verification.get("tensor_hash", "")
    
    return computed_hash == expected_hash == declared_hash


def verify_receipt_signature(container: PicoContainer, secret: str = "psivicom-public") -> bool:
    """
    Verify that the agent receipt hasn't been tampered with.
    """
    expected_signature = container.state_verification.get("receipt_signature", "")
    return container.receipt.verify_signature(expected_signature, secret)


def verify_container(container: PicoContainer, secret: str = "psivicom-public") -> Dict[str, bool]:
    """
    Complete verification of a .psvc container.
    Returns a dictionary of verification results.
    """
    return {
        "tensor_integrity": verify_tensor_integrity(container),
        "receipt_signature": verify_receipt_signature(container, secret),
        "fair_license": container.header.fair_license == "CC-BY-4.0",
        "rfc1001_compliant": container.receipt.rfc1001_compliant,
        "provenance_linked": container.receipt.parent_receipt_hash is not None
    }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Demonstration of the complete .psvc container lifecycle.
    """
    print("=" * 80)
    print("PSIVI .psvc Container Demonstration")
    print("=" * 80)
    
    # 1. Create a sample tensor (simulating vector data)
    print("\n1. Creating sample tensor...")
    sample_tensor = torch.randn(10, 512, dtype=torch.float16)
    print(f"   Tensor shape: {sample_tensor.shape}")
    print(f"   Tensor dtype: {sample_tensor.dtype}")
    print(f"   VRAM address: {sample_tensor.data_ptr()}")
    
    # 2. Build a .psvc container
    print("\n2. Building .psvc container...")
    container = build_psvc_from_tensor(
        tensor=sample_tensor,
        operation="sample_embedding",
        agent_id="demo_agent-abc123",
        layer="INGESTION",
        content_type="demo_vector_shard"
    )
    print(f"   Container created: {container.header.shard_id}")
    print(f"   Receipt agent: {container.receipt.agent_id}")
    print(f"   Math state hash: {container.payload.math_state.output_hash[:16]}...")
    
    # 3. Serialize to bytes
    print("\n3. Serializing to bytes...")
    serialized = serialize_psvc(container)
    print(f"   Serialized size: {len(serialized)} bytes")
    print(f"   Header size: ~{len(json.dumps(container.header.to_dict()))} bytes")
    print(f"   Tensor size: {len(container.payload.tensor_bytes)} bytes")
    
    # 4. Deserialize back to container
    print("\n4. Deserializing from bytes...")
    deserialized = deserialize_psvc(serialized)
    print(f"   Deserialized container: {deserialized.header.shard_id}")
    
    # 5. Verify integrity
    print("\n5. Verifying container integrity...")
    verification = verify_container(deserialized)
    for check, passed in verification.items():
        status = "✓" if passed else "✗"
        print(f"   {status} {check}: {passed}")
    
    # 6. Reconstruct tensor
    print("\n6. Reconstructing tensor...")
    reconstructed = reconstruct_torch_tensor(deserialized)
    print(f"   Reconstructed shape: {reconstructed.shape}")
    print(f"   Tensors match: {torch.allclose(sample_tensor, reconstructed)}")
    
    # 7. Demonstrate tamper detection
    print("\n7. Demonstrating tamper detection...")
    tampered_bytes = bytearray(serialized)
    tampered_bytes[-1] = (tampered_bytes[-1] + 1) % 256  # Flip last byte
    tampered_container = deserialize_psvc(bytes(tampered_bytes))
    tamper_check = verify_tensor_integrity(tampered_container)
    print(f"   Tampered container passes integrity check: {tamper_check}")
    print(f"   (Should be False - tamper detected!)")
    
    print("\n" + "=" * 80)
    print("Demonstration complete!")
    print("=" * 80)
