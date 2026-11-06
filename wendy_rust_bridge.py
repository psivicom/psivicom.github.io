import socket
import json
import logging
from datetime import datetime, timezone

# --- STRICT ZULU (UTC) LOGGER ---
class ZuluFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        return dt.strftime('%Y-%m-%dT%H:%M:%S.') + f"{int(record.msecs):03d}Z"

logger = logging.getLogger("wendy_rust_bridge")
handler = logging.StreamHandler()
handler.setFormatter(ZuluFormatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class WendyRustBridge:
    def __init__(self, host="127.0.0.1", port=1966):
        self.host = host
        self.port = port

    def commit_to_substrate(self, uri: str, symbolic_math: str):
        payload = {
            "action": "commit",
            "uri": uri,
            "payload": symbolic_math
        }
        
        logger.info(f"transmitting crystallized math to rust substrate | uri={uri}")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.sendall(json.dumps(payload).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                
                if response == "ACK":
                    logger.info(f"rust substrate acknowledged commit | state=synchronized")
                else:
                    logger.error(f"rust substrate rejected commit | response={response}")
        except ConnectionRefusedError:
            logger.error("connection refused | ensure wendy-cortex rust daemon is running on port 1966")

if __name__ == "__main__":
    bridge = WendyRustBridge()
    
    # Simulating the Crystalline Executor passing data to the bridge
    test_uri = "gemini://wendy/capsule/learned_cas_loop.gmi"
    test_math = "# Lock-Free CAS Axiom\n∀ counter ∈ AtomicUsize:\n  mutate(counter) ≡ CAS(current, current + 1, SeqCst)\n  ⊢ lock_free(counter) ≡ ⊤"
    
    bridge.commit_to_substrate(test_uri, test_math)
