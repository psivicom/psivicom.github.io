# src/agents/forage_agent.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Production ForageAgent with REAL API integrations:
- Open-Meteo (weather data): https://open-meteo.com/
- NASA POWER (solar/agricultural): https://power.larc.nasa.gov/

Both APIs are FREE, no API key required.
"""

import logging
import time
from typing import Dict, Any, List, Optional
import numpy as np
import torch

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.http_client import ProductionHTTPClient
from psvc_containers import build_psvc_from_tensor

logger = logging.getLogger(__name__)


class ForageAgent(BaseAgent):
    """
    Production ForageAgent that fetches real weather and environmental data.
    """
    LAYER = AgentLayer.INGESTION

    def __init__(
        self,
        name: str = "forage_agent",
        open_meteo_timeout: float = 30.0,
        nasa_power_timeout: float = 30.0,
        rate_limit_per_second: float = 5.0
    ):
        super().__init__(name=name, capabilities=["fetch_weather", "fetch_solar", "fetch_historical"])

        # Real HTTP clients with production safeguards
        self.open_meteo = ProductionHTTPClient(
            base_url="https://api.open-meteo.com/v1",
            timeout=open_meteo_timeout,
            rate_limit_per_second=rate_limit_per_second,
            headers={"Accept": "application/json"}
        )

        self.nasa_power = ProductionHTTPClient(
            base_url="https://power.larc.nasa.gov/api/temporal/daily/point",
            timeout=nasa_power_timeout,
            rate_limit_per_second=rate_limit_per_second,
            headers={"Accept": "application/json"}
        )

        logger.info(f"ForageAgent initialized: {self.agent_id}")

    def fetch_weather(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Fetch real weather forecast from Open-Meteo API.
        
        Args:
            latitude: Location latitude (-90 to 90)
            longitude: Location longitude (-180 to 180)
            days: Forecast days (1-16)
            
        Returns:
            Dictionary with temperature, humidity, wind, precipitation
        """
        logger.info(f"Fetching weather for ({latitude}, {longitude}), {days} days")

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,relative_humidity_2m_max",
            "timezone": "auto",
            "forecast_days": min(days, 16)
        }

        data = self.open_meteo.get("forecast", params=params)

        # Validate response structure
        if "daily" not in data:
            raise ValueError(f"Invalid Open-Meteo response: {data}")

        result = {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "daily": data["daily"],
            "fetched_at": time.time()
        }

        logger.info(f"Weather fetched: {len(data['daily'].get('time', []))} days")
        return result

    def fetch_solar(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Fetch real solar/agricultural data from NASA POWER API.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: YYYYMMDD format
            end_date: YYYYMMDD format
            
        Returns:
            Dictionary with solar radiation, temperature, humidity
        """
        logger.info(f"Fetching NASA POWER data for ({latitude}, {longitude})")

        params = {
            "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M,PRECTOTCORR",
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }

        data = self.nasa_power.get("", params=params)

        # Validate response
        if "parameters" not in data:
            raise ValueError(f"Invalid NASA POWER response: {data}")

        result = {
            "latitude": latitude,
            "longitude": longitude,
            "parameters": data["parameters"],
            "fetched_at": time.time()
        }

        logger.info(f"NASA POWER data fetched: {len(data['parameters'])} parameters")
        return result

    def fetch_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Fetch historical weather data from Open-Meteo Archive API.
        """
        logger.info(f"Fetching historical weather for ({latitude}, {longitude})")

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum"
        }

        data = self.open_meteo.get("archive", params=params)

        if "daily" not in data:
            raise ValueError(f"Invalid Open-Meteo Archive response: {data}")

        return {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "daily": data["daily"],
            "fetched_at": time.time()
        }

    def embed_weather_data(self, weather_data: Dict[str, Any]) -> torch.Tensor:
        """
        Convert weather data to tensor representation for mesh processing.
        """
        daily = weather_data.get("daily", {})

        # Extract numeric arrays
        temp_max = np.array(daily.get("temperature_2m_max", []), dtype=np.float32)
        temp_min = np.array(daily.get("temperature_2m_min", []), dtype=np.float32)
        precip = np.array(daily.get("precipitation_sum", []), dtype=np.float32)
        wind = np.array(daily.get("windspeed_10m_max", []), dtype=np.float32)
        humidity = np.array(daily.get("relative_humidity_2m_max", []), dtype=np.float32)

        # Stack into feature matrix [days, features]
        features = np.stack([temp_max, temp_min, precip, wind, humidity], axis=1)

        # Normalize to [-1, 1] range
        features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)

        # Flatten to 1D vector
        vector = torch.tensor(features.flatten(), dtype=torch.float32)

        logger.info(f"Weather embedded: {vector.shape[0]} dimensions")
        return vector

    def execute(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> bytes:
        """
        Main execution: fetch weather, embed, seal into .psvc container.
        """
        # 1. Fetch real data
        weather_data = self.fetch_weather(latitude, longitude, days)

        # 2. Embed to tensor
        vector = self.embed_weather_data(weather_data)

        # 3. Seal operation
        receipt = self.seal(
            operation="fetch_and_embed_weather",
            payload={"latitude": latitude, "longitude": longitude, "days": days}
        )

        # 4. Build .psvc container
        container = build_psvc_from_tensor(
            tensor=vector,
            operation="weather_embedding",
            agent_id=self.agent_id,
            layer=self.LAYER.name,
            parent_receipt_hash=receipt.payload_hash,
            content_type="weather_vector"
        )

        from psvc_containers import serialize_psvc
        return serialize_psvc(container)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Real-world usage: Fetch weather for Montreal and create .psvc container.
    """
    logging.basicConfig(level=logging.INFO)

    agent = ForageAgent()

    # Fetch real weather data for Montreal
    print("\n=== Fetching Real Weather Data ===")
    container_bytes = agent.execute(
        latitude=45.5017,  # Montreal
        longitude=-73.5673,
        days=7
    )

    print(f"✓ Container created: {len(container_bytes)} bytes")

    # Verify the container
    from psvc_containers import deserialize_psvc, verify_container
    container = deserialize_psvc(container_bytes)
    verification = verify_container(container)

    print(f"✓ Verification: {verification}")
    print(f"✓ Agent: {container.receipt.agent_id}")
    print(f"✓ Operation: {container.receipt.operation}")
    print(f"✓ Tensor shape: {container.payload.tensor_shape}")

    # Check metrics
    print(f"\n=== HTTP Client Metrics ===")
    print(f"Open-Meteo: {agent.open_meteo.get_metrics()}")
