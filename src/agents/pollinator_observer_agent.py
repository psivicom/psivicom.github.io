# src/agents/pollinator_observer_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from base.base_agent import BaseAgent, AgentLayer

logger = logging.getLogger(__name__)

class PollinatorObserverAgent(BaseAgent):
    """
    Monitors for new pollinator observations and triggers mesh workflows.
    Sources: iNaturalist API, hive sensors, transect surveys, RADARSAT granules.
    """
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "pollinator_observer", watch_dirs: list = None):
        super().__init__(name, capabilities=["monitor", "ingest", "trigger"])
        self.watch_dirs = [Path(d) for d in (watch_dirs or ["data/pollinator_observations", "data/incoming"])]
        for d in self.watch_dirs:
            d.mkdir(parents=True, exist_ok=True)
        self.processed_ids = set()

    def scan_for_observations(self) -> List[Dict]:
        new_obs = []
        for watch_dir in self.watch_dirs:
            for json_file in watch_dir.glob("*.json"):
                obs_id = json_file.stem
                if obs_id not in self.processed_ids:
                    try:
                        with open(json_file) as f:
                            obs = json.load(f)
                        if self._validate_observation(obs):
                            new_obs.append(obs)
                            self.processed_ids.add(obs_id)
                            self.seal("observation_detected", {"id": obs_id, "species": obs.get('species')})
                    except Exception as e:
                        logger.error(f"Failed to parse {json_file}: {e}")
        return new_obs

    def _validate_observation(self, obs: Dict) -> bool:
        required = ["species", "location", "timestamp"]
        return all(k in obs for k in required)

    def execute(self, trigger_callback: callable = None) -> int:
        logger.info(f"[{self.agent_id}] Scanning for pollinator observations...")
        observations = self.scan_for_observations()
        
        triggered = 0
        for obs in observations:
            if trigger_callback:
                success = trigger_callback(obs)
                if success:
                    triggered += 1
                    self.seal("workflow_triggered", {"obs_id": obs.get('id'), "status": "success"})
        
        return triggered

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = PollinatorObserverAgent()
    count = agent.execute(lambda x: True)
    logger.info(f"Triggered {count} workflows")
