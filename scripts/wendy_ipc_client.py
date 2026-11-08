#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WENDY IPC Client
SPDX-License-Identifier: EUPL-1.2
Communicates with the Rust Tokio substrate on port 1966 to update 
the Gemini capsule and Hebbian topology.
"""
import socket
import json
import logging
import sys
from datetime import datetime, timezone

def zulu_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def notify_rust_core(action: str, uri: str, payload_text: str) -> bool:
    """Sends a JSON payload to the Rust IPC server on 127.0.0.1:1966."""
    msg = json.dumps({
        "action": action,
        "uri": uri,
        "payload": payload_text
    })
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect(("127.0.0.1", 1966))
            s.sendall(msg.encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            
            if response == "ACK":
                logging.info(f"[{zulu_now()}] ✅ Rust Core ACKed: {uri}")
                return True
            elif response == "VETO":
                logging.warning(f"[{zulu_now()}] 🛑 Rust Veto Module rejected: {uri}")
                return False
            else:
                logging.error(f"[{zulu_now()}] ❌ Rust Core returned unexpected response: {response}")
                return False
                
    except ConnectionRefusedError:
        logging.error(f"[{zulu_now()}] ❌ Could not connect to Rust Core on 127.0.0.1:1966. Is the substrate running?")
        return False
    except Exception as e:
        logging.error(f"[{zulu_now()}] ❌ IPC Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) == 4:
        notify_rust_core(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: wendy_ipc_client.py <action> <uri> <payload>")
