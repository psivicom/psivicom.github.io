# src/agents/agent_factory.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AgentFactory:
    def __init__(self, templates_path: str = "config/agent_templates.json"):
        self.templates_path = Path(templates_path)
        self.templates = self._load_templates()
        self.agents_dir = Path("src/agents")
        self.agents_dir.mkdir(parents=True, exist_ok=True)

    def _load_templates(self) -> Dict[str, str]:
        if not self.templates_path.exists():
            logger.warning(f"Templates file not found: {self.templates_path}")
            return {}
        with open(self.templates_path) as f:
            data = json.load(f)
            return data.get("templates", {})

    def create_agent(self, params: Dict[str, Any]) -> bool:
        template_name = params.get("template_name")
        agent_name = params.get("agent_name")
        config = params.get("config", {})
        
        if not template_name or not agent_name:
            logger.error("Missing template_name or agent_name in instruction")
            return False
        
        template_code = self.templates.get(template_name)
        if not template_code:
            logger.error(f"Template {template_name} not found")
            return False
        
        try:
            generated_code = template_code.format(
                agent_name=agent_name,
                agent_id=f"{agent_name}_agent",
                config_json=json.dumps(config, indent=2)
            )
        except KeyError as e:
            logger.error(f"Invalid template placeholder: {e}")
            return False
        
        filename = f"{agent_name}_agent.py"
        filepath = self.agents_dir / filename
        
        if filepath.exists():
            logger.warning(f"Agent {filename} already exists, skipping")
            return False
            
        with open(filepath, 'w') as f:
            f.write(generated_code)
            
        logger.info(f"Generated new agent: {filename}")
        return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    factory = AgentFactory()
    success = factory.create_agent({"template_name": "satellite_observer", "agent_name": "test_sat", "config": {"endpoint": "test"}})
    logger.info(f"Factory test: {'Success' if success else 'Failed'}")
