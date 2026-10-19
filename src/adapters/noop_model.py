# No-op local model adapter
# Default adapter used in CI: returns a clear disabled response so calling code does not crash.

from typing import Dict, Any

def generate(prompt: str, max_tokens: int = 512, **opts) -> Dict[str, Any]:
    """
    No-op adapter: LLM disabled in CI. Operators can run local adapters manually.
    Returns a deterministic failure object with guidance.
    """
    return {
        "success": False,
        "error": "LLM disabled in CI. Run local adapter on operator node.",
        "prompt": prompt,
        "meta": {"adapter": "noop", "note": "LLM disabled"}
    }
