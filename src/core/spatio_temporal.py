# src/core/spatio_temporal.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Neuro-Symbolic Spatio-Temporal Utilities (Inspired by OPERA-SDS-PCM rtc_utils)

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class SpatioTemporalEngine:
    """
    Deterministic engine for spatio-temporal reasoning.
    Offloads calendar math, orbital cycles, and time-series alignment 
    from probabilistic AI agents to hard-coded, verifiable logic.
    """
    
    @staticmethod
    def calculate_acquisition_cycle(
        base_epoch: datetime, 
        current_date: datetime, 
        cycle_days: int = 12
    ) -> Dict[str, Any]:
        """
        Calculates the exact acquisition cycle offset for satellite data.
        E.g., tracking Sentinel-1 12-day repeat cycles or shifted S1D 7-day offsets.
        """
        delta = current_date - base_epoch
        cycle_number = delta.days // cycle_days
        day_offset = delta.days % cycle_days
        
        return {
            "base_epoch": base_epoch.isoformat(),
            "current_date": current_date.isoformat(),
            "cycle_number": cycle_number,
            "day_offset": day_offset,
            "is_exact_match": day_offset == 0,
            "temporal_drift_days": day_offset
        }

    @staticmethod
    def validate_granule_metadata(metadata: Dict[str, Any]) -> bool:
        """
        Pre-flight smoke test for incoming data granules.
        Ensures required spatio-temporal fields exist before agent processing.
        """
        required_fields = ["granule_id", "acquisition_time", "bounding_box"]
        return all(field in metadata for field in required_fields)

    @staticmethod
    def align_time_series(events: List[Dict[str, Any]], window_hours: int = 24) -> List[List[Dict[str, Any]]]:
        """
        Groups spatio-temporal events into aligned windows for vector fusion.
        """
        if not events:
            return []
        
        # Sort by acquisition time
        sorted_events = sorted(events, key=lambda x: x.get("acquisition_time", ""))
        aligned_windows = []
        current_window = [sorted_events[0]]
        
        for event in sorted_events[1:]:
            t1_str = current_window[-1]["acquisition_time"].replace("Z", "+00:00")
            t2_str = event["acquisition_time"].replace("Z", "+00:00")
            
            # Handle potential missing timezone info
            if t1_str[-6:] != "+00:00" and "T" in t1_str:
                t1_str += "+00:00"
            if t2_str[-6:] != "+00:00" and "T" in t2_str:
                t2_str += "+00:00"
                
            try:
                t1 = datetime.fromisoformat(t1_str)
                t2 = datetime.fromisoformat(t2_str)
                if (t2 - t1).total_seconds() <= window_hours * 3600:
                    current_window.append(event)
                else:
                    aligned_windows.append(current_window)
                    current_window = [event]
            except ValueError:
                # Fallback: just append if parsing fails
                current_window.append(event)
                
        if current_window:
            aligned_windows.append(current_window)
            
        return aligned_windows
