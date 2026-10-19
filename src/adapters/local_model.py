# Local model adapter (operator-run only)
# This adapter calls a localhost inference endpoint. CI must not enable it.

import requests
from typing import Dict, Any

LOCAL_ENDPOINT = "http://127.0.0.1:11434/api/generate"


def generate(prompt: str, max_tokens: int = 512, **opts) -> Dict[str, Any]:
    try:
        payload = {"prompt": prompt, "max_tokens": max_tokens}
        r = requests.post(LOCAL_ENDPOINT, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return {"success": True, "text": data.get("response", ""), "meta": {"adapter": "local"}}
    except Exception as e:
        return {"success": False, "error": str(e), "meta": {"adapter": "local"}}
