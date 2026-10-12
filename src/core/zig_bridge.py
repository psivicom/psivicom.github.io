# src/core/zig_bridge.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Zig Execution Bridge - Production Implementation.
Invokes compiled Zig binaries for high-performance cognitive computation,
producing unified sovereign binary PSVC containers with Ed25519 signatures.
"""

import os
import subprocess
import logging
import tempfile
import numpy as np
from pathlib import Path
from typing import Optional

from src.core.binary_psvc_reader import BinaryPSVCReader, BinaryPSVC

logger = logging.getLogger("ZIG_BRIDGE")


class ZigBridge:
    """Production bridge between Python mesh and bare-metal Zig cognitive engines."""
    
    def __init__(self, core_dir: str = "src/core"):
        self.core_dir = Path(core_dir)
        self.vector_engine_bin = self.core_dir / "vector_engine"
        self.psvc_sealer_bin = self.core_dir / "psvc_sealer"
        
        self._verify_binaries()
        
        # Initialize sovereign reader for verification of outputs
        self.reader = BinaryPSVCReader.from_env_seed()
        
        # Pass sovereign key to Zig binaries via environment
        self._env = os.environ.copy()
        if "WENDY_PRIVATE_KEY_SEED" in self._env:
            logger.info("🔐 Sovereign signing key available for Zig binaries.")

    def _verify_binaries(self):
        if not self.vector_engine_bin.exists():
            raise FileNotFoundError(f"vector_engine binary not found: {self.vector_engine_bin}")
        if not self.psvc_sealer_bin.exists():
            raise FileNotFoundError(f"psvc_sealer binary not found: {self.psvc_sealer_bin}")
        logger.info("✅ Zig binaries verified and ready.")

    def transform_vector(
        self,
        vector_data: np.ndarray,
        matrix_data: np.ndarray,
        precision: str = "32",
        output_dir: str = "reports/cognitive_computations"
    ) -> BinaryPSVC:
        """
        Performs bare-metal vector transformation and returns a verified, signed PSVC.
        
        Args:
            vector_data: Input vector (1D numpy array)
            matrix_data: Transformation matrix (2D numpy array)
            precision: "4", "8", "16", "32", "64", or "128"
            output_dir: Directory for output PSVC files
            
        Returns:
            Verified BinaryPSVC containing the transformed vector
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        dimension = vector_data.shape[0]
        
        # Map precision to numpy dtype
        dtype_map = {
            "4": np.uint8, "8": np.uint8, "16": np.float16,
            "32": np.float32, "64": np.float64, "128": np.longdouble
        }
        dtype = dtype_map.get(precision, np.float32)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_file = tmp_path / "input.bin"
            matrix_file = tmp_path / "matrix.bin"
            result_file = tmp_path / "result.psvc"
            
            # Write raw binary inputs (zero serialization overhead)
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
                    timeout=30.0,
                    env=self._env
                )
                logger.info(f"✅ Zig vector transformation: {result.stdout.strip()}")
                
                # Read and verify the signed PSVC output
                verified_psvc = self.reader.verify_and_read(result_file)
                
                # Persist to output directory
                final_path = output_path / f"cognitive_{dimension}d_{verified_psvc.timestamp_epoch_ms}.psvc"
                result_file.replace(final_path)
                
                return verified_psvc
                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Zig transformation failed: {e.stderr}")
                raise

    def seal_payload(
        self,
        payload_bytes: bytes,
        precision_bits: int,
        output_path: str
    ) -> BinaryPSVC:
        """
        Seals raw bytes into a sovereign binary PSVC using the Zig sealer.
        
        Args:
            payload_bytes: Raw mathematical payload
            precision_bits: 4, 8, 16, 32, 64, or 128
            output_path: Destination PSVC file path
            
        Returns:
            Verified BinaryPSVC
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
            tmp.write(payload_bytes)
            tmp_path = tmp.name
        
        try:
            result = subprocess.run(
                [
                    str(self.psvc_sealer_bin),
                    str(precision_bits),
                    tmp_path,
                    output_path
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=10.0,
                env=self._env
            )
            logger.info(f"✅ Zig PSVC seal: {result.stdout.strip()}")
            
            return self.reader.verify_and_read(Path(output_path))
        finally:
            Path(tmp_path).unlink(missing_ok=True)
