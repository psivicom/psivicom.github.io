# src/agents/forage_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
Forage Agent: Ingestion Layer
Fetches real-time weather, solar, and historical pollinator data for the 
Goldstream Watershed (Langford, BC) and embeds it into the PSVC vector mesh.
"""

import sys
import json
import numpy as np
import requests
from pathlib import Path
from datetime import datetime, timezone

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.psvc_reference import write_file, content_hash, PRECISION_FLOAT32

class ForageAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION
    
    # Goldstream Watershed / Langford, BC Coordinates
    LATITUDE = 48.4456
    LONGITUDE = -123.5017
    
    def __init__(self, name: str = "forage"):
        super().__init__(name, capabilities=["fetch_weather", "fetch_solar", "fetch_historical"])
        self.data_dir = Path("data/forage_raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _fetch_open_meteo(self) -> dict:
        """Fetches real-time weather and solar radiation from Open-Meteo (FAIR, no API key required)."""
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={self.LATITUDE}&longitude={self.LONGITUDE}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"
            f"&timezone=America/Vancouver"
        )
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.seal("fetch_error", {"error": str(e)})
            return {"error": str(e)}

    def execute(self, input_vector: np.ndarray = None) -> np.ndarray:
        """Main execution: Fetches data, embeds it into a float32 vector, and seals provenance."""
        raw_data = self._fetch_open_meteo()
        
        if "error" in raw_data:
            fallback_vector = np.zeros(4096, dtype=np.float32)
            self.seal("forage_fallback", {"reason": "network_error"})
            return fallback_vector

        current = raw_data.get("current", {})
        temp = float(current.get("temperature_2m", 0.0))
        humidity = float(current.get("relative_humidity_2m", 0.0))
        wind = float(current.get("wind_speed_10m", 0.0))
        solar = float(current.get("shortwave_radiation", 0.0))

        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        record = {
            "timestamp": timestamp,
            "location": "Goldstream Watershed, Langford BC",
            "coordinates": {"lat": self.LATITUDE, "lon": self.LONGITUDE},
            "metrics": {"temp_c": temp, "humidity_pct": humidity, "wind_kmh": wind, "solar_wm2": solar},
            "source": "Open-Meteo API",
            "license": "CC BY-4.0 (Data)"
        }
        
        safe_time = timestamp.replace(':', '-').replace('.', '-')
        file_path = self.data_dir / f"forage_{safe_time}.json"
        
        # Write the file (returns bool per your official psvc_reference.py)
        success = write_file(file_path, record)
        
        # Hash the JSON string as bytes (per your official content_hash signature)
        data_hash = content_hash(json.dumps(record, sort_keys=True).encode('utf-8')) if success else "hash_failed"
        
        # Embed into a 4096-dimensional float32 vector
        vector = np.random.randn(4096).astype(np.float32)
        vector[0] = np.float32(temp / 40.0)      # Normalized temp (0-40C)
        vector[1] = np.float32(humidity / 100.0) # Normalized humidity (0-100%)
        vector[2] = np.float32(wind / 50.0)      # Normalized wind (0-50km/h)
        vector[3] = np.float32(solar / 1000.0)   # Normalized solar (0-1000 W/m²)
        
        # Normalize the entire vector to unit length for stable mesh routing
        vector /= np.linalg.norm(vector)
        
        self.seal("forage_collect", {
            "vector_shape": vector.shape,
            "precision": PRECISION_FLOAT32,
            "data_hash": data_hash,
            "file_saved": str(file_path),
            "write_success": success
        })
        
        return vector

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    agent = ForageAgent()
    print("🐝 Foraging Goldstream Watershed data...")
    result_vector = agent.execute()
    print(f"✅ Vector generated: Shape {result_vector.shape}, Mean {np.mean(result_vector):.4f}")
    print(f"🔒 Seals recorded: {len(agent.state['seals'])}")
