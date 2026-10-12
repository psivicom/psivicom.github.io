# src/core/binary_psvc_reader.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Binary PSVC Reader - Sovereign Verification Layer.
Parses the unified v2 binary PSVC format produced by the Zig engines,
verifies Ed25519 signatures, and extracts raw vector payloads losslessly.
"""

import os
import struct
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

import numpy as np
import nacl.signing
import nacl.exceptions

logger = logging.getLogger("BINARY_PSVC_READER")

PSVC_MAGIC = b'PSVC'
HEADER_SIZE = 20  # 4 + 1 + 1 + 2 + 4 + 8
SIGNATURE_SIZE = 64  # Ed25519 signature

@dataclass
class BinaryPSVC:
    """Represents a parsed, verified binary PSVC container."""
    version: int
    precision_bits: int
    payload_length: int
    timestamp_epoch_ms: int
    payload: bytes
    signature: Optional[bytes]
    is_signed: bool
    source_path: Path

    def to_numpy(self, dtype: Optional[np.dtype] = None) -> np.ndarray:
        """Converts the raw payload to a numpy array with zero-copy semantics."""
        if dtype is None:
            dtype_map = {
                4: np.uint8,   # Packed 4-bit stored as uint8 (2 values per byte)
                8: np.uint8,
                16: np.float16,
                32: np.float32,
                64: np.float64,
                128: np.float128 if hasattr(np, 'float128') else np.longdouble,
            }
            dtype = dtype_map.get(self.precision_bits, np.float32)
        
        return np.frombuffer(self.payload, dtype=dtype)


class BinaryPSVCReader:
    """Reads and verifies unified v2 binary PSVC containers."""
    
    def __init__(self, verify_key: Optional[nacl.signing.VerifyKey] = None):
        """
        Initializes the reader with an optional Ed25519 verify key.
        If provided, all PSVCs will be cryptographically verified.
        """
        self.verify_key = verify_key
        if verify_key:
            logger.info("🔐 BinaryPSVCReader initialized with sovereign verification key.")
        else:
            logger.warning("⚠️ BinaryPSVCReader initialized WITHOUT verification key. Signatures will not be checked.")

    @classmethod
    def from_env_seed(cls) -> 'BinaryPSVCReader':
        """Creates a reader using the WENDY_PRIVATE_KEY_SEED environment variable."""
        seed_hex = os.environ.get("WENDY_PRIVATE_KEY_SEED")
        if not seed_hex:
            logger.warning("⚠️ WENDY_PRIVATE_KEY_SEED not set. Verification disabled.")
            return cls(verify_key=None)
        
        try:
            signing_key = nacl.signing.SigningKey(bytes.fromhex(seed_hex))
            verify_key = signing_key.verify_key
            logger.info("✅ Sovereign verify key loaded from environment.")
            return cls(verify_key=verify_key)
        except Exception as e:
            logger.error(f"❌ Failed to load sovereign verify key: {e}")
            return cls(verify_key=None)

    def read(self, psvc_path: Path) -> BinaryPSVC:
        """Reads a binary PSVC file from disk."""
        if not psvc_path.exists():
            raise FileNotFoundError(f"PSVC not found: {psvc_path}")
        
        raw_bytes = psvc_path.read_bytes()
        
        if len(raw_bytes) < HEADER_SIZE:
            raise ValueError(f"File too small to be a valid PSVC: {len(raw_bytes)} bytes")
        
        # Parse header
        magic = raw_bytes[0:4]
        if magic != PSVC_MAGIC:
            raise ValueError(f"Invalid PSVC magic: {magic!r}")
        
        version = raw_bytes[4]
        precision_bits = raw_bytes[5]
        # reserved = raw_bytes[6:8]
        payload_length = struct.unpack('<I', raw_bytes[8:12])[0]
        timestamp_epoch_ms = struct.unpack('<Q', raw_bytes[12:20])[0]
        
        # Extract payload
        payload_end = HEADER_SIZE + payload_length
        if len(raw_bytes) < payload_end:
            raise ValueError(f"File truncated: expected {payload_end} bytes, got {len(raw_bytes)}")
        
        payload = raw_bytes[HEADER_SIZE:payload_end]
        
        # Extract optional signature
        signature = None
        is_signed = False
        if len(raw_bytes) > payload_end:
            sig_bytes = raw_bytes[payload_end:payload_end + SIGNATURE_SIZE]
            if len(sig_bytes) == SIGNATURE_SIZE:
                signature = sig_bytes
                is_signed = True
        
        return BinaryPSVC(
            version=version,
            precision_bits=precision_bits,
            payload_length=payload_length,
            timestamp_epoch_ms=timestamp_epoch_ms,
            payload=payload,
            signature=signature,
            is_signed=is_signed,
            source_path=psvc_path
        )

    def verify_and_read(self, psvc_path: Path) -> BinaryPSVC:
        """Reads and cryptographically verifies a binary PSVC."""
        psvc = self.read(psvc_path)
        
        if not psvc.is_signed:
            if self.verify_key:
                raise ValueError(f"PSVC is unsigned but verification is required: {psvc_path}")
            logger.warning(f"⚠️ PSVC is unsigned: {psvc_path}")
            return psvc
        
        if not self.verify_key:
            logger.warning(f"⚠️ PSVC is signed but no verify key available: {psvc_path}")
            return psvc
        
        # Reconstruct the signed message: header bytes + payload
        raw_bytes = psvc_path.read_bytes()
        signed_message = raw_bytes[:HEADER_SIZE + psvc.payload_length]
        
        try:
            self.verify_key.verify(signed_message, psvc.signature)
            logger.info(f"✅ PSVC signature verified: {psvc_path.name}")
        except nacl.exceptions.BadSignatureError:
            raise ValueError(f"❌ CRITICAL: Invalid signature on {psvc_path}. Possible tampering detected.")
        
        return psvc

    def extract_vector(self, psvc_path: Path, dtype: Optional[np.dtype] = None) -> np.ndarray:
        """Convenience method: reads, verifies, and extracts the vector in one call."""
        psvc = self.verify_and_read(psvc_path)
        return psvc.to_numpy(dtype=dtype)

    def get_metadata(self, psvc_path: Path) -> Dict[str, Any]:
        """Returns metadata about a PSVC without loading the full payload."""
        psvc = self.read(psvc_path)
        return {
            "path": str(psvc.source_path),
            "version": psvc.version,
            "precision_bits": psvc.precision_bits,
            "payload_length": psvc.payload_length,
            "timestamp_epoch_ms": psvc.timestamp_epoch_ms,
            "is_signed": psvc.is_signed,
            "file_size": psvc.source_path.stat().st_size,
        }
