// mesh/spatial-clustering.js
const EARTH_RADIUS_KM = 6371.0;

class SpatialClusterer {
    constructor(radiusKm) {
        this.radiusKm = radiusKm;
        this.cellSizeKm = radiusKm;
        this.grid = new Map();
    }

    _cellKey(lat, lon) {
        const kmPerDegLat = 111.0;
        const kmPerDegLon = 111.0 * Math.cos(lat * Math.PI / 180);
        const cellLat = Math.floor(lat / (this.cellSizeKm / kmPerDegLat));
        const cellLon = Math.floor(lon / (this.cellSizeKm / kmPerDegLon));
        return `${cellLat},${cellLon}`;
    }

    _neighborKeys(lat, lon) {
        const kmPerDegLat = 111.0;
        const kmPerDegLon = 111.0 * Math.cos(lat * Math.PI / 180);
        const cellLat = Math.floor(lat / (this.cellSizeKm / kmPerDegLat));
        const cellLon = Math.floor(lon / (this.cellSizeKm / kmPerDegLon));
        
        const keys = [];
        for (let dLat = -1; dLat <= 1; dLat++) {
            for (let dLon = -1; dLon <= 1; dLon++) {
                keys.push(`${cellLat + dLat},${cellLon + dLon}`);
            }
        }
        return keys;
    }

    _haversine(p1, p2) {
        const toRad = (d) => d * Math.PI / 180;
        const dLat = toRad(p2.lat - p1.lat);
        const dLon = toRad(p2.lon - p1.lon);
        const a = Math.sin(dLat / 2) ** 2 + 
                  Math.cos(toRad(p1.lat)) * Math.cos(toRad(p2.lat)) * 
                  Math.sin(dLon / 2) ** 2;
        return EARTH_RADIUS_KM * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    }

    cluster(nodes) {
        this.grid.clear();
        
        for (const node of nodes) {
            if (!node.location?.lat || !node.location?.lon) continue;
            const key = this._cellKey(node.location.lat, node.location.lon);
            if (!this.grid.has(key)) this.grid.set(key, []);
            this.grid.get(key).push(node);
        }

        const sortedNodes = [...nodes].sort((a, b) => (a.current_load || 0) - (b.current_load || 0));
        const assigned = new Set();
        const clusters = [];

        for (const seed of sortedNodes) {
            const nodeId = seed.nodeId || seed.id;
            if (assigned.has(nodeId) || !seed.location?.lat) continue;

            const members = [nodeId];
            assigned.add(nodeId);

            const neighborKeys = this._neighborKeys(seed.location.lat, seed.location.lon);
            for (const key of neighborKeys) {
                const cellNodes = this.grid.get(key) || [];
                for (const candidate of cellNodes) {
                    const candId = candidate.nodeId || candidate.id;
                    if (assigned.has(candId) || !candidate.location?.lat) continue;

                    if (this._haversine(seed.location, candidate.location) <= this.radiusKm) {
                        members.push(candId);
                        assigned.add(candId);
                    }
                }
            }

            if (members.length >= 2) {
                const maxLatency = Math.max(...members.map(id => {
                    const n = nodes.find(x => (x.id || x.nodeId) === id);
                    return n?.latency_to_wendy_core || 0;
                }));

                clusters.push({
                    cluster_id: `cluster-${nodeId.replace(/[^a-z0-9]/gi, '')}`,
                    seed_node: nodeId,
                    center_location: seed.location,
                    members,
                    member_count: members.length,
                    max_internal_latency_ms: Math.round(maxLatency * 100) / 100,
                    max_radius_km: this.radiusKm,
                    created_at: new Date().toISOString()
                });
            }
        }
        return clusters;
    }
}

module.exports = SpatialClusterer;
