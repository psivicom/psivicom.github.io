# src/mesh/pico_mesh.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PicoMesh:
    def __init__(self, container_dir: str = "reports/pico_containers"):
        self.container_dir = Path(container_dir)
        self.container_dir.mkdir(parents=True, exist_ok=True)
    
    def store_vector(self, vector: Any, metadata: Dict) -> Path:
        from psvc_reference import write_file, content_hash
        chash = content_hash(vector)
        filepath = self.container_dir / f"{chash}.psvc"
        write_file(vector, filepath)
        sidecar = filepath.with_suffix('.json')
        import json
        with open(sidecar, 'w') as f:
            json.dump(metadata, f, indent=2)
        return filepath
