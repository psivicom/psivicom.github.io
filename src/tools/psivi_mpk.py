# tools/psivi_mpk.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSIVI Message Pack (MPK) - Zero-Copy Binary Envelope
Implements CCSDS-inspired structured dtypes, quantize->delta->pack->zstd pipeline,
and strict LE-pinned, size-proof, crc32-guarded envelopes.

Enforces the One Law: Never let data change representation more than once per hop.
"""

import struct
import zlib
import hashlib
import numpy as np
import zstandard as zstd
from typing import Tuple, Optional

# ============================================================================
# 1. SCHEMA-IN-BUFFER: Structured Dtypes (CCSDS Style)
# ============================================================================

# Hive logger record: 7 bytes fixed.
HIVE_RECORD_DTYPE = np.dtype([
    ('ts_delta', '<i2'),   # int16: ms since last record (Gorilla-style delta)
    ('weight_g', '<i2'),   # int16: fixed-point grams (scale 1000)
    ('temp_c', '<i2'),     # int16: fixed-point Celsius (scale 100)
    ('flags', 'u1')        # uint8: bitmask for status, errors, keep-masks
])

# CERN / Awkward Array compatible: Fixed-size tensor chunk
TENSOR_CHUNK_DTYPE = np.dtype([
    ('chunk_id', '<u4'),       # 4 bytes: Unique identifier
    ('layer_idx', '<u2'),      # 2 bytes: Neural network layer
    ('precision', 'u1'),       # 1 byte: 0=float32, 1=float16, 2=int8
    ('data', 'V1024')          # 1024 bytes: Variable payload (zstd compressed inside)
])

# arXiv / Vector Search compatible: Quantized Embedding
VECTOR_EMBEDDING_DTYPE = np.dtype([
    ('doc_hash', '<u8'),       # 8 bytes: SHA-256 truncated hash of source
    ('timestamp', '<i8'),      # 8 bytes: Zulu epoch ms
    ('dim_count', '<u2'),      # 2 bytes: e.g., 384
    ('embeddings', 'i1', (384,))  # 384 bytes: int8 quantized vector
])

# ============================================================================
# 2. ENVELOPE GUARDS: LE-pinned, size-proof, crc32
# ============================================================================

MAGIC = b'PSVC'
VERSION = 0x01
HEADER_FORMAT = '<4sBBI'  # LE: magic(4), version(1), flags(1), payload_size(4)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
CRC32_SIZE = 4

def compute_crc32(data: bytes) -> int:
    """
    Fast CRC32 (IEEE 802.3) using zlib's built-in implementation.
    Note: This is CRC32, not CRC32C (Castagnoli). For true CRC32C,
    use a hardware-accelerated library like crc32c or sse4.2 intrinsics.
    """
    return zlib.crc32(data) & 0xFFFFFFFF

def compute_sha256_truncated(data: bytes, length: int = 8) -> bytes:
    """Compute truncated SHA-256 hash for document identification."""
    return hashlib.sha256(data).digest()[:length]

# ============================================================================
# 3. THE PIPELINE: Quantize → Delta → Pack → Zstd
# ============================================================================

class PSIVIEncoder:
    """
    Encodes structured data into zero-copy-ready MPK envelopes.
    Enforces Law #3: Compress AFTER structuring.
    Enforces Law #6: Sort to compress.
    """
    
    def __init__(self, zstd_level: int = 3):
        self.cctx = zstd.ZstdCompressor(level=zstd_level)

    def encode_hive_stream(
        self, 
        timestamps_ms: np.ndarray, 
        weights_g: np.ndarray, 
        temps_c: np.ndarray, 
        flags: np.ndarray
    ) -> bytes:
        """
        Encodes a hive telemetry stream into a zero-copy-ready MPK envelope.
        
        Args:
            timestamps_ms: Monotonic timestamps in milliseconds
            weights_g: Hive weights in grams (will be cast to int16)
            temps_c: Temperatures in centi-degrees Celsius (will be cast to int16)
            flags: Status flags (will be cast to uint8)
            
        Returns:
            Complete PSVC envelope with header, compressed payload, and CRC32
        """
        n = len(timestamps_ms)
        
        # Input validation
        if n == 0:
            return self._build_envelope(b'')
        
        if not (len(weights_g) == len(temps_c) == len(flags) == n):
            raise ValueError(f"Array length mismatch: {len(timestamps_ms)}, {len(weights_g)}, {len(temps_c)}, {len(flags)}")

        # A. Quantize & Delta (Gorilla-style for timestamps)
        ts_delta = np.diff(timestamps_ms, prepend=timestamps_ms[0]).astype('<i2')
        
        # Ensure other arrays match dtype and are contiguous
        weights = np.asarray(weights_g, dtype='<i2')
        temps = np.asarray(temps_c, dtype='<i2')
        flags_arr = np.asarray(flags, dtype='u1')

        # B. Structured Array Assembly (Zero-copy view creation)
        structured = np.rec.fromarrays(
            [ts_delta, weights, temps, flags_arr],
            dtype=HIVE_RECORD_DTYPE
        )

        # C. Sort to Compress (Law #6)
        sort_idx = np.argsort(structured['ts_delta'])
        sorted_structured = structured[sort_idx]

        # D. Zstd Compression (Law #3: Compress AFTER structuring)
        raw_bytes = sorted_structured.tobytes()
        compressed = self.cctx.compress(raw_bytes)

        return self._build_envelope(compressed)

    def encode_tensor_chunk(
        self,
        chunk_id: int,
        layer_idx: int,
        precision: int,
        data: bytes
    ) -> bytes:
        """
        Encodes a CERN-compatible tensor chunk.
        
        Args:
            chunk_id: Unique identifier for this chunk
            layer_idx: Neural network layer index
            precision: 0=float32, 1=float16, 2=int8
            data: Raw tensor data (max 1024 bytes)
        """
        if len(data) > 1024:
            raise ValueError(f"Tensor data exceeds 1024 bytes: {len(data)}")
        
        # Pad to exactly 1024 bytes
        padded_data = data.ljust(1024, b'\x00')
        
        record = np.array([(chunk_id, layer_idx, precision, padded_data)], dtype=TENSOR_CHUNK_DTYPE)
        raw_bytes = record.tobytes()
        compressed = self.cctx.compress(raw_bytes)
        
        return self._build_envelope(compressed)

    def encode_vector_embedding(
        self,
        doc_bytes: bytes,
        timestamp_ms: int,
        embeddings: np.ndarray
    ) -> bytes:
        """
        Encodes an arXiv-compatible quantized vector embedding.
        
        Args:
            doc_bytes: Source document bytes (for hashing)
            timestamp_ms: Zulu epoch milliseconds
            embeddings: 384-dimensional vector (will be quantized to int8)
        """
        if len(embeddings) != 384:
            raise ValueError(f"Embedding must be 384 dimensions, got {len(embeddings)}")
        
        # Compute truncated SHA-256 hash
        doc_hash = int.from_bytes(compute_sha256_truncated(doc_bytes, 8), byteorder='little')
        
        # Quantize to int8 (simple rounding)
        quantized = np.clip(np.round(embeddings), -128, 127).astype('i1')
        
        record = np.array([(doc_hash, timestamp_ms, 384, quantized)], dtype=VECTOR_EMBEDDING_DTYPE)
        raw_bytes = record.tobytes()
        compressed = self.cctx.compress(raw_bytes)
        
        return self._build_envelope(compressed)

    def _build_envelope(self, payload: bytes) -> bytes:
        """Wraps payload with magic, version, flags, size, and crc32."""
        header = struct.pack(HEADER_FORMAT, MAGIC, VERSION, 0x00, len(payload))
        crc = compute_crc32(payload)
        return header + payload + struct.pack('<I', crc)


class PSIVIDecoder:
    """
    Decodes MPK envelopes into zero-copy numpy views.
    Enforces Law #1: Single representation change per hop.
    """
    
    def __init__(self):
        self.dctx = zstd.ZstdDecompressor()

    def decode_to_view(self, envelope: bytes, dtype: np.dtype = HIVE_RECORD_DTYPE) -> np.ndarray:
        """
        Decodes envelope and returns a zero-copy numpy view.
        
        Args:
            envelope: Complete PSVC envelope bytes
            dtype: Expected structured dtype (default: HIVE_RECORD_DTYPE)
            
        Returns:
            Zero-copy numpy structured array view over decompressed bytes
            
        Raises:
            ValueError: If envelope is malformed, CRC fails, or magic/version mismatch
        """
        if len(envelope) < HEADER_SIZE + CRC32_SIZE:
            raise ValueError(f"Envelope too small: {len(envelope)} < {HEADER_SIZE + CRC32_SIZE}")

        # A. Parse Header
        magic, version, flags, payload_size = struct.unpack(HEADER_FORMAT, envelope[:HEADER_SIZE])
        if magic != MAGIC:
            raise ValueError(f"Invalid magic: {magic!r} (expected {MAGIC!r})")
        if version != VERSION:
            raise ValueError(f"Unsupported version: {version} (expected {VERSION})")

        # B. Extract Payload and Verify CRC
        payload = envelope[HEADER_SIZE : HEADER_SIZE + payload_size]
        expected_crc = struct.unpack('<I', envelope[-CRC32_SIZE:])[0]
        if compute_crc32(payload) != expected_crc:
            raise ValueError("CRC32 mismatch: data corruption detected")

        # C. Decompress (Law #1: Single representation change per hop)
        raw_bytes = self.dctx.decompress(payload)

        # D. Zero-Copy View (Law #1: frombuffer)
        # This creates a view over the decompressed bytes without copying.
        return np.frombuffer(raw_bytes, dtype=dtype)

    # Alias for backward compatibility
    decode_to_memmap = decode_to_view


# ============================================================================
# 4. BIT-LEVEL DEDUP & BLOOM (Law #4)
# ============================================================================

class MeshBloomFilter:
    """
    64 KB shared Bloom filter for O(1) 'have I seen this document' checks.
    Uses deterministic hashing for cross-node consistency.
    """
    
    def __init__(self, size_bytes: int = 65536):
        self.size_bits = size_bytes * 8
        self.bitarray = np.zeros(self.size_bits, dtype=np.uint8)
        # Use deterministic hash functions (not Python's hash() which is randomized)
        self.hashes = [
            lambda x: int.from_bytes(hashlib.md5(x).digest()[:4], 'little') % self.size_bits,
            lambda x: int.from_bytes(hashlib.sha1(x).digest()[:4], 'little') % self.size_bits,
            lambda x: int.from_bytes(hashlib.sha256(x).digest()[:4], 'little') % self.size_bits
        ]

    def add(self, item: bytes):
        """Add an item to the Bloom filter."""
        for h in self.hashes:
            self.bitarray[h(item)] = 1

    def check(self, item: bytes) -> bool:
        """Check if an item might be in the Bloom filter (may have false positives)."""
        return all(self.bitarray[h(item)] == 1 for h in self.hashes)

    def to_bytes(self) -> bytes:
        """Serialize Bloom filter to bytes for mesh broadcast."""
        return np.packbits(self.bitarray).tobytes()

    @classmethod
    def from_bytes(cls, data: bytes) -> 'MeshBloomFilter':
        """Deserialize Bloom filter from bytes."""
        bf = cls(size_bytes=len(data))
        unpacked = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        bf.bitarray = unpacked[:bf.size_bits]
        return bf

    def clear(self):
        """Reset the Bloom filter."""
        self.bitarray.fill(0)
