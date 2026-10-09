# src/mesh/mesh_transport.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Mesh Transport: The Physical Network Layer.
Handles sending and receiving raw PSVC byte payloads between volunteer nodes.
Zero Trust: Accepts nothing without passing it to the Router for verification.
"""
import logging
import requests
from typing import Dict, Any, List
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("MESH_TRANSPORT")

class MeshTransport:
    def __init__(self, router, local_port: int = 8080):
        self.router = router
        self.local_port = local_port
        self.base_url = f"http://localhost:{local_port}/api/mesh"

    def send_psvc(self, payload_bytes: bytes, target_url: str) -> bool:
        """Broadcasts a signed PSVC to a specific peer endpoint."""
        try:
            logger.info(f"📡 Transmitting PSVC to {target_url} at {get_zulu_timestamp_ms()}...")
            headers = {"Content-Type": "application/octet-stream"}
            response = requests.post(target_url, data=payload_bytes, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info("✅ Transmission successful.")
            return True
        except Exception as e:
            logger.error(f"❌ Transmission failed to {target_url}: {e}")
            return False

    def broadcast_to_peers(self, payload_bytes: bytes, peer_urls: List[str]) -> int:
        """Blindly broadcasts a payload to all known peers (Gossip style)."""
        success_count = 0
        for url in peer_urls:
            if self.send_psvc(payload_bytes, url):
                success_count += 1
        logger.info(f"📢 Broadcast complete: {success_count}/{len(peer_urls)} peers reached.")
        return success_count

    def receive_inbound(self, payload_bytes: bytes) -> Dict[str, Any]:
        """
        Inbound handler. Passes raw bytes directly to the Router for 
        cryptographic verification and content-aware routing.
        """
        logger.debug("📥 Transport received inbound PSVC payload. Handing to Router...")
        return self.router.process_inbound_psvc(payload_bytes)
