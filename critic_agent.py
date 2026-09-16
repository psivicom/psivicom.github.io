# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
import os
import json
import datetime
import requests
from vector_mesh import VectorMesh

print("=== PSIVI CRITIC AGENT (READING COMPRESSED VRAM) ===")
mesh = VectorMesh(vram_limit=5)

yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
memories = mesh.read_all() # Reads metadata only, saves VRAM
yesterday_pred = None

for m in memories:
    if m.get("agent") == "forage" and yesterday in m.get("timestamp", ""):
        yesterday_pred = m
        break

if not yesterday_pred:
    mesh.write("Critic ran: No historical prediction found.", "critic", precision="float16")
    exit(0)

# Fetch actual weather
LAT, LON = 48.48, -123.55
url = f"https://archive-api.open-meteo.com/v1/archive?latitude={LAT}&longitude={LON}&start_date={yesterday}&end_date={yesterday}&hourly=temperature_2m&timezone=America%2FVancouver"
try:
    resp = requests.get(url, timeout=15)
    data = resp.json()
    actual_temps = data.get('hourly', {}).get('temperature_2m', [])
    actual_optimal = sum(1 for t in actual_temps if t is not None and 13 <= t <= 38)
except Exception:
    exit(0)

# Calculate Drift
text = yesterday_pred.get("text", "")
predicted_optimal = 0
if "Flight window " in text:
    try: predicted_optimal = int(text.split("Flight window ")[1].split("h")[0])
    except: pass

error = predicted_optimal - actual_optimal
print(f"[CRITIC] Predicted: {predicted_optimal}h. Actual: {actual_optimal}h. Error: {error}h")

# Write Correction (Float16 - Sub-agents pass Float16)
if error > 2:
    correction = f"SELF-CORRECTION: Model overestimated forage window by {error} hours. Future predictions must apply a negative adjustment."
elif error < -2:
    correction = f"SELF-CORRECTION: Model underestimated forage window by {abs(error)} hours. Future predictions must apply a positive adjustment."
else:
    correction = f"SELF-CORRECTION: Model accuracy NOMINAL. Error {error}h. Maintain weights."

mesh.write(correction, "critic", precision="float16")
print("[CRITIC] Correction vector written to compressed mesh.")
