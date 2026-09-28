    def publish_beacon(self):
        """
        Announces this node's presence to the mesh.
        Creates a file: data/beacons/{node_id}.json
        Contains: ID, Status, Velocity, Last Seen, Coordinates (simulated).
        """
        beacon_dir = Path("data/beacons")
        beacon_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate a stable Node ID based on hostname or env var
        import socket
        node_id = os.getenv("WENDY_NODE_ID", socket.gethostname())
        
        beacon_data = {
            "node_id": node_id,
            "status": "ACTIVE", # ACTIVE, SLEEPING, THREAT
            "velocity": self.state["current_velocity_multiplier"],
            "last_seen": datetime.now(timezone.utc).isoformat(),
            # Simulated spatial coordinates for visualization
            # In a real P2P net, these would be GeoIP or Network Latency maps
            "coords": {
                "x": (hash(node_id) % 100) / 50.0 - 1.0, 
                "y": (hash(node_id + "_y") % 100) / 50.0 - 1.0,
                "z": (hash(node_id + "_z") % 100) / 50.0 - 1.0
            },
            "role": "CORE" if node_id == "psivicom-primary" else "VOLUNTEER"
        }
        
        filepath = beacon_dir / f"{node_id}.json"
        filepath.write_text(json.dumps(beacon_data, indent=2))
        logger.info(f"📡 Beacon Published: {node_id}")

    def run(self):
        # ... existing code ...
        
        # NEW STEP: Publish Presence before finishing
        self.publish_beacon()
        
        logger.info("🕊️ Cycle Complete. Ready for next burst.")
        return True
