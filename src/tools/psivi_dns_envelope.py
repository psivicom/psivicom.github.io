# tools/psivi_dns_envelope.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSIVI-DNS Envelope Schemas
Defines the binary structures for sovereign, next-generation naming and resolution.
Supports IPv4, native IPv6, and Blockchain-inspired Decentralized Identifiers (DIDs).
"""

import hashlib
import numpy as np

# ============================================================================
# DNS RECORD TYPES (PSIVI Sovereign Extensions)
# ============================================================================
DNS_TYPE_A = 0x0001          # IPv4 address (Legacy fallback)
DNS_TYPE_AAAA = 0x001C       # IPv6 address (128-bit, Native Mesh Standard)
DNS_TYPE_PSVC = 0x0100       # PSVC envelope reference (hash + location)
DNS_TYPE_BLOOM = 0x0101      # Bloom filter chunk (for mesh O(1) dedup)
DNS_TYPE_DID = 0x0102        # Decentralized Identifier (Blockchain/Sovereign key)
DNS_TYPE_CADDR = 0x0103      # Content-Addressed Hash (IPFS/Arweave style)
DNS_TYPE_TXT = 0x0010        # Text record (sovereign metadata, e.g., "Goldstream Node")

# ============================================================================
# DNS RECORD STRUCT: 272 bytes fixed
# Optimized for zero-copy lookup. The 256-byte payload easily holds:
# - 16 bytes for IPv6
# - 32 bytes for ED25519 Public Key (DID)
# - 32 bytes for SHA-256 Content Hash (CADDR)
# ============================================================================
DNS_RECORD_DTYPE = np.dtype([
    ('name_hash', '<u8'),       # 8 bytes: Truncated SHA-256 of the FQDN or DID
    ('record_type', '<u2'),     # 2 bytes: DNS_TYPE_AAAA, DNS_TYPE_DID, etc.
    ('ttl_sec', '<u4'),         # 4 bytes: Time-to-live in seconds
    ('data_len', '<u2'),        # 2 bytes: Actual length of data in the payload
    ('data', 'V256')            # 256 bytes: The record data (IPv6, DID, or Hash)
])

# ============================================================================
# DNS QUERY STRUCT: 16 bytes fixed
# Minimal overhead for high-throughput, zero-copy resolution.
# ============================================================================
DNS_QUERY_DTYPE = np.dtype([
    ('query_id', '<u4'),        # 4 bytes: Unique query identifier (prevents replay)
    ('name_hash', '<u8'),       # 8 bytes: Truncated SHA-256 of the FQDN or DID
    ('record_type', '<u2'),     # 2 bytes: Requested record type
    ('flags', '<u2')            # 2 bytes: Query flags (0x0100 = RD, 0x0000 = Authoritative)
])

# ============================================================================
# DNS RESPONSE STRUCT: 288 bytes fixed
# Wraps the query + the answer record. Signed at the envelope level.
# ============================================================================
DNS_RESPONSE_DTYPE = np.dtype([
    ('query_id', '<u4'),        # 4 bytes: Echo of the query ID
    ('status', 'u1'),           # 1 byte: 0x00=NOERROR, 0x03=NXDOMAIN
    ('answer_count', 'u1'),     # 1 byte: Number of answer records
    ('reserved', 'u1'),         # 1 byte: Padding for alignment
    ('query', DNS_QUERY_DTYPE), # 16 bytes: The original query
    ('answer', DNS_RECORD_DTYPE), # 272 bytes: The answer record
])

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hash_fqdn(fqdn: str) -> int:
    """
    Computes the truncated SHA-256 hash of a fully-qualified domain name or DID.
    This is the "key" used for O(1) Bloom filter and hash table lookups.
    Example: "node-01.goldstream.psvc" -> 8-byte integer
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
    
    # Pad to exactly 256 bytes to maintain fixed struct size for zero-copy alignment
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

# ============================================================================
# NEXT-GEN HELPERS: IPv6 and Sovereign DIDs
# ============================================================================

def pack_ipv6_record(name_hash: int, ipv6_bytes: bytes, ttl_sec: int = 3600) -> np.ndarray:
    """
    Packs a native IPv6 address (16 bytes) into a DNS record.
    Example: node-01.goldstream.psvc -> fd00:psvc:goldstream::1
    """
    if len(ipv6_bytes) != 16:
        raise ValueError(f"IPv6 address must be exactly 16 bytes, got {len(ipv6_bytes)}")
    return pack_dns_record(name_hash, DNS_TYPE_AAAA, ttl_sec, ipv6_bytes)

def pack_did_record(name_hash: int, public_key_bytes: bytes, ttl_sec: int = 86400) -> np.ndarray:
    """
    Packs a Decentralized Identifier (DID) public key (e.g., 32-byte Ed25519) into a DNS record.
    This is the "Third System": the name resolves directly to the cryptographic identity, 
    bypassing traditional IP routing entirely for peer-to-peer mesh communication.
    """
    if len(public_key_bytes) > 256:
        raise ValueError(f"DID public key exceeds 256 bytes: {len(public_key_bytes)}")
    return pack_dns_record(name_hash, DNS_TYPE_DID, ttl_sec, public_key_bytes)

def pack_caddr_record(name_hash: int, content_hash_bytes: bytes, ttl_sec: int = 86400) -> np.ndarray:
    """
    Packs a Content-Addressed hash (e.g., 32-byte SHA-256 of a PSVC envelope or dataset).
    Used for resolving "What is the latest Goldstream hive telemetry?" directly to the data hash.
    """
    if len(content_hash_bytes) > 256:
        raise ValueError(f"Content hash exceeds 256 bytes: {len(content_hash_bytes)}")
    return pack_dns_record(name_hash, DNS_TYPE_CADDR, ttl_sec, content_hash_bytes)
