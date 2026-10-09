# src/core/zulu_clock.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Zulu Clock Utility (Polyglot Bridge)
Generates strict RFC 3339 UTC timestamps with millisecond precision.
Attempts to use the compiled Zig binary (located in src/core/) for ultimate precision, 
falling back to Python if the binary is not available or fails to execute.
"""

import subprocess
from pathlib import Path
from datetime import datetime, timezone

def get_zulu_timestamp_ms() -> str:
    """
    Returns a strictly formatted Zulu timestamp: "YYYY-MM-DDTHH:MM:SS.sssZ"
    """
    # 1. Try the compiled Zig binary (located in the exact same directory as this Python file)
    zig_bin = Path(__file__).parent / "zulu_clock"
    
    if zig_bin.exists():
        try:
            # Execute the Zig binary and capture the output
            result = subprocess.run(
                [str(zig_bin)], 
                capture_output=True, 
                text=True, 
                timeout=1
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            # If the binary fails for any reason (e.g., permissions, architecture mismatch), 
            # fall through to Python seamlessly.
            pass

    # 2. Fallback to native Python implementation
    now = datetime.now(timezone.utc)
    return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

if __name__ == "__main__":
    print(get_zulu_timestamp_ms())
