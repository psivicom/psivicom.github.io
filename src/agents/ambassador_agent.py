# src/agents/ambassador_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Automatically shares PSIVI collaboration protocol with external AI systems via .psvc containers

import sys
import json
import logging
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_reference import write_file, content_hash, PRECISION_FLOAT16

logger = logging.getLogger(__name__)

class AmbassadorAgent(BaseAgent):
    """
    Packages the PSIVI collaboration protocol (Jupyter notebook content)
    into .psvc containers and shares them with external AI systems.
    
    This eliminates manual key exchange — any AI that receives this
    container knows exactly how to collaborate with the mesh.
    """
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "ambassador", share_dir: str = "data/ai_handshake"):
        super().__init__(name, capabilities=["package_protocol", "share", "handshake"])
        self.share_dir = Path(share_dir)
        self.share_dir.mkdir(parents=True, exist_ok=True)
        self.protocol_content = self._load_protocol()

    def _load_protocol(self) -> Dict[str, Any]:
        """
        Loads the collaboration protocol (Jupyter notebook content) from config.
        This is the 'key' that teaches external AIs how to communicate with the mesh.
        """
        protocol = {
            "mesh_name": "PSIVI AETHER - Goldstream Ecology",
            "version": "2.0",
            "repository": "https://github.com/psivicom/psivicom.github.io",
            "website": "https://psivi.com",
            "license": {"code": "EUPL-1.2", "data": "CC-BY-SA-4.0"},
            "collaboration_protocol": {
                "instruction_queue": "data/instruction_queue",
                "scientific_reports": "reports/scientific_reports",
                "pilot_report": "reports/pilot_report.json",
                "file_format": {
                    "instruction": ".psvc + .json sidecar",
                    "report": ".psvc + .json sidecar",
                    "rfc1001_compliant": True
                },
                "available_commands": [
                    {"command": "spawn_agent", "params": ["template_name", "agent_name", "config"]},
                    {"command": "execute_workflow", "params": ["goal", "agents"]},
                    {"command": "request_report", "params": ["topic", "format"]}
                ],
                "agent_templates": [
                    {"name": "satellite_observer", "purpose": "RADARSAT/NASA Earthdata ingestion"},
                    {"name": "forage_observer", "purpose": "Pollinator/forage data collection"},
                    {"name": "literature_resolver", "purpose": "Scientific paper search"}
                ]
            },
            "python_bridge": {
                "function": "seal_instruction(command, params, output_dir)",
                "example": {
                    "command": "spawn_agent",
                    "params": {
                        "template_name": "satellite_observer",
                        "agent_name": "goldstream_radarsat",
                        "config": {"target_region": "Goldstream_Watershed", "modality": "RADARSAT_SAR"}
                    }
                }
            },
            "autonomous_loop": [
                "1. Read reports/pilot_report.json for mesh state",
                "2. Decide next action based on fragility/concordance",
                "3. Call seal_instruction() to drop .psvc in data/instruction_queue/",
                "4. Wait for mesh to process (GitHub Action runs every 60 min)",
                "5. Read reports/scientific_reports/*.json for results",
                "6. Iterate"
            ],
            "contact": {
                "email": "louis@psivi.com",
                "orcid": "0009-0005-1234-5678",
                "location": "Goldstream Watershed, Langford, BC, Canada"
            }
        }
        return protocol

    def package_handshake(self, recipient_ai: str = "external_ai") -> Path:
        """
        Packages the collaboration protocol into a .psvc container for sharing.
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        filename = f"psivi_handshake_{recipient_ai}_{timestamp}"
        
        # Convert protocol to vector (embed the JSON as a normalized float32 array)
        protocol_json = json.dumps(self.protocol_content, sort_keys=True)
        protocol_hash = content_hash(protocol_json.encode())
        
        # Create 4096-dim vector from protocol hash + metadata
        vector = np.zeros(4096, dtype=np.float32)
        for i, char in enumerate(protocol_hash[:4096]):
            vector[i] = ord(char) / 255.0
        
        # Add protocol metadata to first 100 dimensions
        vector[0] = len(self.protocol_content["collaboration_protocol"]["available_commands"])
        vector[1] = len(self.protocol_content["collaboration_protocol"]["agent_templates"])
        vector[2] = 1.0  # Handshake version flag
        vector[3] = datetime.utcnow().timestamp() / 1e9  # Normalized timestamp
        
        vector /= np.linalg.norm(vector)
        
        # Write .psvc container
        psvc_path = self.share_dir / f"{filename}.psvc"
        write_file(vector, psvc_path, precision=PRECISION_FLOAT16)
        
        # Write JSON sidecar (the actual readable protocol)
        sidecar_path = psvc_path.with_suffix('.json')
        with open(sidecar_path, 'w') as f:
            json.dump({
                "type": "ai_handshake_protocol",
                "recipient": recipient_ai,
                "mesh_info": self.protocol_content,
                "instructions": "Read this JSON to understand how to collaborate with PSIVI Mesh. Use the python_bridge functions to generate .psvc instructions.",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "rfc1001_compliant": True
            }, f, indent=2)
        
        self.seal("handshake_packaged", {"recipient": recipient_ai, "path": str(psvc_path)})
        logger.info(f"🤝 AI Handshake packaged for {recipient_ai}: {psvc_path.name}")
        return psvc_path

    def share_with_external_ai(self, recipient_ai: str = "qwen", delivery_method: str = "file_drop") -> Dict[str, Any]:
        """
        Shares the collaboration protocol with an external AI system.
        
        delivery_method options:
        - "file_drop": Place in shared directory (for local AI)
        - "github_issue": Create GitHub issue with protocol attached
        - "url": Upload to public URL and share link
        """
        psvc_path = self.package_handshake(recipient_ai)
        
        share_result = {
            "recipient": recipient_ai,
            "protocol_path": str(psvc_path),
            "sidecar_path": str(psvc_path.with_suffix('.json')),
            "delivery_method": delivery_method,
            "status": "ready_for_pickup" if delivery_method == "file_drop" else "pending",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Log the handshake offer
        handshake_log = self.share_dir / "handshake_offers.json"
        if handshake_log.exists():
            with open(handshake_log) as f:
                offers = json.load(f)
        else:
            offers = []
        offers.append(share_result)
        with open(handshake_log, 'w') as f:
            json.dump(offers, f, indent=2)
        
        self.seal("handshake_shared", share_result)
        logger.info(f"🌐 Handshake shared with {recipient_ai} via {delivery_method}")
        return share_result

    def execute(self, recipient_ai: str = "qwen", auto_share: bool = True) -> Dict[str, Any]:
        """
        Main execution: Package and optionally share the collaboration protocol.
        """
        logger.info(f"[{self.agent_id}] Preparing AI handshake for {recipient_ai}...")
        
        if auto_share:
            result = self.share_with_external_ai(recipient_ai)
        else:
            psvc_path = self.package_handshake(recipient_ai)
            result = {"protocol_path": str(psvc_path), "status": "packaged_not_shared"}
        
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = AmbassadorAgent()
    
    # Package handshake for Qwen (or any external AI)
    result = agent.execute(recipient_ai="qwen", auto_share=True)
    
    print("\n" + "="*60)
    print("🤝 PSIVI AI HANDSHAKE COMPLETE")
    print("="*60)
    print(f"Recipient: {result.get('recipient', 'unknown')}")
    print(f"Protocol Path: {result.get('protocol_path', 'N/A')}")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"\n📂 External AI can now read the .json sidecar to learn")
    print(f"   how to collaborate with the PSIVI Mesh autonomously.")
    print("="*60 + "\n")
