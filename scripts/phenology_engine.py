import requests
import json
import os
import time
from datetime import datetime, timezone

# Goldstream Apiary Sovereign Coordinates
LAT = 48.46059
LON = -123.54733
ELEVATION = 88

# Expanded Botanical Triggers (Base 5°C GDD Thresholds for Coastal BC)
BOTANY = {
    "Alnus_rubra_Red_Alder": {"gdd_threshold": 50, "resource": "Pollen", "status": "Dormant", "note": "First protein source for spring brood rearing"},
    "Mahonia_aquifolium_Oregon_Grape": {"gdd_threshold": 100, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Early understory bloom"},
    "Acer_macrophyllum_Bigleaf_Maple": {"gdd_threshold": 150, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Major early flow"},
    "Arbutus_menziesii": {"gdd_threshold": 200, "resource": "Nectar", "status": "Dormant", "note": "Coastal fringe specialist"},
    "Gaultheria_shallon_Salal": {"gdd_threshold": 300, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Forest floor evergreen"},
    "Rubus_armeniacus_Blackberry": {"gdd_threshold": 450, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Massive yield along railways and highways"},
    "Symphoricarpos_albus_Snowberry": {"gdd_threshold": 600, "resource": "Nectar", "status": "Dormant", "note": "Forest edge nectar"},
    "Chamerion_angustifolium_Fireweed": {"gdd_threshold": 750, "resource": "Nectar", "status": "Dormant", "note": "Bear Mountain fire scar premium yield"},
    "Calluna_vulgaris_Heather": {"gdd_threshold": 900, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Late season forage"},
    "Hedera_helix_English_Ivy": {"gdd_threshold": 1100, "resource": "Nectar/Pollen", "status": "Dormant", "note": "Crucial late autumn fat reserves"},
    "Pseudotsuga_menziesii_Douglas_Fir": {"gdd_threshold": 120, "resource": "Resin/Propolis", "status": "Dormant", "note": "Spring bud resins for antimicrobial hive defense"},
    "Thuja_plicata_Western_Redcedar": {"gdd_threshold": 150, "resource": "Resin/Propolis", "status": "Dormant", "note": "Waterproofing and antifungal resins"}
}

def fetch_open_data():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=temperature_2m_max,temperature_2m_min&timezone=America/Vancouver"
    
    # Self-Healing Protocol: Retry up to 3 times with a 30s timeout
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['daily']['time'], data['daily']['temperature_2m_max'], data['daily']['temperature_2m_min']
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Satellite uplink attempt {attempt + 1} failed: {e}")
            time.sleep(5)
            
    print("🏛️ Open-Meteo unreachable. Preserving workflow state.")
    return [], [], []

def calculate_phenology():
    dates, t_maxs, t_mins = fetch_open_data()
    gdd_7day = 0
    base_temp = 5.0 
    
    if not dates:
        # Graceful degradation if the satellite is unreachable
        for plant in BOTANY:
            BOTANY[plant]["status"] = "Awaiting_Satellite_Uplink"
        return 0, BOTANY

    for i in range(len(dates)):
        if t_maxs[i] is not None and t_mins[i] is not None:
            avg_temp = (t_maxs[i] + t_mins[i]) / 2
            daily_gdd = max(0, avg_temp - base_temp)
            gdd_7day += daily_gdd

    for plant, data in BOTANY.items():
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
