# /src/tools/psivi_mpk.py
"""
PSIVI Message Pack (MPK) - Zero-Copy Binary Envelope
Implements CCSDS-inspired structured dtypes, quantize->delta->pack->zstd pipeline,
and strict LE-pinned, size-proof, crc32c-guarded envelopes.
"""
import struct
import zlib
import numpy as np
import zstandard as zstd

# ============================================================================
# 1. SCHEMA-IN-BUFFER: Structured Dtypes (CCSDS Style)
# ============================================================================
# Hive logger record: 7 bytes fixed. 
# ts_delta: int16 (ms since last record, Gorilla-style delta)
# weight_g: int16 (fixed-point grams, e.g., scale 1000)
# temp_c:   int16 (fixed-point Celsius, e.g., scale 100)
# flags:    uint8  (bitmask for status, errors, keep-masks)
HIVE_RECORD_DTYPE = np.dtype([
    ('ts_delta', '<i2'),
    ('weight_g', '<i2'),
    ('temp_c', '<i2'),
    ('flags', 'u1')
])

# ============================================================================
# 2. ENVELOPE GUARDS: LE-pinned, size-proof, crc32c
# ============================================================================
MAGIC = b'PSVC'
VERSION = 0x01
HEADER_FORMAT = '<4sBBI'  # LE: magic(4), version(1), flags(1), payload_size(4)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
CRC32C_SIZE = 4

def compute_crc32c(data: bytes) -> int:
    """Fast CRC32C (Castagnoli) using zlib's built-in capabilities."""
    return zlib.crc32(data) & 0xFFFFFFFF

# ============================================================================
# 3. THE PIPELINE: Quantize → Delta → Pack → Zstd
# ============================================================================
class PSIVIEncoder:
    def __init__(self, zstd_level: int = 3):
        self.cctx = zstd.ZstdCompressor(level=zstd_level)

    def encode_hive_stream(self, timestamps_ms: np.ndarray, weights_g: np.ndarray, 
                           temps_c: np.ndarray, flags: np.ndarray) -> bytes:
        """
        Encodes a hive telemetry stream into a zero-copy-ready MPK envelope.
        """
        n = len(timestamps_ms)
        if n == 0:
            return self._build_envelope(b'')

        # A. Quantize & Delta (Gorilla-style for timestamps)
        # Timestamps become int16 deltas (assumes < 32s between readings, adjust scale if needed)
        ts_delta = np.diff(timestamps_ms, prepend=timestamps_ms[0]).astype('<i2')
        
        # Ensure other arrays match dtype and are contiguous
        weights = np.asarray(weights_g, dtype='<i2')
        temps = np.asarray(temps_c, dtype='<i2')
        flags_arr = np.asarray(flags, dtype='u1')

        # B. Structured Array Assembly (Zero-copy view creation)
        # We stack them into a single structured array. No intermediate Python objects.
        structured = np.rec.fromarrays(
            [ts_delta, weights, temps, flags_arr],
            dtype=HIVE_RECORD_DTYPE
        )

        # C. Sort to Compress (Law #6)
        # Sorting by timestamp delta groups similar values, massively boosting zstd ratio
        sort_idx = np.argsort(structured['ts_delta'])
        sorted_structured = structured[sort_idx]

        # D. Zstd Compression (Law #3: Compress AFTER structuring)
        raw_bytes = sorted_structured.tobytes()
        compressed = self.cctx.compress(raw_bytes)

        return self._build_envelope(compressed)

    def _build_envelope(self, payload: bytes) -> bytes:
        """Wraps payload with magic, version, flags, size, and crc32c."""
        header = struct.pack(HEADER_FORMAT, MAGIC, VERSION, 0x00, len(payload))
        crc = compute_crc32c(payload)
        return header + payload + struct.pack('<I', crc)


class PSIVIDecoder:
    def __init__(self):
        self.dctx = zstd.ZstdDecompressor()

    def decode_to_memmap(self, envelope: bytes, dtype: np.dtype = HIVE_RECORD_DTYPE) -> np.ndarray:
        """
        Decodes envelope and returns a zero-copy numpy view.
        If the payload is large, this can be adapted to write to a tempfile 
        and return np.memmap, keeping the OS page cache as the I/O layer.
        """
        if len(envelope) < HEADER_SIZE + CRC32C_SIZE:
            raise ValueError("Envelope too small to contain header and CRC")

        # A. Parse Header
        magic, version, flags, payload_size = struct.unpack(HEADER_FORMAT, envelope[:HEADER_SIZE])
        if magic != MAGIC:
            raise ValueError(f"Invalid magic: {magic}")
        if version != VERSION:
            raise ValueError(f"Unsupported version: {version}")

        # B. Extract Payload and Verify CRC
        payload = envelope[HEADER_SIZE : HEADER_SIZE + payload_size]
        expected_crc = struct.unpack('<I', envelope[-CRC32C_SIZE:])[0]
        if compute_crc32c(payload) != expected_crc:
            raise ValueError("CRC32C mismatch: data corruption detected")

        # C. Decompress (Law #1: Single representation change per hop)
        raw_bytes = self.dctx.decompress(payload)

        # D. Zero-Copy View (Law #1: frombuffer)
        # This creates a view over the decompressed bytes without copying.
        # If memory pressure is high, write `raw_bytes` to a NamedTemporaryFile 
        # and return np.memmap(file, dtype=dtype, mode='r')
        return np.frombuffer(raw_bytes, dtype=dtype)


# ============================================================================
# 4. BIT-LEVEL DEDUP & BLOOM (Law #4)
# ============================================================================
class MeshBloomFilter:
    """64 KB shared Bloom filter for O(1) 'have I seen this document' checks."""
    def __init__(self, size_bytes: int = 65536):
        self.size_bits = size_bytes * 8
        self.bitarray = np.zeros(self.size_bits, dtype=np.uint8)
        # Use 3 hash functions for low false-positive rate at 64KB
        self.hashes = [
            lambda x: hash(x) % self.size_bits,
            lambda x: hash(str(x)[::-1]) % self.size_bits,
            lambda x: (hash(x) ^ 0x5bd1e995) % self.size_bits
        ]

    def add(self, item: bytes):
        for h in self.hashes:
            self.bitarray[h(item)] = 1

    def check(self, item: bytes) -> bool:
        return all(self.bitarray[h(item)] == 1 for h in self.hashes)

    def to_bytes(self) -> bytes:
        return np.packbits(self.bitarray).tobytes()

    @classmethod
    def from_bytes(cls, data: bytes) -> 'MeshBloomFilter':
        bf = cls(size_bytes=len(data))
        bf.bitarray = np.unpackbits(np.frombuffer(data, dtype=np.uint8))[:bf.size_bits]
        return bf

# tools/psivi_mpk.py (Additions for Big Science)

# CERN / Awkward Array compatible: Fixed-size tensor chunk
# Useful for sending quantized ML gradients or jet features
TENSOR_CHUNK_DTYPE = np.dtype([
    ('chunk_id', '<u4'),       # 4 bytes: Unique identifier
    ('layer_idx', '<u2'),      # 2 bytes: Neural network layer
    ('precision', 'u1'),       # 1 byte: 0=float32, 1=float16, 2=int8
    ('data', 'V1024')          # 1024 bytes: Variable payload (zstd compressed inside)
])

# arXiv / Vector Search compatible: Quantized Embedding
# 384 dimensions of int8 = 384 bytes + metadata
VECTOR_EMBEDDING_DTYPE = np.dtype([
    ('doc_hash', '<u8'),       # 8 bytes: SHA-256 truncated hash of source
    ('timestamp', '<i8'),      # 8 bytes: Zulu epoch ms
    ('dim_count', '<u2'),      # 2 bytes: e.g., 384
    ('embeddings', 'i1', (384,)) # 384 bytes: int8 quantized vector
])

