/**
 * mesh/dynamic-geo.js
 * 
 * Dynamic Geographic & Network Feasibility Calculator for "Wendy"
 * 
 * This module treats Wendy's live connection like a surgical robot:
 * 1. Physics-based radius (Akamai rule of thumb: RTT * 100 / 2.1)
 * 2. Latency trust tiers (Preferred, Acceptable, Risky, Experimental)
 * 3. Hop/TTL feasibility checks
 * 4. Surgical safety constraints for live control vs. async data
 */

const EARTH_RADIUS_KM = 6371.0;

// --- PHYSICS CONSTANTS (Based on Internet Fiber Research) ---
// Speed of light in fiber is ~200,000 km/s (200 km/ms)
// Internet tortuosity factor (refraction + physical routing) is ~2.1
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

    /**
     * Records a new latency sample (Round Trip Time in ms).
     */
    recordLatency(latencyMs) {
        if (typeof latencyMs !== 'number' || isNaN(latencyMs) || latencyMs <= 0) return;
        this.latencyHistory.push(latencyMs);
        if (this.latencyHistory.length > this.maxHistory) {
            this.latencyHistory.shift();
        }
    }

    /**
     * Calculates the average latency from the history buffer.
     */
    getAverageLatency() {
        if (this.latencyHistory.length === 0) return 0;
        return this.latencyHistory.reduce((a, b) => a + b, 0) / this.latencyHistory.length;
    }

    /**
     * Classifies the latency into a trust tier.
     */
    classifyLatency(latencyMs) {
        if (!Number.isFinite(latencyMs) || latencyMs <= 0) return "unknown";
        if (latencyMs < PREFERRED_LATENCY_MS) return "preferred";
        if (latencyMs <= ACCEPTABLE_LATENCY_MS) return "acceptable";
        if (latencyMs <= RISKY_LATENCY_MS) return "risky";
        return "experimental";
    }

    /**
     * Calculates the maximum physical radius based on the speed of light in fiber.
     * Formula derived from Akamai/Internet research: Distance ≈ (RTT * 100) / 2.1
     */
    getPhysicsBasedRadius(latencyMs) {
        if (!Number.isFinite(latencyMs) || latencyMs <= 0) return MIN_RADIUS_KM;

        // Calculate absolute physical limit based on Round-Trip Time (RTT)
        const absolutePhysicalRadius = (latencyMs * 100.0) / INTERNET_TORTUOSITY_FACTOR;
        
        // Clamp between app minimum and global maximum
        return Math.max(MIN_RADIUS_KM, Math.min(GLOBAL_MAX_RADIUS_KM, absolutePhysicalRadius));
    }

    /**
     * Legacy method name kept for compatibility, now uses physics-based calculation.
     */
    getDynamicRadius() {
        const avgLatency = this.getAverageLatency();
        return this.getPhysicsBasedRadius(avgLatency);
    }

    /**
     * Checks if the TTL and hop count are feasible for the connection.
     */
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

    /**
     * Evaluates the full connection health for Wendy (Surgical Robot rules).
     * @param {Object} metrics - { ttl, hops, isVolunteerNode, requiresSurgicalLink }
     */
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
        const ttlCheck = this.checkTtlFeasibility(ttl, hops);

        let safetyStatus = "NORMAL";
        let action = "PROCEED";

        // Surgical Robot / Wendy Live Rules
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
            // Non-surgical (data, telemetry, async, Moon plane)
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
            ttlCheck,
            safetyStatus,
            action,
            isWendyLiveSafe: requiresSurgicalLink ? safetyStatus === "NORMAL" : true
        };
    }

    /**
     * Calculates the great-circle distance between two points on Earth.
     */
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
