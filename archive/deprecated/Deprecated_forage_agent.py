# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
#
# Forage Agent (Observer) - RFC 1001 Compliant

import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import subprocess
import sys
import os
import json
import numpy as np

from psvc_reference import (
    encode_text, seal, write_file, content_hash,
    PRECISION_INT8, PRECISION_FLOAT16
)

print("=== PSIVI FORAGE AGENT (RFC 1001 COMPLIANT) ===")

CONTAINER_DIR = "reports/pico_containers"
os.makedirs(CONTAINER_DIR, exist_ok=True)
os.makedirs('maps', exist_ok=True)

# 1. FETCH WEATHER DATA
LAT, LON = 48.48, -123.55
url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m&timezone=America%2FVancouver"

try:
    resp = requests.get(url, timeout=15)
    data = resp.json()
    times = [datetime.datetime.fromisoformat(t) for t in data['hourly']['time']]
    temps = data['hourly']['temperature_2m']
except Exception as e:
    print(f"[FORAGE] API Fallback: {e}")
    now = datetime.datetime.now()
    times = [now + datetime.timedelta(hours=i) for i in range(24)]
    temps = [10 + 8 * (i/12) for i in range(12)] + [18 - 8 * ((i-12)/12) for i in range(12, 24)]

# 2. GENERATE MAP
fig, ax = plt.subplots(figsize=(10, 5))
ax.axhspan(13, 38, color='gold', alpha=0.2, label='Optimal Forage Zone')
ax.plot(times, temps, color='#0A1931', linewidth=2)
ax.set_title(f'Goldstream Forage Forecast — {datetime.date.today().isoformat()}', fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('maps/forage_forecast.png', dpi=150)

# 3. CALCULATE FORAGE WINDOW
optimal_hours = sum(1 for t in temps if 13 <= t <= 38)
observation = f"Goldstream forage {datetime.date.today().isoformat()}: Peak {max(temps):.1f}C. Flight window {optimal_hours}h."

# 4. ENCODE AS VECTOR AND SEAL USING CANONICAL LIBRARY
vector = encode_text(observation)
chash = content_hash(vector)
output_path = os.path.join(CONTAINER_DIR, f"{chash}.psvc")

write_file(vector, output_path, precision=PRECISION_INT8)

# 5. WRITE SIDECAR METADATA
sidecar_path = output_path.replace('.psvc', '.json')
with open(sidecar_path, 'w') as f:
    json.dump({
        "text": observation,
        "agent": "forage",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "type": "observation"
    }, f, indent=2)

print(f"[FORAGE] Observation sealed: {chash}.psvc")
print(f"[FORAGE] Flight window: {optimal_hours} hours")

# 6. DEPOSIT PHEROMONE (Go mesh orchestrator - allowed by Governor)
try:
    subprocess.run(["go", "run", "mesh.go", "flow", "forage"], check=True)
except subprocess.CalledProcessError as e:
    print(f"[FORAGE] VANGUARD FAILED: {e}")
    sys.exit(1)

print("[FORAGE] Complete.")
