# src/core/zulu_clock.py
"""
PSIVI AETHER Mesh - Zulu Time Engine
Protocol: RFC 1001
Time Standard: ISO 8601 Zulu (millisecond precision)

The Law: Timestamps are Zulu (UTC) with millisecond precision.
Format: YYYY-MM-DDTHH:MM:SS.mmmZ
No exceptions. No local time. No seconds-only formats.
"""

import datetime
import sys


def get_zulu_time_ms():
    """
    Returns the current UTC time in ISO 8601 Zulu format
    with millisecond precision.

    Format: YYYY-MM-DDTHH:MM:SS.mmmZ

    Returns:
        str: The formatted Zulu timestamp string.

    Raises:
        OSError: If the system clock is inaccessible or overflows.
        ValueError: If the datetime object cannot be formatted
                    into the required ISO 8601 structure.
    """
    try:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
    except (AttributeError, OverflowError, OSError) as exc:
        raise OSError("System clock inaccessible: {0}".format(exc))

    try:
        base_format = now_utc.strftime("%Y-%m-%dT%H:%M:%S")
        millis_part = "{0:03d}".format(now_utc.microsecond // 1000)
        return "{0}.{1}Z".format(base_format, millis_part)
    except (ValueError, OverflowError, TypeError) as exc:
        raise ValueError("Timestamp formatting failure: {0}".format(exc))


def print_zulu_time():
    """
    Prints the current UTC Zulu timestamp to stdout.

    Exits with code 1 if the clock cannot be read or formatted,
    writing the failure reason to stderr.
    """
    try:
        print(get_zulu_time_ms())
    except (OSError, ValueError) as exc:
        sys.stderr.write("CRITICAL: Zulu clock failure - {0}\n".format(exc))
        sys.exit(1)


if __name__ == "__main__":
    print_zulu_time()
