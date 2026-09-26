# src/agents/observer_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# Event-Driven Autonomy Agent (Inspired by OPERA-SDS-PCM data_subscriber)

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

from src.base.base_agent import BaseAgent, AgentLayer
from src.core.spatio_temporal import SpatioTemporalEngine

logger = logging.getLogger(__name__)

class ObserverAgent(BaseAgent):
    """
    Proactive, event-driven agent that monitors external streams or local directories
    for new data granules, automatically triggering downstream workflows.
    """
    LAYER = AgentLayer.INGESTION

    def __init__(self, name: str = "observer", watch_dir: str = "data/incoming"):
        super().__init__(name, capabilities=["monitor", "trigger", "validate"])
        self.watch_dir = Path(watch_dir)
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.st_engine = SpatioTemporalEngine()
        self.processed_granules: set = set()

    def scan_for_new_granules(self) -> list:
        """Scans watch directory for new JSON/metadata files representing data granules."""
        new_granules = []
        for meta_file in self.watch_dir.glob("*.json"):
            granule_id = meta_file.stem
            if granule_id not in self.processed_granules:
                try:
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Pre-flight smoke test for metadata
                    if self.st_engine.validate_granule_metadata(metadata):
                        new_granules.append({"id": granule_id, "metadata": metadata, "path": meta_file})
                        self.processed_granules.add(granule_id)
                        self.seal("granule_detected", {"granule_id": granule_id})
                    else:
                        logger.warning(f"Granule {granule_id} failed metadata validation")
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse metadata for {granule_id}")
        return new_granules

    def execute(self, trigger_workflow_callback: callable) -> int:
        """
        Main execution loop. Finds new granules and triggers the orchestrator.
        """
        logger.info(f"[{self.agent_id}] Scanning for new granules in {self.watch_dir}...")
        new_granules = self.scan_for_new_granules()
        
        triggered_count = 0
        for granule in new_granules:
            logger.info(f"[{self.agent_id}] Triggering workflow for granule: {granule['id']}")
            success = trigger_workflow_callback(granule['metadata'])
            if success:
                triggered_count += 1
                self.seal("workflow_triggered", {"granule_id": granule['id'], "status": "success"})
            else:
                self.seal("workflow_triggered", {"granule_id": granule['id'], "status": "failed"}, fragility=True)
                
        return triggered_count

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    observer = ObserverAgent()
    
    # Mock callback simulating ChainOrchestrator execution
    def mock_workflow_trigger(metadata: Dict[str, Any]) -> bool:
        logger.info(f"  -> Orchestrator received: {metadata.get('granule_id')}")
        return True
        
    count = observer.execute(mock_workflow_trigger)
    logger.info(f"[{observer.agent_id}] Scan complete. Triggered {count} workflows.")
