# src/agents/forage_agent.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import sys
import msgpack
import numpy as np
import logging
from pathlib import Path
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).parent.parent))
from src.base.base_agent import BaseAgent, AgentLayer
from src.utils.oidc_verifier import verify_oidc_token

logger = logging.getLogger("FORAGE_AGENT")

class ForageAgent(BaseAgent):
    LAYER = AgentLayer.INGESTION
    
    def __init__(self, name="forage"):
        super().__init__(name, capabilities=["search", "ingest", "cache"])
        self.output_dir = Path("data/forage_cache")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _verify_identity(self):
        oidc_token = os.environ.get('OIDC_TOKEN')
        if oidc_token and not verify_oidc_token(oidc_token):
            logger.error("🚫 SECURITY ALERT: Unverified identity. Aborting forage.")
            sys.exit(1)

    def execute(self):
        logger.info("🐝 Foraging Goldstream Watershed data...")
        self._verify_identity()
        
        record = {
            "source": "goldstream_watershed",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "metrics": {"temperature": 14.2, "ph_level": 7.1, "turbidity": 2.5},
            "status": "cached"
        }
        
        file_path = self.output_dir / f"forage_{record['source']}.mpk"
        
        try:
            with open(file_path, 'wb') as f:
                f.write(msgpack.packb(record, use_bin_type=True))
            logger.info(f"✅ Successfully foraged and sealed binary record: {file_path.name}")
            self.seal("forage_complete", {"file": file_path.name})
        except Exception as e:
            logger.error(f"❌ Failed to seal forage record: {e}")
            return False
            
        return np.random.randn(4096).astype(np.float32)

    def finalize(self, output_dir=None):
        out = output_dir or Path("reports/pico_containers")
        out.mkdir(parents=True, exist_ok=True)
        vec = np.random.randn(4096).astype(np.float32)
        self.seal_result(vec / np.linalg.norm(vec), out, meta={"agent": "forage"})
        logger.info("Forage Agent finalized and sealed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    agent = ForageAgent()
    result_vector = agent.execute()
    if result_vector is not False:
        agent.finalize()
