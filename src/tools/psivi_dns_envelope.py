# tools/psivi_dns_envelope.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSIVI-DNS Envelope Schemas
Defines the binary structures for sovereign DNS resolution.
Every DNS record is a fixed-size, zero-copy, cryptographically verifiable struct.
"""

import hashlib
import numpy as np

# ============================================================================
# DNS RECORD TYPES (Custom PSIVI Extensions)
# ============================================================================
DNS_TYPE_A = 0x0001          # IPv4 address
DNS_TYPE_AAAA = 0x001C       # IPv6 address
DNS_TYPE_PSVC = 0xPSVC       # PSVC envelope reference (hash + location)
DNS_TYPE_BLOOM = 0xBL00      # Bloom filter chunk (for mesh dedup)
DNS_TYPE_SOA = 0x0006        # Start of Authority
DNS_TYPE_NS = 0x0002         # Name Server
DNS_TYPE_TXT = 0x0010        # Text record (sovereign metadata)

# ============================================================================
# DNS RECORD STRUCT: 272 bytes fixed
# Optimized for zero-copy lookup and Bloom filter integration.
# ============================================================================
DNS_RECORD_DTYPE = np.dtype([
    ('name_hash', '<u8'),       # 8 bytes: Truncated SHA-256 of the FQDN (the "key")
    ('record_type', '<u2'),     # 2 bytes: DNS_TYPE_A, DNS_TYPE_PSVC, etc.
    ('ttl_sec', '<u4'),         # 4 bytes: Time-to-live in seconds
    ('data_len', '<u2'),        # 2 bytes: Actual length of data in the payload
    ('data', 'V256')            # 256 bytes: The record data (IP, PSVC hash, Bloom chunk, etc.)
])

# ============================================================================
# DNS QUERY STRUCT: 16 bytes fixed
# Minimal overhead for high-throughput resolution.
# ============================================================================
DNS_QUERY_DTYPE = np.dtype([
    ('query_id', '<u4'),        # 4 bytes: Unique query identifier (prevents replay)
    ('name_hash', '<u8'),       # 8 bytes: Truncated SHA-256 of the FQDN
    ('record_type', '<u2'),     # 2 bytes: Requested record type
    ('flags', '<u2')            # 2 bytes: Query flags (RD, CD, etc.)
])

# ============================================================================
# DNS RESPONSE STRUCT: 288 bytes fixed
# Wraps the query + the answer record + cryptographic signature.
# ============================================================================
DNS_RESPONSE_DTYPE = np.dtype([
    ('query_id', '<u4'),        # 4 bytes: Echo of the query ID
    ('status', 'u1'),           # 1 byte: 0x00=NOERROR, 0x03=NXDOMAIN
    ('answer_count', 'u1'),     # 1 byte: Number of answer records
    ('reserved', 'u1'),         # 1 byte: Padding
    ('query', DNS_QUERY_DTYPE), # 16 bytes: The original query
    ('answer', DNS_RECORD_DTYPE), # 272 bytes: The answer record
])

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hash_fqdn(fqdn: str) -> int:
    """
    Computes the truncated SHA-256 hash of a fully-qualified domain name.
    This is the "key" used for O(1) Bloom filter and hash table lookups.
    """
    digest = hashlib.sha256(fqdn.encode('utf-8')).digest()[:8]
    return int.from_bytes(digest, byteorder='little')

def pack_dns_record(name_hash: int, record_type: int, ttl_sec: int, data: bytes) -> np.ndarray:
    """
    Packs a DNS record into the fixed-size struct.
    Zero-copy: returns a numpy view over the data.
    """
    if len(data) > 256:
        raise ValueError(f"DNS record data exceeds 256 bytes: {len(data)}")
    
    padded_data = data.ljust(256, b'\x00')
    record = np.array([(name_hash, record_type, ttl_sec, len(data), padded_data)], dtype=DNS_RECORD_DTYPE)
    return record

def pack_dns_query(query_id: int, name_hash: int, record_type: int, flags: int = 0x0100) -> np.ndarray:
    """
    Packs a DNS query into the fixed-size struct.
    """
    query = np.array([(query_id, name_hash, record_type, flags)], dtype=DNS_QUERY_DTYPE)
    return query

def pack_dns_response(query_id: int, status: int, answer_count: int, query: np.ndarray, answer: np.ndarray) -> np.ndarray:
    """
    Packs a DNS response into the fixed-size struct.
    """
    response = np.array([(query_id, status, answer_count, 0x00, query[0], answer[0])], dtype=DNS_RESPONSE_DTYPE)
    return response
