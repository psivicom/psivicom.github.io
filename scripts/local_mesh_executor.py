# scripts/local_mesh_executor.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import logging
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s | LOCAL_EXECUTOR | %(levelname)s | %(message)s')
logger = logging.getLogger("LOCAL_EXECUTOR")

def execute_sar_spatial_repair(tensor_np: np.ndarray) -> np.ndarray:
    """
    Real mathematical repair for sparse RADARSAT SAR data.
    Applies a 3x3 Lee-filter style convolution to reduce speckle noise.
    Implemented in pure, vectorized NumPy for maximum CI/CD speed and zero bloat.
    """
    kernel = np.array([
        [0.1, 0.1, 0.1],
        [0.1, 0.2, 0.1],
        [0.1, 0.1, 0.1]
    ], dtype=np.float32)
    
    # Pad the array to handle borders (edge reflection)
    padded = np.pad(tensor_np.astype(np.float32), pad_width=1, mode='edge')
    
    # Vectorized 2D convolution using sliding windows (Blazing fast)
    windows = sliding_window_view(padded, window_shape=(3, 3))
    repaired = np.sum(windows * kernel, axis=(-2, -1))
    
    return repaired.astype(tensor_np.dtype)

def process_local_queue():
    """Scans the mesh queue and processes any pending .psvc work units locally."""
    queue_dir = Path("data/mesh_queue")
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    if not queue_dir.exists():
        logger.info("ℹ️ No mesh queue directory found.")
        return

    # Find all .psvc.json metadata files
    json_files = list(queue_dir.glob("*.psvc.json"))
    
    if not json_files:
        logger.info("ℹ️ Mesh queue is empty. No local processing needed.")
        return

    logger.info(f"🚀 Found {len(json_files)} pending work unit(s). Executing locally on GitHub runner...")

    for json_path in json_files:
        try:
            # 1. Load Metadata
            with open(json_path, 'r') as f:
                metadata = json.load(f)
            
            task_id = metadata.get("task_id")
            shape = tuple(metadata.get("shape", [64, 64]))
            dtype_str = metadata.get("dtype", "float16")
            
            # 2. Load Binary Payload
            bin_path = json_path.with_suffix(".bin")
            if not bin_path.exists():
                logger.warning(f"⚠️ Binary payload missing for {task_id}. Skipping.")
                continue
                
            np_dtype = np.float16 if dtype_str == "float16" else np.float32
            raw_bytes = bin_path.read_bytes()
            
            # 3. Reconstruct Tensor
            sparse_array = np.frombuffer(raw_bytes, dtype=np_dtype).copy()
            sparse_tensor = sparse_array.reshape(shape)
            logger.info(f"📥 Loaded {task_id} | Shape: {shape} | Size: {len(raw_bytes)} bytes")
            
            # 4. Execute Real Mathematical Repair
            repaired_tensor = execute_sar_spatial_repair(sparse_tensor)
            
            # 5. Save Repaired Output for Jupyter Assembly
            output_path = reports_dir / f"{task_id}_repaired.npy"
            np.save(output_path, repaired_tensor)
            logger.info(f"✅ Successfully repaired and saved: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {json_path.name}: {e}")

if __name__ == "__main__":
    logger.info("🔄 Initializing Local Mesh Executor (GitHub Runner Fallback)...")
    process_local_queue()
    logger.info("🏁 Local execution cycle completed.")
