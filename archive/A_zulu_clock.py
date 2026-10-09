# src/core/zulu_clock.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Zulu Clock — the single temporal authority for the PSIVI AETHER Mesh.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def get_zulu_timestamp_ms() -> str:
    """
    Return the current UTC time as a Zulu-formatted string to millisecond precision.
    Format: YYYY-MM-DDTHH:MM:SS.sssZ
    """
    try:
        now = datetime.now(timezone.utc)
        return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    except Exception as e:
        logger.error(f"Failed to generate Zulu timestamp: {e}")
        raise RuntimeError("Cannot produce Zulu timestamp.")
