# src/core/psvc_containers.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import json
import hashlib
from pathlib import Path
from typing import Dict, Any

def seal_container(vector, metadata: Dict[str, Any], output_path: Path):
    from psvc_reference import write_file, PRECISION_FLOAT16
    write_file(vector, output_path, precision=PRECISION_FLOAT16)
    sidecar = output_path.with_suffix('.json')
    with open(sidecar, 'w') as f:
        json.dump(metadata, f, indent=2)

def extract_metadata(sidecar_path: Path) -> Dict[str, Any]:
    with open(sidecar_path, 'r') as f:
        return json.load(f)
