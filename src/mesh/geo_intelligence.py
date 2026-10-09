class SpatialClusterer:
    """Grid-based spatial clustering for low-latency volunteer node grouping."""
    def __init__(self, radius_km: float):
        self.radius_km = radius_km
        self.cell_size_km = radius_km
        self.grid: Dict[str, List[Dict[str, Any]]] = {}

    def _cell_key(self, lat: float, lon: float) -> str:
        km_per_deg_lat = 111.0
        km_per_deg_lon = 111.0 * math.cos(math.radians(lat))
        cell_lat = math.floor(lat / (self.cell_size_km / km_per_deg_lat))
        cell_lon = math.floor(lon / (self.cell_size_km / km_per_deg_lon))
        return f"{cell_lat},{cell_lon}"

    def _neighbor_keys(self, lat: float, lon: float) -> List[str]:
        km_per_deg_lat = 111.0
        km_per_deg_lon = 111.0 * math.cos(math.radians(lat))
        cell_lat = math.floor(lat / (self.cell_size_km / km_per_deg_lat))
        cell_lon = math.floor(lon / (self.cell_size_km / km_per_deg_lon))
        return [f"{cell_lat + dLat},{cell_lon + dLon}" for dLat in (-1, 0, 1) for dLon in (-1, 0, 1)]

    def cluster(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.grid.clear()
        for node in nodes:
            if "lat" not in node.get("location", {}) or "lon" not in node.get("location", {}):
                continue
            key = self._cell_key(node["location"]["lat"], node["location"]["lon"])
            self.grid.setdefault(key, []).append(node)

        sorted_nodes = sorted(nodes, key=lambda x: x.get("current_load", 0))
        assigned = set()
        clusters = []

        for seed in sorted_nodes:
            node_id = seed.get("nodeId") or seed.get("id")
            if node_id in assigned or "lat" not in seed.get("location", {}):
                continue

            members = [node_id]
            assigned.add(node_id)

            for key in self._neighbor_keys(seed["location"]["lat"], seed["location"]["lon"]):
                for candidate in self.grid.get(key, []):
                    cand_id = candidate.get("nodeId") or candidate.get("id")
                    if cand_id in assigned or "lat" not in candidate.get("location", {}):
                        continue
                    
                    if GeoIntelligenceEngine.haversine_distance(seed["location"], candidate["location"]) <= self.radius_km:
                        members.append(cand_id)
                        assigned.add(cand_id)

            if len(members) >= 2:
                clusters.append({
                    "cluster_id": f"cluster-{node_id.replace('_', '')}",
                    "seed_node": node_id,
                    "center_location": seed["location"],
                    "members": members,
                    "max_radius_km": self.radius_km,
                    "timestamp": get_zulu_timestamp_ms()
                })
        return clusters
