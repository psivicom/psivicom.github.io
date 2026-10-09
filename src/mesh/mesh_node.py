# src/mesh/mesh_node.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Mesh Node: The Sovereign Conductor.
Initializes and ties together the Kernel, Router, Gossip, and Transport
to form a fully autonomous, decentralized mesh participant.
"""
import logging
import json
from pathlib import Path
from src.core.sovereign_kernel import SovereignKernel
from src.core.psvc_sovereign import SovereignKeyPair, SovereignPSVC
from src.mesh.mesh_router import SovereignMeshRouter
from src.mesh.mesh_gossip import MeshGossip
from src.mesh.mesh_transport import MeshTransport
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("MESH_NODE")

class MeshNode:
    def __init__(self, root_dir: str = ".", port: int = 8080, node_id: str = "node_01"):
        self.root = Path(root_dir)
        self.node_id = node_id
        
        # 1. Initialize Sovereign Identity
        self.keys = SovereignKeyPair(self.root / "data/wendy_private.key")
        self.psvc_factory = SovereignPSVC(self.keys)
        
        # 2. Initialize Subsystems
        self.kernel = SovereignKernel(root_dir=root_dir, key_pair=self.keys)
        self.router = SovereignMeshRouter()
        self.transport = MeshTransport(router=self.router, local_port=port)
        self.gossip = MeshGossip(psvc_factory=self.psvc_factory, transport=self.transport, known_peers=[])
        
        # Wire Router to handle Gossip (Circular dependency resolution)
        # In a full implementation, the Router would have a callback to the Gossip module
        
        logger.info(f"🌐 Mesh Node '{self.node_id}' initialized. Sovereign systems online at {get_zulu_timestamp_ms()}.")

    def start(self):
        """Main lifecycle for the mesh node."""
        logger.info("🚀 Starting Mesh Node. Initiating sovereign lifecycle...")
        self.simulate_lifecycle()

    def simulate_lifecycle(self):
        """Demonstrates the node exporting its soul and gossiping to the mesh."""
        logger.info("🧬 1. Exporting sovereign soul state...")
        soul_bytes = self.kernel.export_soul(target_node_id="global_mesh")
        
        logger.info("📡 2. Broadcasting soul to known peers...")
        # In production, these would be real volunteer endpoints
        mock_peers = ["http://volunteer-1.net:8080/api/mesh", "http://volunteer-2.org:8080/api/mesh"]
        self.transport.broadcast_to_peers(soul_bytes, mock_peers)
        
        logger.info("🤝 3. Emitting gossip beacon...")
        beacon_bytes = self.gossip.create_gossip_beacon(self.node_id)
        self.transport.broadcast_to_peers(beacon_bytes, mock_peers)
        
        logger.info(f"✅ Simulation complete at {get_zulu_timestamp_ms()}. Node returning to idle state.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    # Ensure data directories exist
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("src").mkdir(parents=True, exist_ok=True)
    
    node = MeshNode(node_id="goldstream_primary")
    node.start()
