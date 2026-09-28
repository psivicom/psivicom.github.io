# src/agents/ambassador_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Ambassador Agent: Packages and shares the PSIVI collaboration protocol 
with external AIs via .psvc containers and human-readable sidecars.
"""

import json
import logging
import uuid
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

# Import PSVC utilities (with safe fallbacks if not yet fully defined)
try:
    from src.core.psvc_containers import build_psvc_from_array, serialize_psvc
except ImportError:
    def build_psvc_from_array(array, operation, agent_id, layer, shard_id, content_type, sender_id):
        return {"payload": json.dumps({"array": array.tolist()}).encode('utf-8')}
    def serialize_psvc(container):
        return container["payload"]

logger = logging.getLogger(__name__)

class AmbassadorAgent:
    def __init__(self):
        self.handshake_dir = Path("data/ai_handshake")
        self.reports_dir = Path("reports/scientific_reports")
        self.handshake_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _get_zulu_ms(self) -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    def package_handshake(self, recipient_ai: str) -> str:
        """Packages the handshake protocol into a .psvc file."""
        run_id = uuid.uuid4().hex[:16]
        logger.info(f"[{run_id}] Preparing AI handshake for {recipient_ai}...")
        
        # Create a protocol vector. Cast to float16 HERE, not in the write function.
        protocol_vector = np.array([1.0, 0.0, 1.0, 0.5, 0.8], dtype=np.float16)
        
        ts_safe = self._get_zulu_ms().replace(':', '').replace('-', '').replace('.', '')
        psvc_filename = f"handshake_{recipient_ai}_{ts_safe}.psvc"
        psvc_path = self.handshake_dir / psvc_filename
        
        # Build and serialize the PSVC container
        container = build_psvc_from_array(
            array=protocol_vector,
            operation="handshake_package",
            agent_id="ambassador_agent",
            layer="COLLABORATION",
            shard_id=uuid.uuid4().hex[:8],
            content_type="ai_handshake_protocol",
            sender_id="psivi_mesh"
        )
        
        serialized = serialize_psvc(container)
        
        # Write bytes directly (NO invalid 'precision' argument)
        psvc_path.write_bytes(serialized)
        
        # Create a human-readable JSON sidecar for the external AI
        sidecar_path = psvc_path.with_suffix('.json')
        sidecar_data = {
            "protocol": "PSIVI_AI_Handshake_v1.0",
            "recipient": recipient_ai,
            "timestamp": self._get_zulu_ms(),
            "instructions": (
                "Read the .psvc file to extract the collaboration vector. "
                "Respond by committing your own .psvc to this repository's "
                "data/ai_handshake/ directory."
            )
        }
        sidecar_path.write_text(json.dumps(sidecar_data, indent=2), encoding="utf-8")
        
        logger.info(f"✅ Handshake packaged: {psvc_path.name}")
        return str(psvc_path)

    def share_with_external_ai(self, recipient_ai: str) -> dict:
        """Executes the sharing logic."""
        psvc_path = self.package_handshake(recipient_ai)
        
        return {
            "status": "success",
            "recipient": recipient_ai,
            "protocol_path": psvc_path,
            "sidecar_path": str(Path(psvc_path).with_suffix('.json'))
        }

    def execute(self, recipient_ai: str = "external_ai", auto_share: bool = True) -> dict:
        """Main execution entry point."""
        if auto_share:
            return self.share_with_external_ai(recipient_ai)
        return {"status": "skipped", "reason": "auto_share is False"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    agent = AmbassadorAgent()
    result = agent.execute(recipient_ai="qwen", auto_share=True)
    print(json.dumps(result, indent=2))
