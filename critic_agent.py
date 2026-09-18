# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
#
# Critic Agent (Corrector) - RFC 1001 Compliant

import os
import json
import datetime
import requests
import numpy as np
from pathlib import Path

from psvc_reference import (
    encode_text, write_file, content_hash, read_file,
    PRECISION_FLOAT16
)

print("=== PSIVI CRITIC AGENT (RFC 1001 COMPLIANT) ===")

CONTAINER_DIR = Path("reports/pico_containers")
CONTAINER_DIR.mkdir(parents=True, exist_ok=True)

yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

# 1. FIND YESTERDAY'S PREDICTION
yesterday_pred = None
yesterday_vector = None

for json_file in CONTAINER_DIR.glob("*.json"):
    with open(json_file) as f:
        meta = json.load(f)
    
    if meta.get("agent") == "forage" and yesterday in meta.get("timestamp", ""):
        psvc_file = json_file.with_suffix('.psvc')
        if psvc_file.exists():
            yesterday_pred = meta
            yesterday_vector = read_file(psvc_file)
            break

if not yesterday_pred:
    print("[CRITIC] No prediction found for yesterday.")
    exit(0)

# 2. FETCH ACTUAL WEATHER
LAT, LON = 48.48, -123.55
url = f"https://archive-api.open-meteo.com/v1/archive?latitude={LAT}&longitude={LON}&start_date={yesterday}&end_date={yesterday}&hourly=temperature_2m&timezone=America%2FVancouver"

try:
    resp = requests.get(url, timeout=15)
    data = resp.json()
    actual_temps = data.get('hourly', {}).get('temperature_2m', [])
    actual_optimal = sum(1 for t in actual_temps if t is not None and 13 <= t <= 38)
except Exception as e:
    print(f"[CRITIC] Archive API failed: {e}")
    exit(0)

# 3. CALCULATE DRIFT
text = yesterday_pred.get("text", "")
predicted_optimal = 0
if "Flight window " in text:
    try:
        predicted_optimal = int(text.split("Flight window ")[1].split("h")[0])
    except:
        pass

error = predicted_optimal - actual_optimal
print(f"[CRITIC] Predicted: {predicted_optimal}h. Actual: {actual_optimal}h. Error: {error}h")

# 4. WRITE CORRECTION USING CANONICAL LIBRARY
if error > 2:
    correction = f"SELF-CORRECTION: Model overestimated forage window by {error} hours. Future predictions must apply a negative adjustment."
elif error < -2:
    correction = f"SELF-CORRECTION: Model underestimated forage window by {abs(error)} hours. Future predictions must apply a positive adjustment."
else:
    correction = f"SELF-CORRECTION: Model accuracy NOMINAL. Error {error}h. Maintain weights."

correction_vector = encode_text(correction)
chash = content_hash(correction_vector)
output_path = CONTAINER_DIR / f"{chash}.psvc"

write_file(correction_vector, output_path, precision=PRECISION_FLOAT16)

# 5. WRITE SIDECAR
sidecar_path = output_path.with_suffix('.json')
with open(sidecar_path, 'w') as f:
    json.dump({
        "text": correction,
        "agent": "critic",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "type": "correction",
        "error_hours": error
    }, f, indent=2)

print(f"[CRITIC] Correction sealed: {chash}.psvc")
