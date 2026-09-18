# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
# Affiliation: PSIVI Research
#
# RFC 1001 Reference Implementation
# Pico Service Container (.psvc) Format v1
# This is the canonical, spec-compliant library.

import struct
import zlib
import hashlib
import json
import numpy as np
from pathlib import Path

# RFC 1001 Constants
MAGIC = b'PSVI'
VERSION = 1
HEADER_SIZE = 14
DEFAULT_DIM = 4096

# Precision codes (RFC 1001 Section 4)
PRECISION_INT8 = 0
PRECISION_FLOAT16 = 1
PRECISION_FLOAT32 = 2


class PSVCError(Exception):
    """Raised when a .psvc file violates RFC 1001."""
    pass


def encode_text(text, dim=DEFAULT_DIM):
    """Encode text into a normalized float32 vector using the hashing trick.
    
    RFC 1001 does not mandate an encoding method, but this is the
    reference encoding used by the PSIVI Mesh Pico AI.
    """
    vec = np.zeros(dim, dtype=np.float32)
    text = text.lower().strip()
    for i in range(max(1, len(text) - 2)):
        trigram = text[i:i+3]
        h = int(hashlib.md5(trigram.encode()).hexdigest(), 16)
        idx = h % dim
        sign = 1 if (h % 2) == 0 else -1
        vec[idx] += sign
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def content_hash(vector):
    """Compute the RFC 1001 content address.
    
    SHA-256 of the uncompressed normalized float32 bytes,
    truncated to 12 hexadecimal characters.
    """
    vec = vector.astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return hashlib.sha256(vec.tobytes()).hexdigest()[:12]


def seal(vector, precision=PRECISION_INT8):
    """Seal a vector into RFC 1001 binary format.
    
    Returns the complete .psvc file content as bytes.
    """
    vec = vector.astype(np.float32)
    dim = len(vec)
    
    # Compress payload according to precision profile
    if precision == PRECISION_INT8:
        scale = np.max(np.abs(vec)) / 127.0
        if scale == 0:
            scale = 1.0
        quantized = np.round(vec / scale).astype(np.int8)
        payload = struct.pack('f', scale) + quantized.tobytes()
    elif precision == PRECISION_FLOAT16:
        payload = vec.astype(np.float16).tobytes()
    elif precision == PRECISION_FLOAT32:
        payload = vec.tobytes()
    else:
        raise PSVCError(f"Invalid precision code: {precision}")
    
    # Compress with zlib level 9
    compressed = zlib.compress(payload, level=9)
    
    # Build 14-byte header (Little-Endian)
    header = MAGIC
    header += struct.pack('B', VERSION)
    header += struct.pack('B', precision)
    header += struct.pack('I', dim)
    header += struct.pack('I', len(compressed))
    
    return header + compressed


def open_container(data):
    """Open a .psvc container from bytes.
    
    Validates the header and returns the decompressed float32 vector.
    Raises PSVCError if the file violates RFC 1001.
    """
    if len(data) < HEADER_SIZE:
        raise PSVCError(f"File too small: {len(data)} bytes (minimum {HEADER_SIZE})")
    
    # Validate magic bytes
    if data[:4] != MAGIC:
        raise PSVCError(f"Invalid magic bytes: {data[:4]} (expected {MAGIC})")
    
    # Parse header
    version = data[4]
    precision = data[5]
    dim = struct.unpack('I', data[6:10])[0]
    payload_size = struct.unpack('I', data[10:14])[0]
    
    # Validate version
    if version != VERSION:
        raise PSVCError(f"Unsupported version: {version}")
    
    # Validate total size
    expected_size = HEADER_SIZE + payload_size
    if len(data) != expected_size:
        raise PSVCError(f"Size mismatch: expected {expected_size}, got {len(data)}")
    
    # Decompress payload
    compressed = data[HEADER_SIZE:HEADER_SIZE + payload_size]
    try:
        payload = zlib.decompress(compressed)
    except zlib.error as e:
        raise PSVCError(f"Decompression failed: {e}")
    
    # Decode according to precision profile
    if precision == PRECISION_INT8:
        scale = struct.unpack('f', payload[:4])[0]
        int8_data = np.frombuffer(payload[4:], dtype=np.int8)
        vector = int8_data.astype(np.float32) * scale
    elif precision == PRECISION_FLOAT16:
        vector = np.frombuffer(payload, dtype=np.float16).astype(np.float32)
    elif precision == PRECISION_FLOAT32:
        vector = np.frombuffer(payload, dtype=np.float32).copy()
    else:
        raise PSVCError(f"Invalid precision code: {precision}")
    
    if len(vector) != dim:
        raise PSVCError(f"Dimension mismatch: header says {dim}, payload has {len(vector)}")
    
    return vector


def write_file(vector, output_path, precision=PRECISION_INT8):
    """Write a vector to a .psvc file with content-addressed filename."""
    data = seal(vector, precision)
    Path(output_path).write_bytes(data)
    return output_path


def read_file(file_path):
    """Read and validate a .psvc file from disk."""
    data = Path(file_path).read_bytes()
    return open_container(data)


def validate_file(file_path):
    """Validate a .psvc file without loading the full vector.
    
    Returns a dict with header info, or raises PSVCError.
    """
    data = Path(file_path).read_bytes()
    
    if len(data) < HEADER_SIZE:
        raise PSVCError("File too small")
    if data[:4] != MAGIC:
        raise PSVCError("Invalid magic bytes")
    
    version = data[4]
    precision = data[5]
    dim = struct.unpack('I', data[6:10])[0]
    payload_size = struct.unpack('I', data[10:14])[0]
    
    return {
        "valid": True,
        "version": version,
        "precision": {0: "int8", 1: "float16", 2: "float32"}.get(precision, "unknown"),
        "dimensions": dim,
        "compressed_size": payload_size,
        "total_size": len(data),
        "compression_ratio": round((dim * 4) / max(1, payload_size), 2)
    }


def write_sidecar(vector, meta, output_dir):
    """Write the FAIR-compliant JSON sidecar (RFC 1001 Section 5.2)."""
    chash = content_hash(vector)
    sidecar_path = Path(output_dir) / f"{chash}.json"
    with open(sidecar_path, 'w') as f:
        json.dump(meta, f, indent=2)
    return sidecar_path
