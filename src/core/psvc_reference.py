# src/core/psvc_reference.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSVC Reference Validator.
Currently a stub implementation to prevent ImportErrors.
Future versions will implement strict schema validation for Pico Service Containers.
"""

from pathlib import Path
import json

def validate_file(file_path: str) -> bool:
    """
    Validates if a given file path exists and contains valid JSON structure 
    expected for a PSVC container.
    
    Args:
        file_path: String path to the .json or .psvc file.
        
    Returns:
        True if valid, False otherwise.
    """
    try:
        p = Path(file_path)
        if not p.exists():
            return False
        
        # Basic structural check for now
        content = p.read_text()
        data = json.loads(content)
        
        # Check for minimal required keys if applicable
        # For now, we just ensure it parses as JSON
        return isinstance(data, dict) or isinstance(data, list)
        
    except Exception:
        return False

def get_schema_version() -> str:
    """Returns the current PSVC schema version."""
    return "1.0.0-alpha"
