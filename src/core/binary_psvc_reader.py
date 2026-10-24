import struct
import os

class BinaryPSVCReader:
    """
    Sovereign Binary PSVC Reader.
    Dependency-free, repurposed for the biological AI mesh.
    Compatible with volunteer_worker.py and multi-dimensional headers.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.header = {}
        self.payload = b''
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Sovereign binary not found: {self.filepath}")
            
        with open(self.filepath, 'rb') as f:
            # Read first 4 bytes to check magic and determine header version
            magic = f.read(4)
            f.seek(0)
            
            if magic == b'PSVC':
                # Try new 41-byte multi-dimensional header first
                header_bytes = f.read(41)
                if len(header_bytes) == 41:
                    data = struct.unpack('<4sBBHIQdfffB', header_bytes)
                    self.header = {
                        'magic': data[0].decode('ascii', errors='ignore').strip('\x00'),
                        'version': data[1],
                        'length': data[4],
                        'timestamp': data[5],
                        'entropy': data[6],
                        'vector': (data[7], data[8], data[9]),
                        'actuation': data[10]
                    }
                    self.payload = f.read(self.header['length'])
                else:
                    # Fallback to legacy 28-byte header for backward compatibility
                    f.seek(0)
                    header_bytes = f.read(28)
                    data = struct.unpack('<4sBBHIQd', header_bytes)
                    self.header = {
                        'magic': data[0].decode('ascii', errors='ignore').strip('\x00'),
                        'version': data[1],
                        'length': data[4],
                        'timestamp': data[5],
                        'entropy': data[6]
                    }
                    self.payload = f.read(self.header['length'])
            else:
                raise ValueError(f"Invalid magic signature: {magic}")

    def get_entropy(self) -> float:
        """Returns the Shannon Entropy of the payload."""
        return self.header.get('entropy', 0.0)

    def get_actuation_state(self) -> int:
        """Returns the actuation state (0-3) if available."""
        return self.header.get('actuation', 0)

# Backward compatibility alias for any scripts expecting the old name
BinaryPSVC = BinaryPSVCReader
