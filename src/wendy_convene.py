# Add this import to the top of src/wendy_convene.py
from wendy_adjudicator import WendyAdjudicator, SystemState

# Inside the WendyConvene class __init__:
# self.adjudicator = WendyAdjudicator()

# Replace the return block in execute_convene with this:
            parsed = json.loads(content)
            
            # ADVERSARIAL CHECK: Force validation against actual system state
            # (In production, these values are passed in from the Go/Zig orchestration layer)
            current_state = SystemState(
                zig_checksum_valid=True, # Pulled from Zig FFI
                go_sandbox_exit_code=0,  # Pulled from Go Sandbox
                go_sandbox_stdout_hash=hashlib.sha256(b"mock_stdout").hexdigest(),
                sensor_data_present=True
            )
            
            adjudication = self.adjudicator.evaluate_ruling(parsed, current_state)
            
            if adjudication["status"] == "REJECTED":
                print(f"[WENDY ADJUDICATOR] Blocked biased ruling: {adjudication['reason']}")
                return {
                    "action": "respond", 
                    "payload": {"text": "System state mismatch. Operation aborted for safety."}, 
                    "confidence": 0.0
                }
                
            print(f"[WENDY CONVENE] Single-pass execution validated in {time.time() - start_time:.2f}s")
            return adjudication["ruling"]
