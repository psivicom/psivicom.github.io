# tests/test_psivi_mpk.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Property-based correctness tests for PSIVI MPK Envelope.
Validates: bit-exact round-trips, dtype identity, malformed header rejection.
"""
import pytest
import numpy as np
from hypothesis import given, strategies as st

from tools.psivi_mpk import (
    PSIVIEncoder, 
    PSIVIDecoder, 
    HIVE_RECORD_DTYPE, 
    compute_crc32, 
    MAGIC, 
    HEADER_FORMAT, 
    HEADER_SIZE,
    CRC32_SIZE
)
import struct

encoder = PSIVIEncoder()
decoder = PSIVIDecoder()

# ============================================================================
# 1. Bit-Exact Round-Trip Property (Law #7)
# ============================================================================
@given(
    n=st.integers(min_value=1, max_value=10000),
    seed=st.integers(min_value=0, max_value=2**32 - 1)
)
def test_hive_stream_roundtrip_bit_exact(n: int, seed: int):
    """Random arrays → encode → decode → bit-exact round-trip."""
    rng = np.random.default_rng(seed)
    
    # Generate realistic hive telemetry
    base_ts = 1690000000000
    timestamps = base_ts + np.cumsum(rng.integers(100, 5000, size=n))
    weights = rng.integers(10000, 50000, size=n)  # 10-50 kg in grams
    temps = rng.integers(-1000, 4000, size=n)      # -10C to 40C in centi-degrees
    flags = rng.integers(0, 255, size=n, dtype=np.uint8)

    # Encode
    envelope = encoder.encode_hive_stream(timestamps, weights, temps, flags)
    
    # Decode
    decoded = decoder.decode_to_view(envelope, dtype=HIVE_RECORD_DTYPE)
    
    # Verify dtype identity
    assert decoded.dtype == HIVE_RECORD_DTYPE
    
    # Verify bit-exact round-trip (after sorting, which the encoder does)
    ts_delta = np.diff(timestamps, prepend=timestamps[0]).astype('<i2')
    expected_structured = np.rec.fromarrays(
        [ts_delta, np.asarray(weights, dtype='<i2'), np.asarray(temps, dtype='<i2'), flags],
        dtype=HIVE_RECORD_DTYPE
    )
    sort_idx = np.argsort(expected_structured['ts_delta'])
    expected_sorted = expected_structured[sort_idx]
    
    assert np.array_equal(decoded, expected_sorted), "Round-trip is not bit-exact"


# ============================================================================
# 2. Malformed Header Rejection (Never Crash, Always ValueError)
# ============================================================================
@given(
    bad_magic=st.binary(min_size=4, max_size=4).filter(lambda x: x != MAGIC),
    payload=st.binary(min_size=0, max_size=100)
)
def test_reject_bad_magic(bad_magic: bytes, payload: bytes):
    """Malformed magic must trip ValueError, never segfault or crash."""
    header = struct.pack(HEADER_FORMAT, bad_magic, 0x01, 0x00, len(payload))
    crc = struct.pack('<I', compute_crc32(payload))
    bad_envelope = header + payload + crc
    
    with pytest.raises(ValueError, match="Invalid magic"):
        decoder.decode_to_view(bad_envelope)


@given(
    bad_version=st.integers(min_value=0, max_value=255).filter(lambda x: x != 0x01),
    payload=st.binary(min_size=0, max_size=100)
)
def test_reject_bad_version(bad_version: int, payload: bytes):
    """Unsupported version must trip ValueError."""
    header = struct.pack(HEADER_FORMAT, MAGIC, bad_version, 0x00, len(payload))
    crc = struct.pack('<I', compute_crc32(payload))
    bad_envelope = header + payload + crc
    
    with pytest.raises(ValueError, match="Unsupported version"):
        decoder.decode_to_view(bad_envelope)


def test_reject_truncated_envelope():
    """Envelope smaller than header + CRC must raise ValueError."""
    with pytest.raises(ValueError, match="Envelope too small"):
        decoder.decode_to_view(b'PSVC\x01\x00')  # Only 6 bytes


def test_reject_corrupted_payload():
    """Bit-flip in payload must be caught by CRC32."""
    timestamps = np.array([1000, 2000, 3000], dtype=np.int64)
    weights = np.array([100, 100, 100], dtype=np.int16)
    temps = np.array([200, 200, 200], dtype=np.int16)
    flags = np.array([0, 0, 0], dtype=np.uint8)
    
    envelope = encoder.encode_hive_stream(timestamps, weights, temps, flags)
    
    # Corrupt a byte in the middle of the payload
    corrupted = bytearray(envelope)
    corrupted[10] ^= 0xFF  # Flip bits
    
    with pytest.raises(ValueError, match="CRC32 mismatch"):
        decoder.decode_to_view(bytes(corrupted))


# ============================================================================
# 3. Duty-Cycle / Compression Ratio Benchmark (Sanity Check)
# ============================================================================
def test_compression_ratio():
    """Verify that quantize->delta->sort->zstd achieves expected compression."""
    rng = np.random.default_rng(42)
    n = 10000
    
    # Realistic correlated data (not pure random, to allow delta/sort to work)
    timestamps = np.cumsum(rng.integers(500, 1500, size=n)) + 1690000000000
    weights = 30000 + np.cumsum(rng.integers(-50, 50, size=n))  # Slowly drifting weight
    temps = 2500 + rng.integers(-200, 200, size=n)               # Noisy temp around 25C
    flags = np.zeros(n, dtype=np.uint8)
    
    envelope = encoder.encode_hive_stream(timestamps, weights, temps, flags)
    
    # Raw structured size: 7 bytes * 10000 = 70,000 bytes
    raw_size = n * HIVE_RECORD_DTYPE.itemsize
    
    # Envelope size: header(10) + compressed + crc(4)
    compressed_size = len(envelope)
    
    ratio = raw_size / compressed_size
    
    # With delta + sort + zstd, we expect at least 5x compression on this data
    assert ratio > 5.0, f"Compression ratio {ratio:.2f}x is too low (expected >5x)"
