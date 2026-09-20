# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
import requests
import subprocess
import sys

print("=== PSIVI LIDAR AGENT AWAKENING ===")

# Goldstream Watershed Bounding Box
MINX, MINY = -123.65, 48.45
MAXX, MAXY = -123.45, 48.55

print(f"[AGENT] Querying OpenTopography for Goldstream...")

url = "https://portal.opentopography.org/API/otCatalog"
params = {
    "minx": MINX, "miny": MINY,
    "maxx": MAXX, "maxy": MAXY,
    "outputFormat": "json",
    "include_federated": "false"
}

try:
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    datasets = data.get("Datasets", {}).get("Dataset", [])
    if not isinstance(datasets, list):
        datasets = [datasets]
    print(f"[AGENT] SUCCESS: Found {len(datasets)} LiDAR datasets in Goldstream corridor.")
except Exception as e:
    print(f"[AGENT] API FALLBACK: {e}")
    print("[AGENT] Proceeding with simulated analysis.")

print("[AGENT] Depositing pheromone...")

try:
    subprocess.run(["go", "run", "mesh.go", "flow", "lidar"], check=True)
    print("[AGENT] LiDAR node active.")
except subprocess.CalledProcessError as e:
    print(f"[AGENT] FAILURE: {e}")
    sys.exit(1)
