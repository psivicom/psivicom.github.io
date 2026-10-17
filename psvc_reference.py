"""
psvc_reference.py
Reference Implementation for Pico Service Container (.psvc) Format v1
RFC 1001 Specification
Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
"""

import struct
import zlib
import hashlib
import numpy as np

# Header Constants
MAGIC = b'PSVI'
VERSION = 1
HEADER_SIZE = 14

# Precision Flags
PRECISION_INT8 = 0
PRECISION_FLOAT16 = 1
PRECISION_FLOAT32 = 2


class PSVCError(Exception):
    """Base exception for all PSVC container format violations."""
    pass


def content_hash(vec: np.ndarray) -> str:
    """
    Computes deterministic 12-character lowercase hex hash (RFC 1001 Section 5.1).
    """
    if not isinstance(vec, np.ndarray):
        vec = np.array(vec, dtype=np.float32)
    raw = vec.astype(np.float32).tobytes()
    return hashlib.sha256(raw).hexdigest()[:12]


def encode_text(text: str, dim: int = 4096) -> np.ndarray:
    """
    Deterministic Text-to-Vector Encoding (RFC 1001).
    Produces a normalized, deterministic float32 vector of length `dim`.
    """
    if not isinstance(text, str):
        text = str(text)

    # Deterministic seed from text hash
    digest = hashlib.sha256(text.encode('utf-8')).digest()
    seed = struct.unpack('<I', digest[:4])[0]

    rng = np.random.RandomState(seed)
    vec = rng.randn(dim).astype(np.float32)

    # Normalize to unit length
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm

    return vec


def seal(vec: np.ndarray, precision: int = PRECISION_INT8) -> bytes:
    """
    Seals a vector into a .psvc binary container (RFC 1001 Section 3 & 4).
    """
    if not isinstance(vec, np.ndarray):
        vec = np.array(vec, dtype=np.float32)

    vec = vec.astype(np.float32)
    dim = len(vec)

    if precision == PRECISION_INT8:
        # Scale-normalized INT8 quantization
        scale = float(np.max(np.abs(vec)))
        if scale == 0:
            scale = 1.0
        quantized = np.clip(np.round((vec / scale) * 127.0), -128, 127).astype(np.int8)
        raw_payload = struct.pack('<f', scale) + quantized.tobytes()

    elif precision == PRECISION_FLOAT16:
        raw_payload = vec.astype(np.float16).tobytes()

    elif precision == PRECISION_FLOAT32:
        raw_payload = vec.tobytes()

    else:
        raise PSVCError(f"Unsupported precision: {precision}")

    # Compress payload
    compressed_payload = zlib.compress(raw_payload)
    payload_size = len(compressed_payload)

    # Pack 14-byte Header: Magic(4s) + Version(B) + Precision(B) + Dim(I) + PayloadSize(I)
    header = struct.pack('4sBBII', MAGIC, VERSION, precision, dim, payload_size)

    return header + compressed_payload


def open_container(data: bytes) -> np.ndarray:
    """
    Validates and unpacks a .psvc binary container (RFC 1001 Section 3 & Security).
    """
    if not isinstance(data, (bytes, bytearray)):
        raise PSVCError("Container data must be bytes.")

    if len(data) < HEADER_SIZE:
        raise PSVCError(f"Truncated container: length {len(data)} is less than header size {HEADER_SIZE}.")

    magic, version, precision, dim, payload_size = struct.unpack('4sBBII', data[:HEADER_SIZE])

    if magic != MAGIC:
        raise PSVCError(f"Invalid magic bytes: expected {MAGIC!r}, got {magic!r}.")

    if version != VERSION:
        raise PSVCError(f"Unsupported version: {version}.")

    expected_total_size = HEADER_SIZE + payload_size
    if len(data) != expected_total_size:
        raise PSVCError(
            f"Size mismatch: expected {expected_total_size} bytes (header + payload), got {len(data)} bytes."
        )

    compressed_payload = data[HEADER_SIZE:expected_total_size]

    try:
        raw_payload = zlib.decompress(compressed_payload)
    except Exception as e:
        raise PSVCError(f"Corrupted compressed payload: {e}")

    if precision == PRECISION_INT8:
        scale = struct.unpack('<f', raw_payload[:4])[0]
        quantized = np.frombuffer(raw_payload[4:], dtype=np.int8)
        if len(quantized) != dim:
            raise PSVCError(f"Dimension mismatch: expected {dim}, got {len(quantized)}.")
        return (quantized.astype(np.float32) / 127.0) * scale

    elif precision == PRECISION_FLOAT16:
        recovered = np.frombuffer(raw_payload, dtype=np.float16)
        if len(recovered) != dim:
            raise PSVCError(f"Dimension mismatch: expected {dim}, got {len(recovered)}.")
        return recovered.astype(np.float32)

    elif precision == PRECISION_FLOAT32:
        recovered = np.frombuffer(raw_payload, dtype=np.float32)
        if len(recovered) != dim:
            raise PSVCError(f"Dimension mismatch: expected {dim}, got {len(recovered)}.")
        return recovered.copy()

    else:
        raise PSVCError(f"Invalid precision byte: {precision}")


def validate_file(filepath: str) -> bool:
    """
    Validates a .psvc file on disk without corrupting memory state.
    """
    with open(filepath, 'rb') as f:
        data = f.read()
    open_container(data)
    return True


def write_file(filepath: str, vec: np.ndarray, precision: int = PRECISION_INT8) -> int:
    """
    Writes a sealed vector to a .psvc file on disk.
    """
    data = seal(vec, precision)
    with open(filepath, 'wb') as f:
        f.write(data)
    return len(data)


def read_file(filepath: str) -> np.ndarray:
    """
    Reads and unseals a .psvc file from disk.
    """
    with open(filepath, 'rb') as f:
        data = f.read()
    return open_container(data)