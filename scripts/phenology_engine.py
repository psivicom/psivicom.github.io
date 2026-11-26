import requests
import json
import os
from datetime import datetime, timezone

# Goldstream Apiary Sovereign Coordinates
LAT = 48.46059
LON = -123.54733
ELEVATION = 88

# Expanded Botanical Triggers (Base 5°C GDD Thresholds for Coastal BC)
BOTANY = {
    # Early Spring: Brood Stimulators
    "Alnus_rubra_Red_Alder": {"gdd_threshold": 50, "resource": "Pollen", "status": "Dormant", "note": "First protein source for spring brood rearing"},
    "Mahonia_aquifolium_Oregon_Grape": {"gdd_threshold": 100, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Early understory bloom"},
    
    # Mid Spring: The Awakening Flow
    "Acer_macrophyllum_Bigleaf_Maple": {"gdd_threshold": 150, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Major early flow"},
    "Arbutus_menziesii": {"gdd_threshold": 200, "resource": "Nectar", "status": "Dormant", "note": "Coastal fringe specialist"},
    "Gaultheria_shallon_Salal": {"gdd_threshold": 300, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Forest floor evergreen"},
    
    # Early Summer: The Heavy Engines
    "Rubus_armeniacus_Blackberry": {"gdd_threshold": 450, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Massive yield along railways and highways"},
    
    # Late Summer: The Premium Gold
    "Symphoricarpos_albus_Snowberry": {"gdd_threshold": 600, "resource": "Nectar", "status": "Dormant", "note": "Forest edge nectar"},
    "Chamerion_angustifolium_Fireweed": {"gdd_threshold": 750, "resource": "Nectar", "status": "Dormant", "note": "Bear Mountain fire scar premium yield"},
    
    # Autumn: Winter Preparation
    "Calluna_vulgaris_Heather": {"gdd_threshold": 900, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Late season forage"},
    "Hedera_helix_English_Ivy": {"gdd_threshold": 1100, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Crucial late autumn fat reserves"},
    
    # Propolis: Hive Defense & Medicine (Resin Collectors)
    "Pseudotsuga_menziesii_Douglas_Fir": {"gdd_threshold": 120, "resource": "Resin/Propolis", "status": "Dormant", "note": "Spring bud resins for antimicrobial hive defense"},
    "Thuja_plicata_Western_Redcedar": {"gdd_threshold": 150, "resource": "Resin/Propolis", "status": "Dormant", "note": "Waterproofing and antifungal resins"}
}

def fetch_open_data():
    # Open-Meteo: Free, open-science satellite/climate API
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=temperature_2m_max,temperature_2m_min&timezone=America/Vancouver"
    response = requests.get(url).json()
    return response['daily']['time'], response['daily']['temperature_2m_max'], response['daily']['temperature_2m_min']

def calculate_phenology():
    dates, t_maxs, t_mins = fetch_open_data()
    gdd_7day = 0
    base_temp = 5.0 
    
    for i in range(len(dates)):
        if t_maxs[i] is not None and t_mins[i] is not None:
            avg_temp = (t_maxs[i] + t_mins[i]) / 2
            daily_gdd = max(0, avg_temp - base_temp)
            gdd_7day += daily_gdd

    # Map thermal momentum to botanical states
    for plant, data in BOTANY.items():
        # Open-Meteo gives us a 7-day forecast. If the weekly momentum is high, things are waking up.
        if gdd_7day > 40: 
            data["status"] = f"Imminent_{data['resource']}_Flow"
        elif gdd_7day > 15:
            data["status"] = "Waking_Sap_Flow"
            
    return gdd_7day, BOTANY

def execute_sovereign_cycle():
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    gdd, botany = calculate_phenology()
    
    output_dir = "data/aether"
    os.makedirs(output_dir, exist_ok=True)
    
    state = {
        "timestamp": timestamp,
        "location": {"lat": LAT, "lon": LON, "elevation_m": ELEVATION},
        "thermal_momentum_7day_gdd": round(gdd, 2),
        "phenology_status": botany
    }
    
    with open(f"{output_dir}/phenology_state.json", "w") as f:
        json.dump(state, f, indent=2)
        
    print(f"🏛️ [WENDY] Phenology Engine crystallized at {timestamp}")
    print(f"🐝 7-Day Thermal Momentum: {round(gdd, 2)} GDD")

if __name__ == '__main__':
    execute_sovereign_cycle()
