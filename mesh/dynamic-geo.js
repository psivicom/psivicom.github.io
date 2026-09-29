// mesh/dynamic-geo.js

const EARTH_RADIUS_KM = 6371.0;

// --- PHYSICS CONSTANTS (Based on Internet Fiber Research) ---
const INTERNET_TORTUOSITY_FACTOR = 2.1;

// --- APP BOUNDARIES ---
const MIN_RADIUS_KM = 50.0;
const GLOBAL_MAX_RADIUS_KM = 2000.0; 

// --- LATENCY TIERS (ms) ---
const PREFERRED_LATENCY_MS = 10;
const ACCEPTABLE_LATENCY_MS = 50;
const RISKY_LATENCY_MS = 200;

// --- SURGICAL / WENDY LIVE CONSTRAINTS ---
const SURGICAL_MAX_HOPS = 3;
const RECOMMENDED_TTL = 128;

class DynamicGeoCalculator {
    constructor() {
        this.latencyHistory = [];
        this.maxHistory = 50;
    }

    recordLatency(latencyMs) {
        if (typeof latencyMs !== 'number' || isNaN(latencyMs) || latencyMs <= 0) return;
        this.latencyHistory.push(latencyMs);
        if (this.latencyHistory.length > this.maxHistory) {
            this.latencyHistory.shift();
        }
    }

    getAverageLatency() {
        if (this.latencyHistory.length === 0) return 0;
        return this.latencyHistory.reduce((a, b) => a + b, 0) / this.latencyHistory.length;
    }

    classifyLatency(latencyMs) {
        if (!Number.isFinite(latencyMs) || latencyMs <= 0) return "unknown";
        if (latencyMs < PREFERRED_LATENCY_MS) return "preferred";
        if (latencyMs <= ACCEPTABLE_LATENCY_MS) return "acceptable";
        if (latencyMs <= RISKY_LATENCY_MS) return "risky";
        return "experimental";
    }

    getPhysicsBasedRadius(latencyMs) {
        if (!Number.isFinite(latencyMs) || latencyMs <= 0) return MIN_RADIUS_KM;
        const absolutePhysicalRadius = (latencyMs * 100.0) / INTERNET_TORTUOSITY_FACTOR;
        return Math.max(MIN_RADIUS_KM, Math.min(GLOBAL_MAX_RADIUS_KM, absolutePhysicalRadius));
    }

    getOperationalSearchRadius(avgLatencyMs) {
        const TARGET_LATENCY_MS = 10.0;
        if (!Number.isFinite(avgLatencyMs) || avgLatencyMs <= 0) {
            return GLOBAL_MAX_RADIUS_KM;
        }
        const congestionFactor = Math.min(1.0, TARGET_LATENCY_MS / Math.max(avgLatencyMs, 1.0));
        const desiredRadius = GLOBAL_MAX_RADIUS_KM * congestionFactor;
        return Math.max(MIN_RADIUS_KM, Math.min(GLOBAL_MAX_RADIUS_KM, desiredRadius));
    }

    getDynamicRadius() {
        const avgLatency = this.getAverageLatency();
        return this.getOperationalSearchRadius(avgLatency);
    }

    checkTtlFeasibility(initialTtl, observedHops) {
        if (!Number.isFinite(initialTtl) || !Number.isFinite(observedHops)) {
            return { ok: false, reason: "UNKNOWN_HOPS", remainingHops: null };
        }
        const remainingHops = initialTtl - observedHops;
        if (remainingHops <= 0) {
            return { ok: false, reason: "TTL_EXCEEDED", remainingHops };
        }
        if (remainingHops < 5) {
            return { ok: true, warning: "LOW_TTL_MARGIN", remainingHops };
        }
        return { ok: true, reason: "HEALTHY", remainingHops };
    }

    evaluateConnection(metrics = {}) {
        const { 
            ttl, 
            hops, 
            isVolunteerNode = false, 
            requiresSurgicalLink = false 
        } = metrics;

        const latencyMs = this.getAverageLatency();
        const trust = this.classifyLatency(latencyMs);
        const radiusKm = this.getPhysicsBasedRadius(latencyMs);
        const operationalRadiusKm = this.getOperationalSearchRadius(latencyMs);
        const ttlCheck = this.checkTtlFeasibility(ttl, hops);

        let safetyStatus = "NORMAL";
        let action = "PROCEED";

        if (requiresSurgicalLink) {
            if (trust === "risky" || trust === "experimental" || trust === "unknown") {
                safetyStatus = "UNSAFE_LATENCY_FOR_LIVE";
                action = "SAFE_HOLD_OR_REJECT";
            } else if (Number.isFinite(hops) && hops > SURGICAL_MAX_HOPS) {
                safetyStatus = "TOO_MANY_HOPS_FOR_LIVE";
                action = "SAFE_HOLD_OR_REJECT";
            } else if (isVolunteerNode) {
                safetyStatus = "VOLUNTEER_NODE_NOT_TRUSTED_FOR_LIVE";
                action = "SAFE_HOLD_OR_REJECT";
            } else if (!ttlCheck.ok) {
                safetyStatus = "TTL_FEASIBILITY_FAILED";
                action = "SAFE_HOLD_OR_REJECT";
            }
        } else {
            if (trust === "experimental") {
                action = "ALLOW_ASYNC_ONLY";
            } else if (!ttlCheck.ok) {
                action = "RETRY_OR_QUEUE";
            }
        }

        return {
            latencyMs,
            trust,
            radiusKm,
            operationalRadiusKm,
            ttlCheck,
            safetyStatus,
            action,
            isWendyLiveSafe: requiresSurgicalLink ? safetyStatus === "NORMAL" : true
        };
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
