// mesh/dynamic-geo.js
const EARTH_RADIUS_KM = 6371.0;
const TARGET_LATENCY_MS = 10.0;
const BASE_KM_PER_MS = 20.0; // Fixed: 20km per ms, not 200km

class DynamicGeoCalculator {
    constructor() {
        this.latencyHistory = [];
        this.maxHistory = 50;
    }

    recordLatency(latencyMs) {
        if (typeof latencyMs !== 'number' || isNaN(latencyMs)) return;
        this.latencyHistory.push(latencyMs);
        if (this.latencyHistory.length > this.maxHistory) {
            this.latencyHistory.shift();
        }
    }

    getDynamicRadius() {
        if (this.latencyHistory.length === 0) {
            return 200.0; // Default: 200km when no data
        }

        const avgLatency = this.latencyHistory.reduce((a, b) => a + b, 0) / this.latencyHistory.length;
        const congestionFactor = Math.min(1.0, TARGET_LATENCY_MS / Math.max(avgLatency, 1.0));
        const dynamicRadius = (TARGET_LATENCY_MS * BASE_KM_PER_MS) * congestionFactor;
        
        // Strict clamping: never below 50km, never above 200km
        return Math.max(50.0, Math.min(200.0, dynamicRadius));
    }

    haversineDistance(point1, point2) {
        const toRad = (deg) => deg * (Math.PI / 180);
        const dLat = toRad(point2.lat - point1.lat);
        const dLon = toRad(point2.lon - point1.lon);
        const a = Math.sin(dLat / 2) ** 2 + 
                  Math.cos(toRad(point1.lat)) * Math.cos(toRad(point2.lat)) * 
                  Math.sin(dLon / 2) ** 2;
        return EARTH_RADIUS_KM * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    }
}

module.exports = DynamicGeoCalculator;
