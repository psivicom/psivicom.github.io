# src/mesh/mesh_gossip.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Mesh Gossip: Decentralized Peer Discovery.
Nodes periodically exchange signed lists of known peers to maintain 
mesh connectivity without a central directory.
"""
import logging
import json
from typing import List, Dict, Any
from src.core.psvc_sovereign import SovereignPSVC
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("MESH_GOSSIP")

class MeshGossip:
    def __init__(self, psvc_factory: SovereignPSVC, transport, known_peers: List[str] = None):
        self.psvc_factory = psvc_factory
        self.transport = transport
        self.known_peers = list(set(known_peers or []))

    def add_peer(self, peer_url: str):
        if peer_url not in self.known_peers:
            self.known_peers.append(peer_url)
            logger.info(f"🤝 Gossip: Added new peer: {peer_url}")

    def create_gossip_beacon(self, node_id: str) -> bytes:
        """Creates a signed PSVC containing this node's peer list."""
        beacon_data = {
            "node_id": node_id,
            "peers": self.known_peers,
            "timestamp": get_zulu_timestamp_ms()
        }
        
        container = self.psvc_factory.create_container(
            content_type="gossip_beacon",
            data=beacon_data,
            operation="gossip"
        )
        
        return json.dumps(container).encode('utf-8')

    def process_gossip_beacon(self, container: Dict[str, Any]) -> int:
        """Receives a beacon, verifies it, and merges the peer list."""
        try:
            if not SovereignPSVC.verify_container(container):
                logger.warning("🚫 Gossip: Rejected beacon with invalid signature.")
                return 0
                
            data = SovereignPSVC.extract_data(container)
            new_peers = data.get("peers", [])
            
            added_count = 0
            for peer in new_peers:
                if peer not in self.known_peers:
                    self.known_peers.append(peer)
                    added_count += 1
                    
            logger.info(f"🔄 Gossip: Merged {added_count} new peers. Total known: {len(self.known_peers)}")
            return added_count
            
        except Exception as e:
            logger.error(f"❌ Gossip: Failed to process beacon: {e}")
            return 0
