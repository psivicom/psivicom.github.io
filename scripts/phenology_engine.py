import requests
import json
import os
from datetime import datetime, timezone

# Goldstream Apiary Sovereign Coordinates
LAT = 48.46059
LON = -123.54733
ELEVATION = 88

# Botanical Triggers (Base 5°C GDD Thresholds for Coastal BC)
BOTANY = {
    "Arbutus_menziesii": {"gdd_threshold": 150, "status": "Dormant"},
    "Acer_macrophyllum": {"gdd_threshold": 200, "status": "Dormant"},
    "Fireweed_Bear_Mtn": {"gdd_threshold": 650, "status": "Dormant"}
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
        if gdd_7day > 15: 
            data["status"] = "Active_Nectar_Flow_Potential"
        elif gdd_7day > 5:
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
