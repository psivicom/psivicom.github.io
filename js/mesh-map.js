// js/mesh-map.js
class MeshMapVisualizer {
    constructor(mapElementId) {
        this.map = L.map(mapElementId).setView([48.45, -123.5], 4);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(this.map);
        this.markers = new Map();
        this.circles = [];
        this.startPolling();
    }

    async startPolling() {
        await this.fetchAndRender();
        setInterval(() => this.fetchAndRender(), 10000);
    }

    async fetchAndRender() {
        try {
            const response = await fetch(`/mesh-status.json?t=${Date.now()}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            this.render(await response.json());
        } catch (error) {
            console.error(`[${new Date().toISOString()}] Mesh fetch failed:`, error);
        }
    }

    render(data) {
        document.getElementById('radius-metric').textContent = `Dynamic Radius: ${data.dynamic_radius_km.toFixed(1)} km`;
        document.getElementById('cluster-metric').textContent = `Clusters: ${data.optimal_clusters.length} | Nodes: ${data.summary.total_nodes}`;
        document.getElementById('timestamp-metric').textContent = `Last Sync: ${data.timestamp}`;

        this.circles.forEach(c => this.map.removeLayer(c));
        this.circles = [];

        data.optimal_clusters.forEach(cluster => {
            const color = cluster.max_internal_latency_ms <= 10 ? '#00ff88' : '#ffaa00';
            const circle = L.circle([cluster.center_location.lat, cluster.center_location.lon], {
                color, fillColor: color, fillOpacity: 0.1, radius: data.dynamic_radius_km * 1000
            }).addTo(this.map);
            circle.bindPopup(`<b>Cluster:</b> ${cluster.cluster_id}<br><b>Nodes:</b> ${cluster.member_count}<br><b>Max Latency:</b> ${cluster.max_internal_latency_ms}ms`);
            this.circles.push(circle);
        });

        data.nodes.forEach(node => {
            if (!node.location?.lat) return;
            const loadColor = node.current_load < 0.5 ? '#00ff88' : node.current_load < 0.8 ? '#ffaa00' : '#ff4444';
            
            if (this.markers.has(node.nodeId)) {
                this.markers.get(node.nodeId).setLatLng([node.location.lat, node.location.lon]);
            } else {
                const marker = L.circleMarker([node.location.lat, node.location.lon], {
                    radius: 8, fillColor: loadColor, color: '#fff', weight: 1, fillOpacity: 0.9
                }).addTo(this.map);
                marker.bindPopup(`<b>Node:</b> ${node.nodeId}<br><b>Load:</b> ${(node.current_load * 100).toFixed(1)}%<br><b>Latency:</b> ${node.latency_to_wendy_core}ms`);
                this.markers.set(node.nodeId, marker);
            }
        });
    }
}
