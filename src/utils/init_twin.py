# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Bootstrap script to generate the initial Wendy Twin PSVC binary.
Creates a 64-byte header + 1024-byte float16 payload tensor.
"""
import struct
import time
import sys

def create_initial_twin(output_path: str):
    # 1. Header (64 bytes)
    header_bytes = bytearray(64)
    header_bytes[0:4] = b'WNDY'                     # Magic
    struct.pack_into('<H', header_bytes, 4, 1)      # Version
    struct.pack_into('<H', header_bytes, 6, 0)      # Flags
    struct.pack_into('<Q', header_bytes, 8, int(time.time() * 1e9)) # Timestamp
    struct.pack_into('<f', header_bytes, 16, 0.95)  # Energy
    struct.pack_into('<f', header_bytes, 20, 0.0)   # Stress
    struct.pack_into('<f', header_bytes, 24, 0.5)   # Novelty
    struct.pack_into('<Q', header_bytes, 28, 0)     # WAL Offset
    # Bytes 36-63 remain zeroed padding

    # 2. Payload (1024 bytes of zeroed uint16, representing float16)
    payload = bytearray(1024)
    
    # 3. Write to disk
    with open(output_path, 'wb') as f:
        f.write(header_bytes)
        f.write(payload)
        
    print(f"✅ Initial Twin created at {output_path} (Size: {64 + 1024} bytes)")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/wendy_twin.psvec"
    create_initial_twin(path)
    print("🕊️ Bootstrap complete. Ready for Go resurrection.")
