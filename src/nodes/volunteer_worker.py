# src/nodes/volunteer_worker.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

import torch
import numpy as np
from src.core.psvc_builder import deserialize_psvc, serialize_psvc, build_psvc_container
from src.core.vector_math import compute_attention, MathState
from src.orchestrator.mesh_governor import audit_psvc_container, ValidationResult
from src.base.base_agent import BaseAgent, AgentLayer, AgentReceipt

class VolunteerWorker(BaseAgent):
    LAYER = AgentLayer.INGESTION # Operates at the edge

    def __init__(self, name: str = "volunteer_worker"):
        super().__init__(name=name, capabilities={"process_shard": self._process_shard})

    def _process_shard(self, container_bytes: bytes) -> bytes:
        """
        Functional Pipeline for Volunteer Compute:
        1. Audit incoming container (Reject if tampered).
        2. Deserialize and extract tensor.
        3. Perform mathematical operation (e.g., attention, quantization).
        4. Build NEW .psvc container with new MathState and chained receipt.
        5. Serialize and return.
        """
        # 1. GOVERNOR AUDIT (Crucial: Do not process unverified data)
        audit_result: ValidationResult = audit_psvc_container(container_bytes)
        if not audit_result.is_valid:
            raise PermissionError(f"RFC 1001 Violation: {audit_result.checks_failed}")

        # 2. Deserialize
        container = deserialize_psvc(container_bytes)
        
        # 3. Reconstruct tensor from bytes (Simulating VRAM load)
        tensor = torch.from_numpy(
            np.frombuffer(container.payload.tensor_bytes, dtype=np.dtype(container.payload.tensor_dtype))
        ).reshape(container.payload.tensor_shape)
        
        # 4. Perform Mathematical Operation (e.g., a simple transformation for this example)
        # In reality, this could be compute_attention(q, k, v, head_dim)
        processed_tensor = tensor * 1.05 # Example transformation
        
        # 5. Capture NEW Mathematical State
        new_math_state = MathState(
            operation="volunteer_scale_transform",
            input_hash=container.payload.math_state.output_hash,
            output_hash=hashlib.sha256(processed_tensor.cpu().detach().numpy().tobytes()).hexdigest(),
            vram_address=processed_tensor.data_ptr(),
            tensor_shape=tuple(processed_tensor.shape),
            flops_estimate=processed_tensor.numel(),
            timestamp=time.time()
        )
        
        # 6. Chain the Receipt (Parent is the incoming container's receipt)
        new_receipt = self.seal(
            operation="volunteer_compute_complete",
            payload={"input_shard": container.header.shard_id},
            parent_hash=container.receipt.payload_hash
        )
        
        # 7. Build and Serialize NEW Container
        new_container = build_psvc_container(
            tensor=processed_tensor,
            math_state=new_math_state,
            receipt=new_receipt,
            content_type=f"processed_{container.header.content_type}"
        )
        
        return serialize_psvc(new_container)

    def execute(self, incoming_bytes: bytes) -> bytes:
        return self.execute_capability("process_shard", incoming_bytes)
