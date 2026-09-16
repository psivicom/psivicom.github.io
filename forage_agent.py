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

print("=== PSIVI FORAGE AGENT + VECTOR MEMORY AWAKENING ===")

# --- 1. INITIALIZE VECTOR MESH ---
mesh = VectorMesh()
os.makedirs('reports', exist_ok=True)
os.makedirs('maps', exist_ok=True)

# --- 2. FETCH WEATHER DATA ---
LAT, LON = 48.48, -123.55
url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m&timezone=America%2FVancouver"

try:
    resp = requests.get(url, timeout=15)
    data = resp.json()
    times = [datetime.datetime.fromisoformat(t) for t in data['hourly']['time']]
    temps = data['hourly']['temperature_2m']
    print(f"[AGENT] Fetched {len(temps)} hours of weather data for Goldstream.")
except Exception as e:
    print(f"[AGENT] WEATHER API FAILED: {e}. Using fallback data.")
    now = datetime.datetime.now()
    times = [now + datetime.timedelta(hours=i) for i in range(24)]
    temps = [10 + 8 * (i/12) for i in range(12)] + [18 - 8 * ((i-12)/12) for i in range(12, 24)]

# --- 3. GENERATE MAP ---
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

map_path = 'maps/forage_forecast.png'
plt.savefig(map_path, dpi=150)
print(f"[AGENT] Map saved to {map_path}")

# --- 4. WRITE REPORT ---
os.makedirs('reports', exist_ok=True)
report_path = 'reports/forage_log.md'
with open(report_path, 'w') as f:
    f.write(f"# Forage Forecast Log\n\n")
    f.write(f"**Date:** {datetime.date.today().isoformat()}\n")
    f.write(f"**Location:** Goldstream, Langford BC ({LAT}, {LON})\n\n")
    f.write(f"## Analysis\n")
    f.write(f"- **Peak Temp:** {max(temps):.1f}°C\n")
    f.write(f"- **Min Temp:** {min(temps):.1f}°C\n")
    f.write(f"- **Hours in Optimal Zone:** {sum(1 for t in temps if 13 <= t <= 38)} hours\n\n")
    f.write(f"## Methodology\n")
    f.write(f"Data sourced from Open-Meteo API. Forage window defined as 13°C–38°C for *Apis mellifera* flight activity.\n")
print(f"[AGENT] Report saved to {report_path}")

# --- 5. WRITE TO VECTOR MESH (Real 4096-dim vector) ---
optimal_hours = sum(1 for t in temps if 13 <= t <= 38)
observation = (
    f"Goldstream forage forecast for {datetime.date.today().isoformat()}: "
    f"Peak temp {max(temps):.1f}C, min temp {min(temps):.1f}C. "
    f"Optimal bee flight window is {optimal_hours} hours. "
    f"Forage conditions {'favorable' if optimal_hours > 8 else 'limited'}."
)

vector_hash = mesh.write(observation, "forage")
print(f"[AGENT] Vector memory stored: {vector_hash}")

# --- 6. QUERY THE MESH (Demonstrate routing) ---
query = "What is the pollinator flight window today?"
results = mesh.search(query, top_k=1)
if results:
    print(f"[ROUTER] Query: '{query}'")
    print(f"[ROUTER] Best match: {results[0]['agent']} (similarity: {results[0]['similarity']:.4f})")
    print(f"[ROUTER] Content: {results[0]['text'][:100]}...")

# --- 7. DEPOSIT PHEROMONE TO VANGUARD ---
try:
    subprocess.run(["go", "run", "mesh.go", "flow", "forage"], check=True)
    print("[AGENT] Forage node active in mesh.")
except subprocess.CalledProcessError as e:
    print(f"[AGENT] VANGUARD FAILED: {e}")
    sys.exit(1)

print("[AGENT] Forage Agent complete.")
