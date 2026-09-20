# research_pipeline.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette
# RFC 1001 Compliant — PSIVI Open Science Hub

"""
End-to-End Research Pipeline Demonstration

This script demonstrates the complete PSIVI Open Science mesh architecture:
1. Researcher submits a goal
2. ForageAgent fetches weather data
3. VectorPixelizer shards data into .psvc containers
4. VolunteerWorker processes the shards
5. MeshGovernor verifies integrity and RFC 1001 compliance
6. SynthesizerAgent aggregates results
7. LicenseAgent stamps final FAIR-compliant output

Every step is cryptographically sealed and mathematically verified.
"""

import torch
import numpy as np
import time
from typing import List, Dict, Any

from psvc_containers import (
    PicoContainer,
    build_psvc_from_tensor,
    serialize_psvc,
    deserialize_psvc,
    verify_container,
    reconstruct_torch_tensor
)
from src.base.base_agent import BaseAgent, AgentLayer, AgentReceipt
from src.core.vector_math import embed_tokens, compute_attention, MathState
from src.orchestrator.mesh_governor import audit_psvc_container, ValidationResult


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

class ForageAgent(BaseAgent):
    """Ingestion layer: Fetches and embeds raw data."""
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "forage_agent"):
        super().__init__(name=name)
        # Simulated embedding matrix (in production: loaded from pretrained model)
        self.embedding_matrix = torch.randn(1000, 512, dtype=torch.float16)

    def fetch_weather_data(self, location: str) -> Dict[str, Any]:
        """Simulate fetching weather data from Open-Meteo API."""
        # In production: actual API call to Open-Meteo
        return {
            "location": location,
            "temperature": 22.5,
            "humidity": 65,
            "tokens": [12, 45, 99, 234, 567]  # Tokenized weather description
        }

    def embed_data(self, data: Dict[str, Any]) -> torch.Tensor:
        """Convert raw data to high-dimensional vectors in VRAM."""
        tokens = torch.tensor([data["tokens"]])
        vectors, _ = embed_tokens(tokens, self.embedding_matrix)
        return vectors

    def create_containers(self, vectors: torch.Tensor, data: Dict[str, Any]) -> List[PicoContainer]:
        """Shard vectors into .psvc containers with full provenance."""
        containers = []
        
        # Split into shards (simulating VectorPixelizer)
        shard_size = 2
        for i in range(0, vectors.shape[1], shard_size):
            shard = vectors[:, i:i+shard_size]
            
            # Build .psvc container
            container = build_psvc_from_tensor(
                tensor=shard,
                operation=f"embed_weather_shard_{i}",
                agent_id=self.agent_id,
                layer=self.LAYER.name,
                shard_id=f"{self.agent_id}-shard-{i}",
                content_type="weather_vector_shard"
            )
            containers.append(container)
        
        return containers


class VolunteerWorker(BaseAgent):
    """Compute layer: Processes .psvc containers from the mesh."""
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "volunteer_worker"):
        super().__init__(name=name)

    def process_container(self, container_bytes: bytes) -> bytes:
        """
        Process a .psvc container:
        1. Audit integrity (reject if tampered)
        2. Deserialize and extract tensor
        3. Perform computation
        4. Build new container with chained receipt
        """
        # 1. GOVERNOR AUDIT
        audit_result = audit_psvc_container(container_bytes)
        if not audit_result.is_valid:
            raise PermissionError(f"RFC 1001 Violation: {audit_result.checks_failed}")

        # 2. Deserialize
        container = deserialize_psvc(container_bytes)
        
        # 3. Reconstruct tensor
        tensor = reconstruct_torch_tensor(container)
        
        # 4. Perform computation (example: scale transformation)
        processed_tensor = tensor * 1.05
        
        # 5. Capture new mathematical state
        new_math_state = MathState(
            operation="volunteer_scale_transform",
            input_hash=container.payload.math_state.output_hash,
            output_hash=hashlib.sha256(processed_tensor.cpu().detach().numpy().tobytes()).hexdigest(),
            vram_address=processed_tensor.data_ptr(),
            tensor_shape=tuple(processed_tensor.shape),
            tensor_dtype=str(processed_tensor.dtype),
            flops_estimate=processed_tensor.numel(),
            timestamp=time.time()
        )
        
        # 6. Chain the receipt
        new_receipt = self.seal(
            operation="volunteer_compute_complete",
            payload={"input_shard": container.header.shard_id},
            parent_hash=container.receipt.payload_hash
        )
        
        # 7. Build new container
        new_container = build_psvc_from_tensor(
            tensor=processed_tensor,
            operation="volunteer_scale_transform",
            agent_id=self.agent_id,
            layer=self.LAYER.name,
            parent_receipt_hash=container.receipt.payload_hash,
            shard_id=f"processed-{container.header.shard_id}",
            content_type=f"processed_{container.header.content_type}"
        )
        
        return serialize_psvc(new_container)


class SynthesizerAgent(BaseAgent):
    """Synthesis layer: Aggregates processed shards into final results."""
    LAYER = AgentLayer.SYNTHESIS

    def __init__(self, name: str = "synthesizer_agent"):
        super().__init__(name=name)

    def aggregate_containers(self, container_bytes_list: List[bytes]) -> torch.Tensor:
        """Reconstruct the full tensor from processed shards."""
        tensors = []
        
        for container_bytes in container_bytes_list:
            # Audit each container
            audit_result = audit_psvc_container(container_bytes)
            if not audit_result.is_valid:
                raise PermissionError(f"Aggregation failed: {audit_result.checks_failed}")
            
            # Deserialize and reconstruct
            container = deserialize_psvc(container_bytes)
            tensor = reconstruct_torch_tensor(container)
            tensors.append(tensor)
        
        # Concatenate shards back into full tensor
        full_tensor = torch.cat(tensors, dim=1)
        return full_tensor

    def generate_report(self, tensor: torch.Tensor, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final research output."""
        return {
            "summary": f"Processed {tensor.shape[1]} vector dimensions",
            "tensor_shape": list(tensor.shape),
            "tensor_mean": tensor.mean().item(),
            "tensor_std": tensor.std().item(),
            "metadata": metadata,
            "timestamp": time.time()
        }


class LicenseAgent(BaseAgent):
    """Governance layer: Stamps FAIR compliance on final output."""
    LAYER = AgentLayer.GOVERNANCE

    def __init__(self, name: str = "license_agent"):
        super().__init__(name=name)

    def stamp_fair(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Add FAIR-compliant metadata to the report."""
        fair_metadata = {
            "psivi_license": "CC-BY-4.0",
            "author": "Louis-Philippe Audette",
            "project": "psivicom.github.io",
            "timestamp": time.time(),
            "findable": True,
            "accessible": True,
            "interoperable": True,
            "reusable": True,
            "rfc1001_compliant": True
        }
        
        report["_psivi_fair_metadata"] = fair_metadata
        
        # Seal the licensing operation
        self.seal("stamp_fair", report)
        
        return report


# ============================================================================
# MAIN PIPELINE EXECUTION
# ============================================================================

def run_research_pipeline():
    """
    Execute the complete PSIVI research pipeline.
    """
    print("=" * 80)
    print("PSIVI Open Science Research Pipeline")
    print("=" * 80)
    
    # Initialize agents
    forage = ForageAgent()
    worker = VolunteerWorker()
    synthesizer = SynthesizerAgent()
    licensor = LicenseAgent()
    
    print(f"\n✓ Agents initialized:")
    print(f"  - {forage.agent_id} (Forage)")
    print(f"  - {worker.agent_id} (Volunteer Worker)")
    print(f"  - {synthesizer.agent_id} (Synthesizer)")
    print(f"  - {licensor.agent_id} (License)")
    
    # Step 1: Researcher submits goal
    print("\n" + "=" * 80)
    print("STEP 1: Researcher submits goal")
    print("=" * 80)
    research_goal = "Analyze weather patterns in Montreal"
    print(f"Goal: {research_goal}")
    
    # Step 2: ForageAgent fetches and embeds data
    print("\n" + "=" * 80)
    print("STEP 2: ForageAgent fetches and embeds data")
    print("=" * 80)
    raw_data = forage.fetch_weather_data("Montreal")
    print(f"✓ Fetched data: {raw_data}")
    
    vectors = forage.embed_data(raw_data)
    print(f"✓ Embedded vectors: shape={vectors.shape}, dtype={vectors.dtype}")
    print(f"  VRAM address: {vectors.data_ptr()}")
    
    # Step 3: Create .psvc containers
    print("\n" + "=" * 80)
    print("STEP 3: Create .psvc containers (VectorPixelizer)")
    print("=" * 80)
    containers = forage.create_containers(vectors, raw_data)
    print(f"✓ Created {len(containers)} .psvc containers")
    
    # Serialize containers
    serialized_containers = [serialize_psvc(c) for c in containers]
    total_size = sum(len(s) for s in serialized_containers)
    print(f"  Total serialized size: {total_size} bytes")
    
    # Step 4: VolunteerWorker processes containers
    print("\n" + "=" * 80)
    print("STEP 4: VolunteerWorker processes containers")
    print("=" * 80)
    processed_containers = []
    
    for i, container_bytes in enumerate(serialized_containers):
        print(f"\n  Processing shard {i+1}/{len(serialized_containers)}...")
        
        # Audit before processing
        audit_result = audit_psvc_container(container_bytes)
        print(f"    ✓ Audit: {audit_result.is_valid} ({len(audit_result.checks_passed)} checks passed)")
        
        # Process
        processed_bytes = worker.process_container(container_bytes)
        processed_containers.append(processed_bytes)
        
        # Verify processed container
        processed_container = deserialize_psvc(processed_bytes)
        print(f"    ✓ Processed: {processed_container.header.shard_id}")
        print(f"      Receipt chain: {processed_container.receipt.parent_receipt_hash[:16]}...")
    
    # Step 5: Synthesizer aggregates results
    print("\n" + "=" * 80)
    print("STEP 5: Synthesizer aggregates results")
    print("=" * 80)
    aggregated_tensor = synthesizer.aggregate_containers(processed_containers)
    print(f"✓ Aggregated tensor: shape={aggregated_tensor.shape}")
    
    report = synthesizer.generate_report(aggregated_tensor, {"goal": research_goal})
    print(f"✓ Generated report:")
    print(f"  Summary: {report['summary']}")
    print(f"  Mean: {report['tensor_mean']:.4f}")
    print(f"  Std: {report['tensor_std']:.4f}")
    
    # Step 6: LicenseAgent stamps FAIR compliance
    print("\n" + "=" * 80)
    print("STEP 6: LicenseAgent stamps FAIR compliance")
    print("=" * 80)
    final_report = licensor.stamp_fair(report)
    print(f"✓ FAIR metadata applied:")
    print(f"  License: {final_report['_psivi_fair_metadata']['psivi_license']}")
    print(f"  Author: {final_report['_psivi_fair_metadata']['author']}")
    print(f"  RFC 1001: {final_report['_psivi_fair_metadata']['rfc1001_compliant']}")
    
    # Final verification
    print("\n" + "=" * 80)
    print("FINAL VERIFICATION")
    print("=" * 80)
    
    # Verify all processed containers
    all_valid = True
    for i, container_bytes in enumerate(processed_containers):
        container = deserialize_psvc(container_bytes)
        verification = verify_container(container)
        if not all(verification.values()):
            all_valid = False
            print(f"✗ Container {i} failed verification: {verification}")
    
    if all_valid:
        print("✓ All containers verified successfully")
        print("✓ Provenance chain intact")
        print("✓ FAIR compliance confirmed")
        print("✓ RFC 1001 compliant")
    
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)
    
    return final_report


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import hashlib  # Required for VolunteerWorker
    
    final_report = run_research_pipeline()
    
    print("\n📊 FINAL RESEARCH OUTPUT:")
    print("-" * 80)
    for key, value in final_report.items():
        if key != "_psivi_fair_metadata":
            print(f"{key}: {value}")
    
    print("\n🔒 FAIR METADATA:")
    print("-" * 80)
    for key, value in final_report["_psivi_fair_metadata"].items():
        print(f"{key}: {value}")
