# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import subprocess
import sys
import os

from vector_mesh import VectorMesh

print("=== PSIVI FORAGE AGENT + SELF-IMPROVEMENT LOOP ===")

# --- 1. INITIALIZE VECTOR MESH ---
mesh = VectorMesh()
os.makedirs('reports', exist_ok=True)
os.makedirs('maps', exist_ok=True)

# --- 2. READ CRITIC'S CORRECTIONS (The Feedback Loop) ---
adjustment = 0
corrections = mesh.search("SELF-CORRECTION overestimated", top_k=1)
if corrections and corrections[0]['similarity'] > 0.4:
    if "negative adjustment" in corrections[0]['text']:
        adjustment = -2
        print(f"[LEARNING] Applying negative adjustment based on Critic feedback.")
    elif "positive adjustment" in corrections[0]['text']:
        adjustment = 2
        print(f"[LEARNING] Applying positive adjustment based on Critic feedback.")

# --- 3. FETCH WEATHER DATA ---
LAT, LON = 48.48, -123.55
url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m&timezone=America%2FVancouver"

try:
    resp = requests.get(url, timeout=15)
    data = resp.json()
    times = [datetime.datetime.fromisoformat(t) for t in data['hourly']['time']]
    temps = data['hourly']['temperature_2m']
except Exception as e:
    print(f"[AGENT] API Fallback: {e}")
    now = datetime.datetime.now()
    times = [now + datetime.timedelta(hours=i) for i in range(24)]
    temps = [10 + 8 * (i/12) for i in range(12)] + [18 - 8 * ((i-12)/12) for i in range(12, 24)]

# --- 4. GENERATE MAP & CALCULATE ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.axhspan(13, 38, color='gold', alpha=0.2, label='Optimal Forage Zone (13°C - 38°C)')
ax.plot(times, temps, color='#0A1931', linewidth=2, label='Forecast Temp (°C)')
ax.set_title(f'Goldstream Forage Forecast — {datetime.date.today().isoformat()}', fontsize=14, fontweight='bold')
ax.set_ylabel('Temperature (°C)')
ax.set_xlabel('Hour (Local Time)')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.legend(loc='upper left')
ax.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('maps/forage_forecast.png', dpi=150)

raw_optimal_hours = sum(1 for t in temps if 13 <= t <= 38)
# APPLY THE LEARNED ADJUSTMENT
final_optimal_hours = max(0, raw_optimal_hours + adjustment)

# --- 5. WRITE TO VECTOR MESH ---
observation = (
    f"Goldstream forage forecast for {datetime.date.today().isoformat()}: "
    f"Peak temp {max(temps):.1f}C. "
    f"Optimal bee flight window is {final_optimal_hours} hours (adjusted by {adjustment}h based on Critic)."
)
mesh.write(observation, "forage")

# --- 6. DEPOSIT PHEROMONE ---
try:
    subprocess.run(["go", "run", "mesh.go", "flow", "forage"], check=True)
except subprocess.CalledProcessError as e:
    print(f"[AGENT] VANGUARD FAILED: {e}")
    sys.exit(1)

print("[AGENT] Self-improving Forage Agent complete.")
