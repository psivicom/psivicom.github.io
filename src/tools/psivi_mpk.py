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

# Satellite EO/SAR Telemetry Record: 12 bytes fixed
# Optimized for downlinking radar backscatter, GPS ephemeris, and thermal status
SATELLITE_TELEMETRY_DTYPE = np.dtype([
    ('epoch_ms', '<i8'),       # 8 bytes: Zulu timestamp (absolute, not delta, for orbital precision)
    ('backscatter_db', '<i2'), # 2 bytes: SAR backscatter in centi-decibels (e.g., -2500 = -25.00 dB)
    ('gps_alt_m', '<u1'),      # 1 byte: Altitude tier (quantized, e.g., 0-255 representing 400-800km)
    ('thermal_status', 'u1')   # 1 byte: Bitmask for panel temp, battery health, radiation flags
])

# Secure Uplink Command Record: 264 bytes fixed
# Optimized for ground-to-space/drone command and control.
# Includes replay-attack protection (cmd_id) and inline parameters.
UPLINK_COMMAND_DTYPE = np.dtype([
    ('cmd_id', '<u4'),         # 4 bytes: Monotonic command ID (prevents replay attacks)
    ('target_sys', 'u1'),      # 1 byte: 0x01=Payload, 0x02=ADCS, 0x03=Comms, 0x04=Power
    ('action_code', 'u1'),     # 1 byte: e.g., 0x10=Reboot, 0x20=Update Bloom Filter, 0x30=Point
    ('payload_len', '<u2'),    # 2 bytes: Actual length of data in the payload block
    ('payload', 'V256')        # 256 bytes: Inline parameters (e.g., quaternions, config bytes)
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
        """Encodes a hive telemetry stream into a zero-copy-ready MPK envelope."""
        n = len(timestamps_ms)
        if n == 0:
            return self._build_envelope(b'')
        
        if not (len(weights_g) == len(temps_c) == len(flags) == n):
            raise ValueError(f"Array length mismatch: {len(timestamps_ms)}, {len(weights_g)}, {len(temps_c)}, {len(flags)}")

        ts_delta = np.diff(timestamps_ms, prepend=timestamps_ms[0]).astype('<i2')
        weights = np.asarray(weights_g, dtype='<i2')
        temps = np.asarray(temps_c, dtype='<i2')
        flags_arr = np.asarray(flags, dtype='u1')

        structured = np.rec.fromarrays(
            [ts_delta, weights, temps, flags_arr],
            dtype=HIVE_RECORD_DTYPE
        )

        sort_idx = np.argsort(structured['ts_delta'])
        sorted_structured = structured[sort_idx]

        raw_bytes = sorted_structured.tobytes()
        compressed = self.cctx.compress(raw_bytes)

        return self._build_envelope(compressed)

    def encode_tensor_chunk(self, chunk_id: int, layer_idx: int, precision: int, data: bytes) -> bytes:
        """Encodes a CERN-compatible tensor chunk."""
        if len(data) > 1024:
            raise ValueError(f"Tensor data exceeds 1024 bytes: {len(data)}")
        
        padded_data = data.ljust(1024, b'\x00')
        record = np.array([(chunk_id, layer_idx, precision, padded_data)], dtype=TENSOR_CHUNK_DTYPE)
        raw_bytes = record.tobytes()
        compressed = self.cctx.compress(raw_bytes)
        
        return self._build_envelope(compressed)

    def encode_vector_embedding(self, doc_bytes: bytes, timestamp_ms: int, embeddings: np.ndarray) -> bytes:
        """Encodes an arXiv-compatible quantized vector embedding."""
        if len(embeddings) != 384:
            raise ValueError(f"Embedding must be 384 dimensions, got {len(embeddings)}")
        
        doc_hash = int.from_bytes(compute_sha256_truncated(doc_bytes, 8), byteorder='little')
        quantized = np.clip(np.round(embeddings), -128, 127).astype('i1')
        
        record = np.array([(doc_hash, timestamp_ms, 384, quantized)], dtype=VECTOR_EMBEDDING_DTYPE)
        raw_bytes = record.tobytes()
        compressed = self.cctx.compress(raw_bytes)
        
        return self._build_envelope(compressed)

    def encode_satellite_telemetry(
        self,
        epoch_ms: np.ndarray,
        backscatter_db: np.ndarray,
        gps_alt_m: np.ndarray,
        thermal_status: np.ndarray
    ) -> bytes:
        """Encodes satellite EO/SAR telemetry into a zero-copy-ready MPK envelope."""
        n = len(epoch_ms)
        if n == 0:
            return self._build_envelope(b'')
            
        if not (len(backscatter_db) == len(gps_alt_m) == len(thermal_status) == n):
            raise ValueError("Array length mismatch in satellite telemetry")

        epochs = np.asarray(epoch_ms, dtype='<i8')
        backscatter = np.asarray(backscatter_db, dtype='<i2')
        altitudes = np.asarray(gps_alt_m, dtype='u1')
        thermals = np.asarray(thermal_status, dtype='u1')

        structured = np.rec.fromarrays(
            [epochs, backscatter, altitudes, thermals],
            dtype=SATELLITE_TELEMETRY_DTYPE
        )

        sort_idx = np.argsort(structured['epoch_ms'])
        sorted_structured = structured[sort_idx]

        raw_bytes = sorted_structured.tobytes()
        compressed = self.cctx.compress(raw_bytes)

        return self._build_envelope(compressed)

    def encode_uplink_command(self, cmd_id: int, target_sys: int, action_code: int, payload: bytes) -> bytes:
        """Encodes a secure, zero-copy uplink command for satellites/drones."""
        if len(payload) > 256:
            raise ValueError(f"Uplink payload exceeds 256 bytes: {len(payload)}")
        
        padded_payload = payload.ljust(256, b'\x00')
        record = np.array([(cmd_id, target_sys, action_code, len(payload), padded_payload)], dtype=UPLINK_COMMAND_DTYPE)
        
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
        
        Raises:
            ValueError: If envelope is malformed, CRC fails, or magic/version mismatch
        """
        if len(envelope) < HEADER_SIZE + CRC32_SIZE:
            raise ValueError(f"Envelope too small: {len(envelope)} < {HEADER_SIZE + CRC32_SIZE}")

        magic, version, flags, payload_size = struct.unpack(HEADER_FORMAT, envelope[:HEADER_SIZE])
        if magic != MAGIC:
            raise ValueError(f"Invalid magic: {magic!r} (expected {MAGIC!r})")
        if version != VERSION:
            raise ValueError(f"Unsupported version: {version} (expected {VERSION})")

        payload = envelope[HEADER_SIZE : HEADER_SIZE + payload_size]
        expected_crc = struct.unpack('<I', envelope[-CRC32_SIZE:])[0]
        if compute_crc32(payload) != expected_crc:
            raise ValueError("CRC32 mismatch: data corruption detected")

        raw_bytes = self.dctx.decompress(payload)
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
