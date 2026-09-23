# test_rfc1001_compliance.py
# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
#
# RFC 1001 Compliance Test Suite
# Verifies that the reference implementation matches the specification.

import struct
import zlib
import numpy as np
from psvc_reference import (
    seal, open_container, encode_text, content_hash, validate_file,
    write_file, read_file, PSVCError,
    MAGIC, VERSION, HEADER_SIZE,
    PRECISION_INT8, PRECISION_FLOAT16, PRECISION_FLOAT32
)

PASS = 0
FAIL = 0

def check(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")

def test_magic_bytes():
    print("\n[TEST] Magic Bytes (RFC 1001 Section 3)")
    vec = np.random.randn(4096).astype(np.float32)
    data = seal(vec, PRECISION_INT8)
    check("First 4 bytes are 'PSVI'", data[:4] == b'PSVI')
    check("Magic is 0x50 0x53 0x56 0x49", data[:4] == bytes([0x50, 0x53, 0x56, 0x49]))

def test_header_structure():
    print("\n[TEST] Header Structure (RFC 1001 Section 3)")
    vec = np.random.randn(4096).astype(np.float32)
    data = seal(vec, PRECISION_INT8)
    check("Header is 14 bytes minimum", len(data) >= 14)
    check("Version byte is 1", data[4] == 1)
    check("Precision byte is 0 (int8)", data[5] == 0)
    dim = struct.unpack('I', data[6:10])[0]
    check("Dimensions field is 4096", dim == 4096)

def test_roundtrip_int8():
    print("\n[TEST] Round-Trip INT8 (RFC 1001 Section 4.1)")
    vec = np.random.randn(4096).astype(np.float32)
    vec /= np.linalg.norm(vec)
    data = seal(vec, PRECISION_INT8)
    recovered = open_container(data)
    check("Recovered shape matches", recovered.shape == vec.shape)
    error = np.max(np.abs(recovered - vec))
    check(f"INT8 error < 0.02 (got {error:.4f})", error < 0.02)

def test_roundtrip_float16():
    print("\n[TEST] Round-Trip Float16 (RFC 1001 Section 4.2)")
    vec = np.random.randn(4096).astype(np.float32)
    vec /= np.linalg.norm(vec)
    data = seal(vec, PRECISION_FLOAT16)
    recovered = open_container(data)
    error = np.max(np.abs(recovered - vec))
    check(f"Float16 error < 0.001 (got {error:.6f})", error < 0.001)

def test_roundtrip_float32():
    print("\n[TEST] Round-Trip Float32 (RFC 1001 Section 4.3)")
    vec = np.random.randn(4096).astype(np.float32)
    data = seal(vec, PRECISION_FLOAT32)
    recovered = open_container(data)
    check("Float32 is lossless", np.array_equal(recovered, vec))

def test_content_addressing():
    print("\n[TEST] Content Addressing (RFC 1001 Section 5.1)")
    vec = np.random.randn(4096).astype(np.float32)
    h1 = content_hash(vec)
    h2 = content_hash(vec)
    check("Hash is deterministic", h1 == h2)
    check("Hash is 12 hex chars", len(h1) == 12)
    check("Hash is lowercase hex", all(c in '0123456789abcdef' for c in h1))

def test_validation_rejects_bad_magic():
    print("\n[TEST] Validation Rejects Bad Magic (RFC 1001 Security)")
    bad_data = b'XXXX' + b'\x00' * 20
    try:
        open_container(bad_data)
        check("Rejects wrong magic bytes", False)
    except PSVCError:
        check("Rejects wrong magic bytes", True)

def test_validation_rejects_truncated():
    print("\n[TEST] Validation Rejects Truncated Files (RFC 1001 Security)")
    vec = np.random.randn(4096).astype(np.float32)
    data = seal(vec, PRECISION_INT8)
    truncated = data[:10]  # Cut off mid-header
    try:
        open_container(truncated)
        check("Rejects truncated file", False)
    except PSVCError:
        check("Rejects truncated file", True)

def test_validation_rejects_size_mismatch():
    print("\n[TEST] Validation Rejects Size Mismatch (RFC 1001 Security)")
    vec = np.random.randn(4096).astype(np.float32)
    data = seal(vec, PRECISION_INT8)
    tampered = data + b'\x00\x00\x00'  # Add extra bytes
    try:
        open_container(tampered)
        check("Rejects size mismatch", False)
    except PSVCError:
        check("Rejects size mismatch", True)

def test_compression():
    print("\n[TEST] Compression Efficiency (RFC 1001 Abstract)")
    vec = np.random.randn(4096).astype(np.float32)
    vec /= np.linalg.norm(vec)
    data = seal(vec, PRECISION_INT8)
    raw_size = 4096 * 4  # float32
    compressed_size = len(data)
    ratio = raw_size / compressed_size
    print(f"  [INFO] Raw: {raw_size}B, Compressed: {compressed_size}B, Ratio: {ratio:.1f}x")
    check("Compression reduces size", compressed_size < raw_size)

def test_text_encoding():
    print("\n[TEST] Text Encoding Determinism")
    v1 = encode_text("Goldstream forage forecast")
    v2 = encode_text("Goldstream forage forecast")
    check("Same text produces same vector", np.array_equal(v1, v2))
    check("Vector is normalized", abs(np.linalg.norm(v1) - 1.0) < 1e-5)
    check("Vector is 4096-dim", len(v1) == 4096)

if __name__ == "__main__":
    print("=== RFC 1001 COMPLIANCE TEST SUITE ===")
    print("Pico Service Container (.psvc) Format v1\n")
    
    test_magic_bytes()
    test_header_structure()
    test_roundtrip_int8()
    test_roundtrip_float16()
    test_roundtrip_float32()
    test_content_addressing()
    test_validation_rejects_bad_magic()
    test_validation_rejects_truncated()
    test_validation_rejects_size_mismatch()
    test_compression()
    test_text_encoding()
    
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    
    if FAIL == 0:
        print("[COMPLIANT] Implementation matches RFC 1001 specification.")
        exit(0)
    else:
        print("[NON-COMPLIANT] Implementation violates RFC 1001.")
        exit(1)
