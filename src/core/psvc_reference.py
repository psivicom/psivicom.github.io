"""
psvc_reference.py
Reference Implementation for Pico Service Container (.psvc) Format v1
RFC 1001 Specification
Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
"""

import os
import struct
import zlib
import hashlib
from pathlib import Path
import numpy as np

# Header Constants
MAGIC = b'PSVI'
VERSION = 1
HEADER_SIZE = 14
HEADER_FORMAT = '<4sBBII'
DEFAULT_DIM = 4096

# Precision Flags
PRECISION_INT8 = 0
PRECISION_FLOAT16 = 1
PRECISION_FLOAT32 = 2


class PSVCError(Exception):
    """Base exception for all PSVC container format violations."""
    pass


def content_hash(vec: np.ndarray) -> str:
    """Computes deterministic 12-character lowercase hex hash (RFC 1001 Section 5.1)."""
    if not isinstance(vec, np.ndarray):
        vec = np.array(vec, dtype=np.float32)
    raw = vec.astype(np.float32).tobytes()
    return hashlib.sha256(raw).hexdigest()[:12]


def encode_text(text: str, dim: int = DEFAULT_DIM) -> np.ndarray:
    """Deterministic Text-to-Vector Encoding (RFC 1001)."""
    if not isinstance(text, str):
        text = str(text)

    digest = hashlib.sha256(text.encode('utf-8')).digest()
    seed = struct.unpack('<I', digest[:4])[0]

    rng = np.random.RandomState(seed)
    vec = rng.randn(dim).astype(np.float32)

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm

    return vec


def seal(vec: np.ndarray, precision: int = PRECISION_INT8) -> bytes:
    """Seals a vector into a .psvc binary container (RFC 1001 Section 3 & 4)."""
    if not isinstance(vec, np.ndarray):
        vec = np.array(vec, dtype=np.float32)

    vec = vec.astype(np.float32)
    dim = len(vec)

    if precision == PRECISION_INT8:
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

    compressed_payload = zlib.compress(raw_payload)
    payload_size = len(compressed_payload)

    # Strictly 14-byte packed header
    header = struct.pack(HEADER_FORMAT, MAGIC, VERSION, precision, dim, payload_size)
    return header + compressed_payload


def open_container(data: bytes) -> np.ndarray:
    """Validates and unpacks a .psvc binary container (RFC 1001 Section 3 & Security)."""
    if not isinstance(data, (bytes, bytearray)):
        raise PSVCError("Container data must be bytes.")

    if len(data) < HEADER_SIZE:
        raise PSVCError(f"Truncated container: length {len(data)} < {HEADER_SIZE}")

    magic, version, precision, dim, payload_size = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])

    if magic != MAGIC:
        raise PSVCError(f"Invalid magic: {magic!r}")

    if version != VERSION:
        raise PSVCError(f"Unsupported version: {version}")

    expected_size = HEADER_SIZE + payload_size
    if len(data) != expected_size:
        raise PSVCError(f"Size mismatch: expected {expected_size}, got {len(data)}")

    compressed_payload = data[HEADER_SIZE:expected_size]

    try:
        raw_payload = zlib.decompress(compressed_payload)
    except Exception as e:
        raise PSVCError(f"Corrupted payload: {e}")

    if precision == PRECISION_INT8:
        scale = struct.unpack('<f', raw_payload[:4])[0]
        quantized = np.frombuffer(raw_payload[4:], dtype=np.int8)
        if len(quantized) != dim:
            raise PSVCError(f"Dimension mismatch: expected {dim}, got {len(quantized)}")
        return (quantized.astype(np.float32) / 127.0) * scale

    elif precision == PRECISION_FLOAT16:
        recovered = np.frombuffer(raw_payload, dtype=np.float16)
        if len(recovered) != dim:
            raise PSVCError(f"Dimension mismatch: expected {dim}, got {len(recovered)}")
        return recovered.astype(np.float32)

    elif precision == PRECISION_FLOAT32:
        recovered = np.frombuffer(raw_payload, dtype=np.float32)
        if len(recovered) != dim:
            raise PSVCError(f"Dimension mismatch: expected {dim}, got {len(recovered)}")
        return recovered.copy()

    else:
        raise PSVCError(f"Invalid precision byte: {precision}")


def validate_file(filepath: str) -> dict:
    """
    Validates a .psvc file and returns container metadata dictionary for cmd_inspect.
    """
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < HEADER_SIZE:
        raise PSVCError(f"Truncated container: length {len(data)} < {HEADER_SIZE}")

    magic, version, precision_val, dim, payload_size = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    if magic != MAGIC:
        raise PSVCError(f"Invalid magic: {magic!r}")
    if version != VERSION:
        raise PSVCError(f"Unsupported version: {version}")
    if len(data) != HEADER_SIZE + payload_size:
        raise PSVCError(f"Size mismatch: expected {HEADER_SIZE + payload_size}, got {len(data)}")

    vec = open_container(data)
    precision_names = {PRECISION_INT8: "int8", PRECISION_FLOAT16: "float16", PRECISION_FLOAT32: "float32"}

    return {
        "Magic": magic.decode('ascii', errors='replace'),
        "Version": version,
        "Precision": precision_names.get(precision_val, str(precision_val)),
        "Dimensions": dim,
        "Payload Size": f"{payload_size} bytes",
        "File Size": f"{len(data)} bytes",
        "Content Hash": content_hash(vec)
    }


def write_file(arg1, arg2, precision: int = PRECISION_INT8) -> int:
    """
    Writes a sealed vector to disk.
    Accepts either (filepath, vec, precision) or (vec, filepath, precision).
    """
    if isinstance(arg1, (str, Path)):
        filepath, vec = str(arg1), arg2
    else:
        vec, filepath = arg1, str(arg2)

    data = seal(vec, precision)
    with open(filepath, 'wb') as f:
        f.write(data)
    return len(data)


def read_file(filepath: str) -> np.ndarray:
    """Reads and unpacks a .psvc container from disk."""
    with open(filepath, 'rb') as f:
        data = f.read()
    return open_container(data)