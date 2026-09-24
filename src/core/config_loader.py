# src/core/config_loader.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load()
    
    def _load(self):
        if self.config_path.exists():
            if self.config_path.suffix == '.json':
                with open(self.config_path) as f:
                    self.config = json.load(f)
            elif self.config_path.suffix in ['.yaml', '.yml']:
                import yaml
                with open(self.config_path) as f:
                    self.config = yaml.safe_load(f) or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
