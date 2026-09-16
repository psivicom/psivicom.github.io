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

print("=== PSIVI FORAGE AGENT (PICO-VRAM + INT8 COMPRESSION) ===")

mesh = VectorMesh(vram_limit=5) # Strict 5-vector VRAM limit
os.makedirs('reports', exist_ok=True)
os.makedirs('maps', exist_ok=True)

# 1. READ CRITIC'S CORRECTIONS
adjustment = 0
corrections = mesh.search("SELF-CORRECTION overestimated", top_k=1)
if corrections and corrections[0]['similarity'] > 0.4:
    if "negative adjustment" in corrections[0]['text']: adjustment = -2
    elif "positive adjustment" in corrections[0]['text']: adjustment = 2
    if adjustment != 0: print(f"[LEARNING] Applying {adjustment}h adjustment from Critic.")

# 2. FETCH WEATHER
LAT, LON = 48.48, -123.55
url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m&timezone=America%2FVancouver"
try:
    resp = requests.get(url, timeout=15)
    data = resp.json()
    times = [datetime.datetime.fromisoformat(t) for t in data['hourly']['time']]
    temps = data['hourly']['temperature_2m']
except Exception:
    now = datetime.datetime.now()
    times = [now + datetime.timedelta(hours=i) for i in range(24)]
    temps = [10 + 8 * (i/12) for i in range(12)] + [18 - 8 * ((i-12)/12) for i in range(12, 24)]

# 3. GENERATE MAP
fig, ax = plt.subplots(figsize=(10, 5))
ax.axhspan(13, 38, color='gold', alpha=0.2, label='Optimal Forage Zone')
ax.plot(times, temps, color='#0A1931', linewidth=2)
ax.set_title(f'Goldstream Forage Forecast — {datetime.date.today().isoformat()}', fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('maps/forage_forecast.png', dpi=150)

# 4. WRITE TO MESH (INT8 QUANTIZATION)
raw_optimal = sum(1 for t in temps if 13 <= t <= 38)
final_optimal = max(0, raw_optimal + adjustment)
observation = f"Goldstream forage {datetime.date.today().isoformat()}: Peak {max(temps):.1f}C. Flight window {final_optimal}h (adj {adjustment}h)."

mesh.write(observation, "forage", precision="int8") # Maximum compression for edge VRAM

# 5. DEPOSIT PHEROMONE
try:
    subprocess.run(["go", "run", "mesh.go", "flow", "forage"], check=True)
except subprocess.CalledProcessError:
    sys.exit(1)

print("[AGENT] Forage complete. VRAM preserved.")
