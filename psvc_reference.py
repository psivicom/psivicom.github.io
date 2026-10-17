# psvc_reference.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import struct
import zlib
import hashlib
import numpy as np
from pathlib import Path

MAGIC = b'PSVI'
VERSION = 1
HEADER_SIZE = 14
PRECISION_FLOAT16 = 1

def content_hash(vector):
    vec = vector.astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return hashlib.sha256(vec.tobytes()).hexdigest()[:12]

def seal(vector, precision=PRECISION_FLOAT16):
    vec = vector.astype(np.float32)
    dim = len(vec)
    if precision == PRECISION_FLOAT16:
        payload = vec.astype(np.float16).tobytes()
    else:
        payload = vec.tobytes()
    compressed = zlib.compress(payload, level=9)
    header = MAGIC + struct.pack('B', VERSION) + struct.pack('B', precision) + struct.pack('I', dim) + struct.pack('I', len(compressed))
    return header + compressed

def open_container(data):
    if len(data) < HEADER_SIZE:
        raise ValueError("File too small")
    if data[:4] != MAGIC:
        raise ValueError("Invalid magic bytes")
    precision = data[5]
    dim = struct.unpack('I', data[6:10])[0]
    payload_size = struct.unpack('I', data[10:14])[0]
    compressed = data[HEADER_SIZE:HEADER_SIZE + payload_size]
    payload = zlib.decompress(compressed)
    if precision == PRECISION_FLOAT16:
        vector = np.frombuffer(payload, dtype=np.float16).astype(np.float32)
    else:
        vector = np.frombuffer(payload, dtype=np.float32)
    return vector

def write_file(vector, output_path, precision=PRECISION_FLOAT16):
    data = seal(vector, precision)
    Path(output_path).write_bytes(data)

def read_file(file_path):
    data = Path(file_path).read_bytes()
    return open_container(data)

def validate_file(file_path):
    data = Path(file_path).read_bytes()
    if len(data) < HEADER_SIZE:
        raise ValueError("File too small")
    if data[:4] != MAGIC:
        raise ValueError("Invalid magic bytes")
    return True

# RFC 1001 Section 14.1 First-Level Encoding / Decoding implementation
def encode_text(text: str) -> str:
    """
    RFC 1001 Section 14.1 First-Level Encoding.
    Maps each 8-bit byte into two 4-bit nibbles biased by ASCII 'A' (0x41).
    """
    if isinstance(text, str):
        data = text.encode('utf-8')
    else:
        data = bytes(text)
        
    encoded_chars = []
    for byte in data:
        high_nibble = ((byte >> 4) & 0x0F) + 0x41
        low_nibble = (byte & 0x0F) + 0x41
        encoded_chars.append(chr(high_nibble))
        encoded_chars.append(chr(low_nibble))
        
    return "".join(encoded_chars)


def decode_text(encoded: str) -> str:
    """
    RFC 1001 Section 14.1 First-Level Decoding.
    Reverses the two-nibble ASCII 'A' bias back into the original text.
    """
    if len(encoded) % 2 != 0:
        raise ValueError("Invalid RFC 1001 encoded string length; must be even.")
        
    decoded_bytes = bytearray()
    for i in range(0, len(encoded), 2):
        high_nibble = (ord(encoded[i]) - 0x41) & 0x0F
        low_nibble = (ord(encoded[i + 1]) - 0x41) & 0x0F
        decoded_bytes.append((high_nibble << 4) | low_nibble)
        
    return decoded_bytes.decode('utf-8', errors='replace')


# Optional alias if other tests expect bytes input
def encode_bytes(data: bytes) -> str:
    return encode_text(data)

def decode_bytes(encoded: str) -> bytes:
    if len(encoded) % 2 != 0:
        raise ValueError("Invalid RFC 1001 encoded string length.")
    raw = bytearray()
    for i in range(0, len(encoded), 2):
        high = (ord(encoded[i]) - 0x41) & 0x0F
        low = (ord(encoded[i + 1]) - 0x41) & 0x0F
        raw.append((high << 4) | low)
    return bytes(raw)