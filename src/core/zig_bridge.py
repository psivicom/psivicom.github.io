# src/core/zig_bridge.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Zig Execution Bridge - Production Implementation.
Invokes compiled Zig binaries for high-performance cognitive computation.
"""

import subprocess
import logging
import tempfile
import numpy as np
from pathlib import Path
from typing import Optional

logger = logging.getLogger("ZIG_BRIDGE")

class ZigBridge:
    def __init__(self, core_dir: str = "src/core"):
        self.core_dir = Path(core_dir)
        self.vector_engine_bin = self.core_dir / "vector_engine"
        self.psvc_sealer_bin = self.core_dir / "psvc_sealer"
        
        self._verify_binaries()

    def _verify_binaries(self):
        if not self.vector_engine_bin.exists():
            raise FileNotFoundError(f"vector_engine binary not found: {self.vector_engine_bin}")
        if not self.psvc_sealer_bin.exists():
            raise FileNotFoundError(f"psvc_sealer binary not found: {self.psvc_sealer_bin}")
        logger.info("✅ Zig binaries verified.")

    def transform_vector(
        self,
        vector_data: np.ndarray,
        matrix_data: np.ndarray,
        precision: str = "32",
        output_dir: str = "reports/cognitive_computations"
    ) -> Path:
        """
        Performs bare-metal vector transformation using the Zig engine.
        
        Args:
            vector_data: Input vector (1D numpy array)
            matrix_data: Transformation matrix (2D numpy array)
            precision: "32" or "64" for float precision
            output_dir: Directory for output files
            
        Returns:
            Path to the transformed vector file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        dimension = vector_data.shape[0]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            input_file = tmp_path / "input.bin"
            matrix_file = tmp_path / "matrix.bin"
            result_file = tmp_path / "result.bin"
            
            dtype = np.float32 if precision == "32" else np.float64
            vector_data.astype(dtype).tofile(input_file)
            matrix_data.astype(dtype).tofile(matrix_file)
            
            try:
                result = subprocess.run(
                    [
                        str(self.vector_engine_bin),
                        precision,
                        str(dimension),
                        str(input_file),
                        str(matrix_file),
                        str(result_file)
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30.0
                )
                logger.info(f"✅ Zig vector transformation complete: {result.stdout.strip()}")
                
                final_output = output_path / f"transformed_{Path().cwd().name}_{dimension}d.bin"
                result_file.rename(final_output)
                
                return final_output
                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Zig transformation failed: {e.stderr}")
                raise

    def seal_payload(self, payload_bytes: bytes, precision_bits: int, timestamp_ms: int, output_path: str) -> Path:
        """Seals raw bytes into a sovereign PSVC container."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
            tmp.write(payload_bytes)
            tmp_path = tmp.name
        
        try:
            result = subprocess.run(
                [
                    str(self.psvc_sealer_bin),
                    str(precision_bits),
                    str(timestamp_ms),
                    tmp_path,
                    output_path
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=5.0
            )
            logger.info(f"✅ Zig PSVC seal complete: {result.stdout.strip()}")
            return Path(output_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
