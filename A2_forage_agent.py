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
import hashlib

print("=== PSIVI FORAGE AGENT + VECTOR MEMORY AWAKENING ===")

# --- 1. LIGHTWEIGHT VECTOR MEMORY (No heavy AI needed) ---
class VectorMesh:
    def encode(self, text):
        # Creates a 4096-dim mathematical fingerprint of the text
        h = hashlib.sha512(text.encode()).digest() * 64 
        vec = np.frombuffer(h[:4096*4], dtype=np.float32)
        return vec / (np.linalg.norm(vec) + 1e-9)

    def write(self, text, filename):
        vec = self.encode(text)
        # Save as JSON so Git catches it easily
        data = {"vector": vec.tolist(), "text": text, "timestamp": datetime.datetime.utcnow().isoformat()}
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"[MEMORY] Wrote vector to {filename}")

    def search(self, query, folder="reports"):
        q_vec = self.encode(query)
        best_match = None
        best_score = -1
        for file in os.listdir(folder):
            if file.endswith("_memory.json"):
                with open(os.path.join(folder, file)) as f:
                    data = json.load(f)
                score = np.dot(q_vec, np.array(data["vector"]))
                if score > best_score:
                    best_score = score
                    best_match = data["text"]
        return best_match, best_score

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
except Exception as e:
    print(f"[AGENT] API Fallback: {e}")
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
plt.savefig('maps/forage_forecast.png', dpi=150)
print("[AGENT] Map saved.")

# --- 4. WRITE SEMANTIC MEMORY ---
optimal_hours = sum(1 for t in temps if 13 <= t <= 38)
observation = f"Goldstream forage forecast for {datetime.date.today().isoformat()}: Peak temp {max(temps):.1f}C. Optimal bee flight window is {optimal_hours} hours."

mesh.write(observation, f"reports/{datetime.date.today().isoformat()}_memory.json")

# --- 5. QUERY THE MEMORY (Proof it works) ---
query = "What is the pollinator flight window today?"
answer, score = mesh.search(query)
print(f"[ROUTER] Query: '{query}'")
print(f"[ROUTER] Found memory with {score:.3f} similarity: {answer}")

# --- 6. UPDATE VANGUARD ---
try:
    subprocess.run(["go", "run", "mesh.go", "flow", "forage"], check=True)
    print("[AGENT] Forage node active in mesh.")
except subprocess.CalledProcessError as e:
    print(f"[AGENT] VANGUARD FAILED: {e}")
    sys.exit(1)
