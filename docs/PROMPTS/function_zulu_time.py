# /docs/PROMPTS/function_zulu_time.py
# EUPL 1.2 , CC-BY-SA 4.0 , 2026 Louis-Philippe Audette

"""
Utility module for retrieving and printing the current UTC time in Zulu format
with millisecond precision.

This implementation adheres to strict error handling protocols for system clock
access and datetime formatting, ensuring robustness in production environments.
"""

import sys
from datetime import datetime, timezone


def print_current_utc_zulu_millis() -> None:
    """
    Print the current Coordinated Universal Time (UTC) in ISO 8601 'Zulu' format
    with millisecond precision.

    The output format is strictly: YYYY-MM-DDTHH:MM:SS.mmmZ
    Example: 2026-09-11T23:09:59.911Z

    Raises:
        OSError: If the system clock cannot be accessed or read due to hardware
                 failure or OS-level permission restrictions.
        ValueError: If the datetime object cannot be formatted into the required
                    string representation (e.g., invalid internal state).
        RuntimeError: If stdout writing fails unexpectedly.
    """
    try:
        # Retrieve current time in UTC with timezone awareness
        now_utc = datetime.now(timezone.utc)
    except OSError as exc:
        raise OSError(
            "Failed to access system clock. Check hardware status or permissions."
        ) from exc

    try:
        # Format manually to ensure exact 'Z' suffix and 3-digit milliseconds
        # strftime('%f') gives microseconds (6 digits), so we slice the first 3
        base_format = now_utc.strftime("%Y-%m-%dT%H:%M:%S.")
        millis_part = now_utc.strftime("%f")[:3]
        zulu_string = f"{base_format}{millis_part}Z"
    except Exception as exc:
        raise ValueError(
            f"Failed to format datetime object '{now_utc}' to Zulu string."
        ) from exc

    try:
        sys.stdout.write(zulu_string + "\n")
        sys.stdout.flush()
    except Exception as exc:
        raise RuntimeError(
            "Unexpected failure while writing to standard output."
        ) from exc


if __name__ == "__main__":
    print_current_utc_zulu_millis()
