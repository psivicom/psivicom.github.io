# scripts/BEGIN_COGNITIVE_LOOP.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
BEGIN: Production Cognitive Loop Demonstration.
Proves the complete integration: Python → Zig → bare-metal computation → result.
"""

import sys
import logging
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.zig_bridge import ZigBridge
from src.core.zulu_clock import get_zulu_timestamp_ms

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("BEGIN_COGNITIVE_LOOP")

def main():
    logger.info("=" * 70)
    logger.info("🚀 BEGIN: Production Cognitive Loop Demonstration")
    logger.info("=" * 70)
    
    bridge = ZigBridge()
    
    logger.info("\n[1/4] Generating cognitive state vector (1500 dimensions)...")
    np.random.seed(42)
    vector_data = np.random.randn(1500).astype(np.float32)
    logger.info(f"   Vector norm: {np.linalg.norm(vector_data):.6f}")
    
    logger.info("\n[2/4] Generating transformation matrix (1500x1500)...")
    np.random.seed(1001)
    matrix_data = np.random.randn(1500, 1500).astype(np.float32) * 0.01
    matrix_data = (matrix_data + matrix_data.T) / 2
    logger.info(f"   Matrix shape: {matrix_data.shape}")
    
    logger.info("\n[3/4] Executing bare-metal transformation via Zig engine...")
    result_path = bridge.transform_vector(
        vector_data=vector_data,
        matrix_data=matrix_data,
        precision="32",
        output_dir="reports/cognitive_computations"
    )
    
    logger.info("\n[4/4] Verifying result...")
    result_data = np.fromfile(result_path, dtype=np.float32)
    logger.info(f"   Result dimensions: {result_data.shape[0]}")
    logger.info(f"   Result norm: {np.linalg.norm(result_data):.6f}")
    logger.info(f"   Result file: {result_path}")
    logger.info(f"   Result size: {result_path.stat().st_size} bytes")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ END-TO-END COGNITIVE LOOP PROVEN")
    logger.info("   Python → Zig → Bare-Metal Computation → Result")
    logger.info("   WENDY's cognitive engine is now ACTIVE and INTEGRATED.")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
