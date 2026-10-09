# src/mesh/geo_intelligence.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Geo-Intelligence Engine: Latency-Aware Network Routing.
Ported from legacy JS to enforce sovereign Python standards, float32 precision,
and Zulu temporal tracking for robotic and mesh network feasibility.
"""

import math
import logging
import numpy as np
from typing import Dict, Any, List
from collections import deque
from src.core.zulu_clock import get_zulu_timestamp_ms

logger = logging.getLogger("GEO_INTELLIGENCE")

# --- PHYSICS CONSTANTS (Based on Internet Fiber Research) ---
EARTH_RADIUS_KM = 6371.0
INTERNET_TORTUOSITY_FACTOR = 2.1

# --- APP BOUNDARIES ---
MIN_RADIUS_KM = 50.0
GLOBAL_MAX_RADIUS_KM = 2000.0 

# --- LATENCY TIERS (ms) ---
PREFERRED_LATENCY_MS = 10.0
ACCEPTABLE_LATENCY_MS = 50.0
RISKY_LATENCY_MS = 200.0

# --- SURGICAL / WENDY LIVE CONSTRAINTS ---
SURGICAL_MAX_HOPS = 3
RECOMMENDED_TTL = 128

class GeoIntelligenceEngine:
    def __init__(self, max_history: int = 50):
        self.latency_history: deque = deque(maxlen=max_history)
        logger.info("🌍 Geo-Intelligence Engine initialized.")

    def record_latency(self, latency_ms: float):
        """Records a latency sample for rolling average calculation."""
        if isinstance(latency_ms, (int, float)) and latency_ms > 0:
            self.latency_history.append(np.float32(latency_ms))

    def get_average_latency(self) -> float:
        if not self.latency_history:
            return 0.0
        return float(np.mean(list(self.latency_history)))

    def classify_latency(self, latency_ms: float) -> str:
        if latency_ms <= 0:
            return "unknown"
        if latency_ms < PREFERRED_LATENCY_MS:
            return "preferred"
        if latency_ms <= ACCEPTABLE_LATENCY_MS:
            return "acceptable"
        if latency_ms <= RISKY_LATENCY_MS:
            return "risky"
        return "experimental"

    def get_physics_based_radius(self, latency_ms: float) -> float:
        if latency_ms <= 0:
            return MIN_RADIUS_KM
        absolute_physical_radius = (latency_ms * 100.0) / INTERNET_TORTUOSITY_FACTOR
        return float(np.clip(absolute_physical_radius, MIN_RADIUS_KM, GLOBAL_MAX_RADIUS_KM))

    def get_operational_search_radius(self, avg_latency_ms: float) -> float:
        target_latency_ms = 10.0
        if avg_latency_ms <= 0:
            return GLOBAL_MAX_RADIUS_KM
        congestion_factor = min(1.0, target_latency_ms / max(avg_latency_ms, 1.0))
        desired_radius = GLOBAL_MAX_RADIUS_KM * congestion_factor
        return float(np.clip(desired_radius, MIN_RADIUS_KM, GLOBAL_MAX_RADIUS_KM))

    def check_ttl_feasibility(self, initial_ttl: int, observed_hops: int) -> Dict[str, Any]:
        remaining_hops = initial_ttl - observed_hops
        if remaining_hops <= 0:
            return {"ok": False, "reason": "TTL_EXCEEDED", "remaining_hops": remaining_hops}
        if remaining_hops < 5:
            return {"ok": True, "warning": "LOW_TTL_MARGIN", "remaining_hops": remaining_hops}
        return {"ok": True, "reason": "HEALTHY", "remaining_hops": remaining_hops}

    def evaluate_connection(self, ttl: int = RECOMMENDED_TTL, observed_hops: int = 0, 
                            is_volunteer_node: bool = False, requires_surgical_link: bool = False) -> Dict[str, Any]:
        """Evaluates if a mesh connection is safe for Wendy's operations."""
        latency_ms = self.get_average_latency()
        trust = self.classify_latency(latency_ms)
        radius_km = self.get_physics_based_radius(latency_ms)
        operational_radius_km = self.get_operational_search_radius(latency_ms)
        ttl_check = self.check_ttl_feasibility(ttl, observed_hops)

        safety_status = "NORMAL"
        action = "PROCEED"

        if requires_surgical_link:
            if trust in ["risky", "experimental", "unknown"]:
                safety_status = "UNSAFE_LATENCY_FOR_LIVE"
                action = "SAFE_HOLD_OR_REJECT"
            elif observed_hops > SURGICAL_MAX_HOPS:
                safety_status = "TOO_MANY_HOPS_FOR_LIVE"
                action = "SAFE_HOLD_OR_REJECT"
            elif is_volunteer_node:
                safety_status = "VOLUNTEER_NODE_NOT_TRUSTED_FOR_LIVE"
                action = "SAFE_HOLD_OR_REJECT"
            elif not ttl_check["ok"]:
                safety_status = "TTL_FEASIBILITY_FAILED"
                action = "SAFE_HOLD_OR_REJECT"
        else:
            if trust == "experimental":
                action = "ALLOW_ASYNC_ONLY"
            elif not ttl_check["ok"]:
                action = "RETRY_OR_QUEUE"

        return {
            "timestamp": get_zulu_timestamp_ms(),
            "latency_ms": latency_ms,
            "trust": trust,
            "radius_km": radius_km,
            "operational_radius_km": operational_radius_km,
            "ttl_check": ttl_check,
            "safety_status": safety_status,
            "action": action,
            "is_wendy_live_safe": safety_status == "NORMAL" if requires_surgical_link else True
        }

    @staticmethod
    def haversine_distance(point1: Dict[str, float], point2: Dict[str, float]) -> float:
        """Calculates the great-circle distance between two points on Earth in KM."""
        def to_rad(deg): return deg * (math.pi / 180.0)
        
        d_lat = to_rad(point2["lat"] - point1["lat"])
        d_lon = to_rad(point2["lon"] - point1["lon"])
        
        a = math.sin(d_lat / 2) ** 2 + \
            math.cos(to_rad(point1["lat"])) * math.cos(to_rad(point2["lat"])) * \
            math.sin(d_lon / 2) ** 2
            
        return float(EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))
