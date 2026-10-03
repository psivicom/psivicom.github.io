# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import ctypes
import os
import numpy as np
from pathlib import Path

class ShannonZBridge:
    """
    Python-to-Go bridge for the Shannon-Z Entropy Kernel.
    Uses ctypes to pass raw memory pointers to the Go shared library,
    achieving zero-allocation, microsecond compression.
    """
    
    def __init__(self, lib_path: str = "src/kernel/libshannon.so"):
        self.lib_path = Path(lib_path)
        if not self.lib_path.exists():
            raise FileNotFoundError(f"Shannon-Z kernel not found at {self.lib_path}. Compile with: go build -buildmode=c-shared")
        
        self.lib = ctypes.CDLL(str(self.lib_path))
        
        # Define C function signatures for strict memory safety
        self.lib.CompressFloat16.argtypes = [
            ctypes.POINTER(ctypes.c_uint16), # src
            ctypes.c_int,                    # srcLen
            ctypes.POINTER(ctypes.c_ubyte),  # dst
            ctypes.c_int                     # dstCap
        ]
        self.lib.CompressFloat16.restype = ctypes.c_int
        
        self.lib.CalculateShannonEntropy.argtypes = [
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.c_int
        ]
        self.lib.CalculateShannonEntropy.restype = ctypes.c_double

    def compress(self, vector: np.ndarray) -> bytes:
        """
        Compresses a numpy float16 array using the Go kernel.
        Returns the compressed bytes.
        """
        if vector.dtype != np.float16:
            vector = vector.astype(np.float16)
            
        # Ensure contiguous memory for C pointer extraction
        vector = np.ascontiguousarray(vector)
        
        src_ptr = vector.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16))
        src_len = ctypes.c_int(len(vector))
        
        # Pre-allocate destination buffer (worst case: slightly larger than original)
        dst_cap = (len(vector) * 2) + 16
        dst_buffer = (ctypes.c_ubyte * dst_cap)()
        dst_ptr = ctypes.cast(dst_buffer, ctypes.POINTER(ctypes.c_ubyte))
        
        # Call Go kernel (Zero Python allocation during this step)
        bytes_written = self.lib.CompressFloat16(src_ptr, src_len, dst_ptr, ctypes.c_int(dst_cap))
        
        if bytes_written < 0:
            raise RuntimeError("Shannon-Z kernel compression failed.")
            
        # Extract the exact compressed bytes
        return bytes(dst_buffer[:bytes_written])

    def entropy(self, vector: np.ndarray) -> float:
        """Calculates the theoretical Shannon entropy of the vector."""
        if vector.dtype != np.float16:
            vector = vector.astype(np.float16)
        vector = np.ascontiguousarray(vector)
        
        src_ptr = vector.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16))
        return self.lib.CalculateShannonEntropy(src_ptr, ctypes.c_int(len(vector)))
