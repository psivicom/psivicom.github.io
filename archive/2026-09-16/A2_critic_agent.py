# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
import os
import json
import datetime
import requests
from vector_mesh import VectorMesh

print("=== PSIVI CRITIC AGENT: CALCULATING DRIFT ===")
mesh = VectorMesh()

# 1. Find yesterday's prediction in the mesh
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
memories = mesh.read_all()
yesterday_pred = None

for m in memories:
    if m.get("agent") == "forage" and yesterday in m.get("timestamp", ""):
        yesterday_pred = m
        break

if not yesterday_pred:
    print("[CRITIC] No prediction found for yesterday. Nothing to evaluate.")
    mesh.write("Critic ran: No historical prediction found to evaluate.", "critic")
    exit(0)

# 2. Fetch ACTUAL historical weather for yesterday
LAT, LON = 48.48, -123.55
url = f"https://archive-api.open-meteo.com/v1/archive?latitude={LAT}&longitude={LON}&start_date={yesterday}&end_date={yesterday}&hourly=temperature_2m&timezone=America%2FVancouver"

try:
    resp = requests.get(url, timeout=15)
    data = resp.json()
    actual_temps = data.get('hourly', {}).get('temperature_2m', [])
    actual_optimal = sum(1 for t in actual_temps if t is not None and 13 <= t <= 38)
except Exception as e:
    print(f"[CRITIC] Archive API failed: {e}")
    mesh.write("Critic ran: Archive API unavailable.", "critic")
    exit(0)

# 3. Calculate the Error (The "Gradient")
text = yesterday_pred.get("text", "")
predicted_optimal = 0
if "Optimal bee flight window is " in text:
    try:
        predicted_optimal = int(text.split("Optimal bee flight window is ")[1].split(" ")[0])
    except:
        pass

error = predicted_optimal - actual_optimal
print(f"[CRITIC] Predicted: {predicted_optimal}h. Actual: {actual_optimal}h. Error: {error}h")

# 4. Write the Correction Vector back to the mesh
if error > 2:
    correction = f"SELF-CORRECTION: Model overestimated forage window by {error} hours. Future predictions must apply a negative adjustment."
elif error < -2:
    correction = f"SELF-CORRECTION: Model underestimated forage window by {abs(error)} hours. Future predictions must apply a positive adjustment."
else:
    correction = f"SELF-CORRECTION: Model accuracy is NOMINAL. Error is only {error} hours. Maintain current vector weights."

mesh.write(correction, "critic")
print(f"[CRITIC] Correction vector written to mesh. The AETHER has learned.")
