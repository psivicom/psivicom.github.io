import os
import json
import requests
import datetime
from pathlib import Path

print("=== PSIVI MESH SYNTHESIZER AWAKENING ===")

# 1. READ ALL MESH MEMORIES
memories = []
for file in Path("reports").glob("*_memory.json"):
    with open(file) as f:
        memories.append(json.load(f))

print(f"[SYNTHESIZER] Found {len(memories)} memories in mesh")

# 2. QUERY EXTERNAL DATA SOURCES
LAT, LON = 48.48, -123.55

# Get soil moisture from NASA SMAP (via Open-Meteo as proxy)
try:
    resp = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=soil_moisture_0_to_7cm&timezone=America%2FVancouver",
        timeout=10
    )
    soil_data = resp.json()
    soil_moisture = soil_data.get('daily', {}).get('soil_moisture_0_to_7cm', [0])[0]
    print(f"[SYNTHESIZER] Soil moisture: {soil_moisture} m³/m³")
except:
    soil_moisture = None

# 3. GENERATE SYNTHESIS
synthesis_date = datetime.date.today().isoformat()
synthesis_text = f"""# Weekly Scientific Synthesis — {synthesis_date}

## Environmental Context
- **Location:** Goldstream Watershed, Langford BC ({LAT}, {LON})
- **Soil Moisture (0-7cm):** {soil_moisture or 'N/A'} m³/m³

## Agent Observations
"""

for mem in memories[-5:]:  # Last 5 memories
    synthesis_text += f"- **{mem.get('agent', 'Unknown')}**: {mem.get('text', 'No data')}\n"

synthesis_text += f"""
## Synthesized Insight
"""

if soil_moisture and soil_moisture > 0.3:
    synthesis_text += "Soil moisture is elevated. Expect increased bloom activity in the next 3-5 days based on historical patterns.\n"
elif soil_moisture and soil_moisture < 0.15:
    synthesis_text += "Soil moisture is low. Pollinator forage may be limited to irrigated areas.\n"
else:
    synthesis_text += "Environmental conditions are within normal range. Continue standard monitoring.\n"

synthesis_text += f"""
## Recommended Actions
- Monitor south-facing Garry oak meadow fragments for early bloom
- Check hive weight trends against forage availability
- Schedule next transect for optimal flight window (13-38°C)
"""

# 4. WRITE SYNTHESIS REPORT
os.makedirs("reports", exist_ok=True)
synthesis_path = f"reports/synthesis_{synthesis_date}.md"
with open(synthesis_path, 'w') as f:
    f.write(synthesis_text)

print(f"[SYNTHESIZER] Synthesis written to {synthesis_path}")

# 5. UPDATE WEBSITE MAIN PAGE
try:
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # Find where to insert the insight (after the About section)
    insert_point = html.find('<!-- BOTTOM AETHER LIVE -->')
    if insert_point > 0:
        insight_section = f"""
<!-- LATEST MESH SYNTHESIS -->
<section id="synthesis" class="section" style="margin-top:32px;padding:20px;background:#fafafa;border-radius:12px;border-left:4px solid #00D4FF">
<h3 style="margin:0 0 12px 0;font-size:18px;color:#0A1931">Latest Mesh Synthesis</h3>
<p style="margin:0;font-size:13px;line-height:1.6">
<strong>Date:</strong> {synthesis_date}<br>
<strong>Soil Moisture:</strong> {soil_moisture or 'N/A'} m³/m³<br>
<strong>Insight:</strong> {"Elevated moisture — expect bloom activity" if soil_moisture and soil_moisture > 0.3 else "Normal conditions — standard monitoring"}<br>
<strong>Full Report:</strong> <a href="{synthesis_path}" style="color:#0A1931">View synthesis report →</a>
</p>
</section>

"""
        html = html[:insert_point] + insight_section + html[insert_point:]
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("[SYNTHESIZER] Updated index.html with latest insight")
except Exception as e:
    print(f"[SYNTHESIZER] Could not update index.html: {e}")

# 6. WRITE SYNTHESIS VECTOR TO MESH
synthesis_memory = {
    "text": f"Synthesis for {synthesis_date}: {synthesis_text.split('## Synthesized Insight')[1].split('##')[0].strip()[:200]}",
    "agent": "synthesizer",
    "timestamp": datetime.datetime.utcnow().isoformat()
}

with open(f"reports/{synthesis_date}_synthesizer_memory.json", 'w') as f:
    json.dump(synthesis_memory, f, indent=2)

print("[SYNTHESIZER] Synthesis vector written to mesh")
print("[SYNTHESIZER] Complete")
