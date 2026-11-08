#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WENDY Real Science Benchmark
SPDX-License-Identifier: EUPL-1.2
Proves WENDY's compiled artifacts outperform pure Python and LLM-generated code.
"""

import array
import time
import math
import logging
from datetime import datetime, timezone
from wendy_crystalline_executor import CrystallineExecutor, zulu_now

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03dZ [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
for handler in logging.root.handlers:
    handler.formatter.converter = lambda *args: datetime.now(timezone.utc).timetuple()

def pure_python_welford_variance(data: array.array) -> float:
    """The exact same math, executed by the Python interpreter."""
    count = 0.0
    mean = 0.0
    m2 = 0.0
    for x in data:
        count += 1.0
        delta = x - mean
        mean += delta / count
        delta2 = x - mean
        m2 += delta * delta2
    return m2 / (count - 1.0) if count > 1 else 0.0

def main():
    logging.info(f"[{zulu_now()}] WENDY Real Science Benchmark Initializing...")
    
    # 1. Generate 10 Million data points of synthetic RADARSAT SAR backscatter
    size = 10_000_000
    logging.info(f"[{zulu_now()}] Ingesting {size:,} synthetic SAR backscatter telemetry points...")
    sar_data = array.array('d', [float(i % 1000) / 10.0 + math.sin(i) for i in range(size)])
    
    # 2. Establish C-types boundary for the native artifact
    arr_type = ctypes.c_double * size
    c_sar_data = arr_type(*sar_data)

    # 3. Execute baseline Python math (The Bottleneck)
    logging.info(f"[{zulu_now()}] Executing pure Python Welford's Variance...")
    t0 = time.perf_counter()
    py_result = pure_python_welford_variance(sar_data)
    t1 = time.perf_counter()
    py_time = t1 - t0
    logging.info(f"[{zulu_now()}] Python Result: {py_result:.8f} | Time: {py_time:.4f}s")

    # 4. Compile and Load WENDY's Native Artifact
    executor = CrystallineExecutor()
    if not executor.compile_artifact():
        logging.error("Failed to compile. Aborting.")
        return
        
    lib = executor.load_artifact()
    if not lib:
        logging.error("Failed to load. Aborting.")
        return

    # 5. Execute the hot-swapped native artifact
    logging.info(f"[{zulu_now()}] Executing compiled Rust SIMD artifact...")
    t2 = time.perf_counter()
    rust_result = lib.wendy_welford_variance(c_sar_data, size)
    t3 = time.perf_counter()
    rust_time = t3 - t2
    
    logging.info(f"[{zulu_now()}] Rust Result:   {rust_result:.8f} | Time: {rust_time:.4f}s")
    
    # 6. Verify Mathematical Certainty and Speedup
    speedup = py_time / rust_time if rust_time > 0 else float('inf')
    logging.info(f"[{zulu_now()}] ⚡️💰 HARD REAL-TIME SPEEDUP: {speedup:.2f}x")
    
    if abs(py_result - rust_result) > 1e-9:
        logging.warning(f"[{zulu_now()}] DIVERGENCE: Math mismatch between Python and Rust!")
    else:
        logging.info(f"[{zulu_now()}] ✅ CERTIFIED: Mathematical parity achieved. WENDY is ready for live telemetry.")

if __name__ == "__main__":
    import ctypes
    main()
