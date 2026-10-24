# ==============================================================================
# FILE: __init__.py
# PATH: psivicom.github.io/src/tools/__init__.py
# DESCRIPTION: Package initializer for the agents module.
#              Required for Python to recognize src/tools/ as a package.
# LICENSE: EUPL-1.2 | COMPLIANCE: NIST SP 800-218, FAIR Open Science
# ==============================================================================
# This file is intentionally minimal.
# It tells Python that src/agents/ is a valid package,
# allowing imports like: from src.agents.satellite_agent import SatelliteAgent
# tools/__init__.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSIVI Tools Package
Zero-copy binary envelopes, structured dtypes, and mesh utilities.
"""

from .psivi_mpk import (
    HIVE_RECORD_DTYPE,
    TENSOR_CHUNK_DTYPE,
    VECTOR_EMBEDDING_DTYPE,
    PSIVIEncoder,
    PSIVIDecoder,
    MeshBloomFilter,
    compute_crc32,
    compute_sha256_truncated
)

__all__ = [
    "HIVE_RECORD_DTYPE",
    "TENSOR_CHUNK_DTYPE",
    "VECTOR_EMBEDDING_DTYPE",
    "PSIVIEncoder",
    "PSIVIDecoder",
    "MeshBloomFilter",
    "compute_crc32",
    "compute_sha256_truncated"
]
