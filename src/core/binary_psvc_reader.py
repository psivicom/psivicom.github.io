import struct
import os

# ARCHITECTURAL REDESIGN: Lazy import to prevent top-level module crashes
def _get_nacl_signing():
    try:
        import nacl.signing
        return nacl.signing
    except ImportError:
        raise RuntimeError("CRITICAL: PyNaCl is missing. The environment must have 'pynacl' installed.")

class BinaryPSVC:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.header = None
        self.payload = None
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"PSVC file not found: {self.filepath}")
            
        with open(self.filepath, 'rb') as f:
            # Read 20-byte header: Magic(4) + Version(1) + Precision(1) + Reserved(2) + Length(4) + Timestamp(8)
            header_bytes = f.read(20)
            if len(header_bytes) < 20:
                raise ValueError("Invalid PSVC file: Header too short")
                
            magic, version, precision, reserved, length, timestamp = struct.unpack('<4sBBHIQ', header_bytes)
            
            if magic != b'PSVC':
                raise ValueError(f"Invalid PSVC magic: {magic}")
                
            self.header = {
                'version': version,
                'precision': precision,
                'length': length,
                'timestamp': timestamp
            }
            self.payload = f.read(length)

    def verify_signature(self, public_key_hex: str, signature_hex: str) -> bool:
        """Verifies the PSVC payload using NaCl Ed25519."""
        nacl_signing = _get_nacl_signing()
        
        verify_key = nacl_signing.VerifyKey(bytes.fromhex(public_key_hex))
        signature = bytes.fromhex(signature_hex)
        
        try:
            verify_key.verify(self.payload, signature)
            return True
        except nacl_signing.exceptions.BadSignatureError:
            return False
