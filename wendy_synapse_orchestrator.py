#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WENDY Synapse Orchestrator
SPDX-License-Identifier: EUPL-1.2
Demonstrates the Ouroboros loop: identifying slow Python math, dreaming a Rust 
crystal, compiling the artifact, and hot-swapping it for native execution.
"""

import array
import time
import ctypes
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

def pure_python_variance(data: array.array) -> float:
    """Baseline slow Python math for Earth Observation backscatter data."""
    mean = sum(data) / len(data)
    return sum((x - mean) ** 2 for x in data) / len(data)

def main():
    logging.info(f"[{zulu_now()}] WENDY Synapse Orchestrator initializing...")
    
    # 1. Generate dummy RADARSAT SAR backscatter data (10 million data points)
    logging.info(f"[{zulu_now()}] Ingesting synthetic RADARSAT backscatter array...")
    size = 10_000_000
    sar_data = array.array('d', [float(i % 100) / 10.0 for i in range(size)])
    
    # 2. Establish C-types boundary for the native artifact
    arr_type = ctypes.c_double * size
    c_sar_data = arr_type(*sar_data)

    # 3. Execute baseline Python math (The Bottleneck)
    logging.info(f"[{zulu_now()}] Executing baseline Python variance calculation...")
    t0 = time.perf_counter()
    py_result = pure_python_variance(sar_data)
    t1 = time.perf_counter()
    py_time = t1 - t0
    logging.info(f"[{zulu_now()}] Python result: {py_result:.4f} | Time: {py_time:.4f}s")

    # 4. The Ouroboros Loop: WENDY dreams a native Rust crystal to replace the bottleneck
    executor = CrystallineExecutor()
    
    # The exact Rust body to calculate variance natively
    rust_logic = """
    let mean = slice.iter().sum::<f64>() / len as f64;
    slice.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / len as f64
    """
    
    func_name = "crystalline_sar_variance"
    
    if executor.dream_and_compile_crystal(func_name, rust_logic):
        lib = executor.load_artifact()
        if lib:
            # Map the C-FFI signature
            native_func = getattr(lib, func_name)
            native_func.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
            native_func.restype = ctypes.c_double

            # 5. Execute the hot-swapped native artifact
            logging.info(f"[{zulu_now()}] Executing hot-swapped native Rust crystal...")
            t2 = time.perf_counter()
            rust_result = native_func(c_sar_data, size)
            t3 = time.perf_counter()
            rust_time = t3 - t2
            
            logging.info(f"[{zulu_now()}] Rust result:   {rust_result:.4f} | Time: {rust_time:.4f}s")
            
            speedup = py_time / rust_time if rust_time > 0 else float('inf')
            logging.info(f"[{zulu_now()}] ⚡️💰 Ouroboros Optimization Achieved: {speedup:.2f}x speedup. Electricity saved.")
            
            if abs(py_result - rust_result) > 0.0001:
                logging.warning(f"[{zulu_now()}] Mathematical divergence detected between Python and Rust artifact!")
            else:
                logging.info(f"[{zulu_now()}] Crystalline artifact mathematically verified. Synapse optimized.")

if __name__ == "__main__":
    main()
