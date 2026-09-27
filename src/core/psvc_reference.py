# src/core/psvc_reference.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSVC Reference Utilities.
Provides core primitives for file I/O, hashing, validation, and precision management
within the Pico Service Container ecosystem.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Union, Dict, Any, Optional

# --- CONSTANTS ---

# Precision Levels for Tensor Storage
PRECISION_FLOAT32 = "float32"
PRECISION_FLOAT16 = "float16"
PRECISION_INT8 = "int8"
DEFAULT_PRECISION = PRECISION_FLOAT32

# Magic Bytes for PSVC Files (Optional, for strict binary checks)
PSVC_MAGIC_BYTES = b'\x89PSVC\r\n\x1a\n'


def content_hash(data: bytes) -> str:
    """
    Generates a SHA-256 hex digest of the given bytes.
    Used for integrity verification of containers.
    """
    return hashlib.sha256(data).hexdigest()


def write_file(path: Union[str, Path], data: Union[bytes, str, Dict, list]) -> bool:
    """
    Safely writes data to a file. Handles directories creation.
    
    Args:
        path: Target file path.
        data: Content to write. If dict/list, serialized as JSON. If str/bytes, written raw.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, (dict, list)):
            # Serialize structured data to JSON string first
            content = json.dumps(data, indent=2)
            p.write_text(content, encoding='utf-8')
        elif isinstance(data, bytes):
            p.write_bytes(data)
        else:
            # Assume string or convertible
            p.write_text(str(data), encoding='utf-8')
            
        return True
    except Exception as e:
        print(f"❌ Write failed for {path}: {e}")
        return False


def read_file(path: Union[str, Path], mode: str = 'text') -> Optional[Union[str, bytes, Dict]]:
    """
    Reads a file and returns its content.
    
    Args:
        path: Source file path.
        mode: 'text', 'binary', or 'json'.
        
    Returns:
        File content or None if error/not found.
    """
    try:
        p = Path(path)
        if not p.exists():
            return None
            
        if mode == 'binary':
            return p.read_bytes()
        elif mode == 'json':
            return json.loads(p.read_text(encoding='utf-8'))
        else:
            return p.read_text(encoding='utf-8')
            
    except Exception as e:
        print(f"❌ Read failed for {path}: {e}")
        return None


def validate_file(file_path: Union[str, Path]) -> bool:
    """
    Validates if a file exists and is readable/non-empty.
    For PSVC files, also attempts basic structural parsing if possible.
    """
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return False
        
    try:
        # Check if empty
        if p.stat().st_size == 0:
            return False
            
        # Try to peek at content if it's likely JSON/Text
        suffix = p.suffix.lower()
        if suffix in ['.json', '.txt', '.md']:
            content = p.read_text(encoding='utf-8')
            if not content.strip():
                return False
                
        return True
    except Exception:
        return False


def get_precision_dtype(precision_str: str):
    """
    Maps string precision identifiers to numpy/torch dtypes if available.
    Falls back to generic types if libraries aren't loaded.
    """
    try:
        import numpy as np
        mapping = {
            PRECISION_FLOAT32: np.float32,
            PRECISION_FLOAT16: np.float16,
            PRECISION_INT8: np.int8
        }
        return mapping.get(precision_str, np.float32)
    except ImportError:
        # Fallback if numpy isn't present (shouldn't happen in this repo context)
        return float 


def calculate_checksum(filepath: Union[str, Path]) -> Optional[str]:
    """
    Calculates MD5 checksum for quick integrity checks of large files.
    """
    try:
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None
