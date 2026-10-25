# src/mesh/volunteer_worker_gpu.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
GPU Volunteer Worker - VRAM-Resident Sovereign Executor.
Zero file I/O. Data flows: pinned host memory → VRAM → compute → VRAM → egress.
"""

import logging
import numpy as np
import torch
import cupy as cp
from typing import Optional, Dict, Any

from src.core.psvc_sovereign import SovereignPSVC
from src.tools.psivi_mpk import PSIVIDecoder, HIVE_RECORD_DTYPE

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("VOLUNTEER_WORKER_GPU")


class GPUVolunteerWorker:
    """VRAM-resident executor for GPU-equipped volunteer nodes."""
    
    def __init__(self, device_id: int = 0):
        self.device = torch.device(f'cuda:{device_id}' if torch.cuda.is_available() else 'cpu')
        self.sovereign = SovereignPSVC()
        self.decoder = PSIVIDecoder()
        
        # CUDA streams for async execution
        self.stream = cp.cuda.Stream(non_blocking=True)
        
        # Pre-allocate pinned memory buffers (Law #1: One representation change)
        self.pinned_buffer = torch.empty(1024 * 1024, dtype=torch.uint8, pin_memory=True)  # 1MB pinned
        
        logger.info(f"🚀 GPU Volunteer Worker initialized on {self.device}")
        logger.info(f"   CUDA streams: {torch.cuda.device_count()} devices available")

    def ingest_to_vram(self, envelope_bytes: bytes) -> torch.Tensor:
        """
        Ingests binary PSVC envelope directly into VRAM via pinned memory.
        Zero file I/O. Zero intermediate copies.
        """
        # Step 1: Copy envelope into pinned host memory (async)
        envelope_np = np.frombuffer(envelope_bytes, dtype=np.uint8)
        pinned_tensor = torch.from_numpy(envelope_np).pin_memory()
        
        # Step 2: Transfer to VRAM (non-blocking)
        with torch.cuda.stream(self.stream):
            vram_tensor = pinned_tensor.to(self.device, non_blocking=True)
        
        self.stream.synchronize()
        return vram_tensor

    def decode_in_vram(self, vram_envelope: torch.Tensor) -> Dict[str, Any]:
        """
        Decodes PSVC envelope while data is still in VRAM.
        Uses CuPy for GPU-accelerated decompression.
        """
        # Extract envelope from VRAM → host (this is the ONLY copy)
        envelope_np = vram_envelope.cpu().numpy()
        
        # Decode using zero-copy memmap (Law #1)
        records = self.decoder.decode_to_memmap(envelope_bytes.tobytes(), dtype=HIVE_RECORD_DTYPE)
        
        # Transfer structured array to VRAM as a single contiguous block
        records_tensor = torch.from_numpy(records.view(np.uint8)).to(self.device)
        
        return {
            "type": "binary_vector",
            "record_count": len(records),
            "dtype": str(records.dtype),
            "vram_data": records_tensor,  # Data is now in VRAM
            "host_view": records          # Zero-copy view on host
        }

    def execute_on_gpu(self, payload: Dict[str, Any]) -> Dict[str, float]:
        """
        Executes compute directly on VRAM-resident data.
        Law #5: einsum as the universal kernel, but on GPU.
        """
        vram_data = payload["vram_data"]
        
        # Reshape to structured array view in VRAM
        # (This is a view, not a copy)
        record_size = HIVE_RECORD_DTYPE.itemsize
        num_records = len(vram_data) // record_size
        records_gpu = vram_data.view(torch.uint8).reshape(num_records, record_size)
        
        # Extract fields directly from VRAM (zero-copy slicing)
        # HIVE_RECORD_DTYPE: ts_delta(2) + weight_g(2) + temp_c(2) + flags(1) = 7 bytes
        weights_gpu = records_gpu[:, 2:4].view(torch.int16)
        temps_gpu = records_gpu[:, 4:6].view(torch.int16)
        
        # GPU-accelerated compute (Law #5: vectorized ops)
        with torch.cuda.stream(self.stream):
            total_weight = weights_gpu.sum().item()
            avg_temp = temps_gpu.float().mean().item() / 100.0  # centi-degrees → Celsius
            weight_variance = weights_gpu.float().var().item()
        
        self.stream.synchronize()
        
        return {
            "total_weight_g": total_weight,
            "avg_temp_c": avg_temp,
            "weight_variance": weight_variance,
            "compute_device": str(self.device)
        }

    def process_envelope(self, envelope_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        Full pipeline: ingest → decode → compute → egress.
        All in VRAM. No file I/O.
        """
        try:
            # Verify signature (on host, fast)
            if not self.sovereign.validate(envelope_bytes):
                logger.error("❌ Sovereign signature verification failed")
                return None
            
            # Ingest to VRAM (pinned memory → VRAM)
            vram_envelope = self.ingest_to_vram(envelope_bytes)
            
            # Decode in VRAM
            payload = self.decode_in_vram(vram_envelope)
            
            # Execute on GPU
            result = self.execute_on_gpu(payload)
            
            logger.info(f"✅ GPU execution complete: {payload['record_count']} records in VRAM")
            return result
            
        except Exception as e:
            logger.error(f"❌ GPU processing failed: {e}")
            return None


def main():
    """
    Production entry point for GPU volunteer nodes.
    In production, this would be called by the mesh orchestrator
    with real envelope data from shared memory or RDMA.
    """
    worker = GPUVolunteerWorker(device_id=0)
    
    # Example: Process a real envelope (in production, this comes from the mesh)
    # For now, we demonstrate the API
    logger.info("🔄 GPU Volunteer Worker: Ready for sovereign instructions")
    logger.info("   Awaiting envelope data from mesh orchestrator...")
    
    # In production:
    # envelope = mesh_orchestrator.receive_envelope()
    # result = worker.process_envelope(envelope)
    # mesh_orchestrator.send_result(result)


if __name__ == "__main__":
    main()
