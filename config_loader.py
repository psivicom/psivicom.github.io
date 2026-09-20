# config_loader.py
# SPDX-License-Identifier: CC-BY-4.0
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette

"""
Configuration loader for PSIVI Open Science Mesh.
Loads and validates YAML configuration with environment variable substitution.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class PSIVIConfig:
    """Strongly-typed configuration container."""
    metadata: Dict[str, Any]
    agents: Dict[str, Any]
    orchestration: Dict[str, Any]
    vector_mesh: Dict[str, Any]
    psvc_containers: Dict[str, Any]
    distributed_mesh: Dict[str, Any]
    llm_automation: Dict[str, Any]
    fair_compliance: Dict[str, Any]
    rfc1001: Dict[str, Any]
    security: Dict[str, Any]
    logging: Dict[str, Any]
    storage: Dict[str, Any]


def substitute_env_vars(value: Any) -> Any:
    """
    Recursively substitute environment variables in configuration values.
    Supports ${VAR_NAME} syntax.
    """
    if isinstance(value, str):
        pattern = re.compile(r'\$\{([^}]+)\}')
        return pattern.sub(lambda m: os.environ.get(m.group(1), ''), value)
    elif isinstance(value, dict):
        return {k: substitute_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [substitute_env_vars(item) for item in value]
    return value


def load_config(config_path: str = "config.yaml") -> PSIVIConfig:
    """
    Load and validate PSIVI configuration from YAML file.
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        raw_config = yaml.safe_load(f)
    
    # Substitute environment variables
    config = substitute_env_vars(raw_config)
    
    # Validate required sections
    required_sections = [
        'metadata', 'agents', 'orchestration', 'vector_mesh',
        'psvc_containers', 'rfc1001'
    ]
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    return PSIVIConfig(
        metadata=config['metadata'],
        agents=config['agents'],
        orchestration=config['orchestration'],
        vector_mesh=config['vector_mesh'],
        psvc_containers=config['psvc_containers'],
        distributed_mesh=config['distributed_mesh'],
        llm_automation=config['llm_automation'],
        fair_compliance=config['fair_compliance'],
        rfc1001=config['rfc1001'],
        security=config['security'],
        logging=config['logging'],
        storage=config['storage']
    )


def get_config() -> PSIVIConfig:
    """
    Get global configuration instance.
    """
    config_path = os.environ.get('PSIVI_CONFIG', 'config.yaml')
    return load_config(config_path)


if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    print(f"✓ Loaded PSIVI configuration v{config.metadata['version']}")
    print(f"✓ RFC 1001 Compliance: {config.metadata['rfc1001_compliant']}")
    print(f"✓ License: {config.metadata['license']}")
    print(f"✓ Agents configured: {list(config.agents.keys())}")
    print(f"✓ LLM Backend: {config.llm_automation['backend']}")
    print(f"✓ Vector Mesh Tiers: {list(config.vector_mesh['tiered_storage'].keys())}")
