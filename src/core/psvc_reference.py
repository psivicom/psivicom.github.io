# src/core/psvc_reference.py
import hashlib
import json
from pathlib import Path

PRECISION_FLOAT16 = 4  # Example constant

def content_hash(data: str) -> str:
    """Generates a SHA256 hash of string data."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def write_file(path: Path, content: str):
    """Writes content to file, ensuring parent dirs exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def read_file(path: Path) -> str:
    """Reads file content safely."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding='utf-8')

def validate_file(path: Path) -> bool:
    """Basic validation that a .psvc file exists and is readable."""
    return path.exists() and path.is_file()
