# src/tools/ai_handshake_initiator.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from src.core.psvc_sovereign import SovereignPSVC

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("AI_HANDSHAKE_INITIATOR")

def main():
    logger.info("🤝 Initiating AI Handshake Protocol...")
    
    # SURGICAL FIX: Prevent EOFError in headless CI environments
    if os.environ.get("CI") == "true":
        recipient = os.environ.get("AI_RECIPIENT", "qwen")
        logger.info(f"ℹ️ CI Environment detected. Using default recipient: {recipient}")
    else:
        recipient = input("Enter external AI name (e.g., qwen, claude, llama): ").strip() or "external_ai"

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")[:-3] + "Z"
    handshake_dir = Path("data/ai_handshake")
    handshake_dir.mkdir(parents=True, exist_ok=True)
    
    payload = {
        "initiator": "WENDY",
        "recipient": recipient,
        "timestamp": timestamp,
        "protocol_version": "1.0",
        "intent": "Establish secure cognitive mesh bridge"
    }
    
    # Seal the handshake
    psvc = SovereignPSVC(payload)
    json_path = handshake_dir / f"handshake_{recipient}_{timestamp}.json"
    psvc_path = handshake_dir / f"handshake_{recipient}_{timestamp}.psvc"
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
        
    psvc.seal_to_file(str(psvc_path))
    
    logger.info(f"✅ Handshake sealed and stored at {psvc_path}")

if __name__ == "__main__":
    main()
