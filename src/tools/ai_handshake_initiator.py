# src/tools/ai_handshake_initiator.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM
# One-command tool to package and share PSIVI collaboration protocol with external AIs

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.ambassador_agent import AmbassadorAgent

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("🌐 PSIVI AI HANDSHAKE INITIATOR")
    print("="*60)
    print("\nThis tool packages the PSIVI collaboration protocol")
    print("into .psvc containers that external AIs can understand.")
    print("\nNo manual key exchange needed. The protocol IS the key.\n")
    
    # Get recipient AI name
    recipient = input("Enter external AI name (e.g., qwen, claude, llama): ").strip() or "external_ai"
    
    # Get delivery method
    print("\nDelivery methods:")
    print("  1. file_drop   - Place in data/ai_handshake/ (local AI access)")
    print("  2. github      - Create GitHub issue with protocol attached")
    print("  3. url         - Upload to public URL (manual step)")
    
    method = input("\nChoose delivery method (1/2/3): ").strip() or "1"
    method_map = {"1": "file_drop", "2": "github", "3": "url"}
    delivery_method = method_map.get(method, "file_drop")
    
    # Execute handshake
    agent = AmbassadorAgent()
    result = agent.execute(recipient_ai=recipient, auto_share=True)
    result["delivery_method"] = delivery_method
    
    print("\n" + "="*60)
    print("✅ HANDSHAKE PACKAGE READY")
    print("="*60)
    print(f"Recipient AI: {recipient}")
    print(f"Protocol File: {result.get('protocol_path', 'N/A')}")
    print(f"Sidecar JSON: {result.get('sidecar_path', 'N/A')}")
    print(f"Delivery: {delivery_method}")
    print(f"\n📄 External AI should read the .json sidecar file to learn")
    print(f"   how to collaborate with your PSIVI Mesh autonomously.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
