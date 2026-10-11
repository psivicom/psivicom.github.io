# src/core/psvc_vector_sealer.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Mathematical Pico Container (PSVC) Sealer.
Encapsulates raw, bare-metal vector payloads into cryptographically signed, 
immutable PSVC containers, ensuring absolute provenance and integrity.
"""

import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any

from src.core.psvc_sovereign import SovereignPSVC
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("PSVC_VECTOR_SEALER")

class PSVCVectorSealer:
    def __init__(self):
        self.sovereign_identity = SovereignPSVC()
        logger.info("🔐 PSVC Vector Sealer initialized with Sovereign Identity.")

    def seal_vector_state(self, raw_payload: bytes, metadata: Dict[str, Any], output_dir: str = "reports/pico_containers") -> Path:
        """
        Takes a raw mathematical payload and seals it into a sovereign PSVC container.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 1. Compute cryptographic hash of the raw mathematical state
        payload_hash = hashlib.sha256(raw_payload).hexdigest()

        # 2. Construct the sovereign container structure
        # We store the raw bytes as a base64 or hex string for JSON compatibility, 
        # or in a production binary PSVC format, directly appended.
        # For maximum fidelity, we use a structured JSON wrapper with hex-encoded payload.
        container_data = {
            "psvc_version": "1.0.0",
            "type": "bare_metal_vector_state",
            "metadata": {
                **metadata,
                "payload_sha256": payload_hash,
                "sealed_at": get_zulu_timestamp_ms()
            },
            "payload_hex": raw_payload.hex() # Lossless byte representation
        }

        # 3. Cryptographically sign the container
        signed_container = self.sovereign_identity.create(
            data=container_data,
            metadata={"agent": "VRAM_VECTOR_ENGINE", "compliance": "EUPL-1.2"}
        )

        # 4. Write to disk as a sovereign .psvc artifact
        zulu_safe = metadata.get("timestamp", get_zulu_timestamp_ms()).replace(':', '-').replace('.', '-')
        file_name = f"vector_state_{metadata.get('checksum', 'unknown')}_{zulu_safe}.psvc"
        final_path = output_path / file_name

        with open(final_path, 'wb') as f:
            f.write(signed_container)

        logger.info(f"✅ Mathematical state sealed and sovereign: {final_path.name} ({len(raw_payload)} bytes)")
        return final_path

    @staticmethod
    def verify_and_extract(psvc_path: str) -> Dict[str, Any]:
        """
        Verifies the cryptographic integrity of a PSVC and extracts the raw mathematical payload.
        """
        path = Path(psvc_path)
        if not path.exists():
            raise FileNotFoundError(f"Sovereign container not found: {psvc_path}")

        with open(path, 'rb') as f:
            container_bytes = f.read()

        # Verify signature using SovereignPSVC
        is_valid = SovereignPSVC().validate(container_bytes)
        if not is_valid:
            raise ValueError("❌ CRITICAL: Cryptographic signature verification failed. Container may be tampered with.")

        # Extract payload
        container = json.loads(container_bytes.decode('utf-8'))
        raw_bytes = bytes.fromhex(container["payload_hex"])
        
        # Verify byte-level integrity
        if hashlib.sha256(raw_bytes).hexdigest() != container["metadata"]["payload_sha256"]:
            raise ValueError("❌ CRITICAL: Payload hash mismatch. Data corruption detected.")

        logger.info(f"✅ Sovereign container verified and extracted: {path.name}")
        return {
            "metadata": container["metadata"],
            "raw_payload": raw_bytes
        }
