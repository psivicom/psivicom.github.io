# tools/__init__.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSIVI Tools Package
Zero-copy binary envelopes, structured dtypes, mesh utilities, and sovereign DNS.

This file makes the `tools` directory a valid Python package, allowing clean imports 
like: `from tools.psivi_mpk import PSIVIDecoder`
"""

from .psivi_mpk import (
    HIVE_RECORD_DTYPE,
    TENSOR_CHUNK_DTYPE,
    VECTOR_EMBEDDING_DTYPE,
    SATELLITE_TELEMETRY_DTYPE,
    UPLINK_COMMAND_DTYPE,
    PSIVIEncoder,
    PSIVIDecoder,
    MeshBloomFilter,
    compute_crc32,
    compute_sha256_truncated
)

from .psivi_dns_envelope import (
    DNS_RECORD_DTYPE,
    DNS_QUERY_DTYPE,
    DNS_RESPONSE_DTYPE,
    DNS_TYPE_A,
    DNS_TYPE_PSVC,
    hash_fqdn,
    pack_dns_record,
    pack_dns_query,
    pack_dns_response
)

__all__ = [
    # MPK Schemas
    "HIVE_RECORD_DTYPE",
    "TENSOR_CHUNK_DTYPE",
    "VECTOR_EMBEDDING_DTYPE",
    "SATELLITE_TELEMETRY_DTYPE",
    "UPLINK_COMMAND_DTYPE",
    # MPK Classes & Functions
    "PSIVIEncoder",
    "PSIVIDecoder",
    "MeshBloomFilter",
    "compute_crc32",
    "compute_sha256_truncated",
    # DNS Schemas
    "DNS_RECORD_DTYPE",
    "DNS_QUERY_DTYPE",
    "DNS_RESPONSE_DTYPE",
    "DNS_TYPE_A",
    "DNS_TYPE_PSVC",
    # DNS Functions
    "hash_fqdn",
    "pack_dns_record",
    "pack_dns_query",
    "pack_dns_response"
]
