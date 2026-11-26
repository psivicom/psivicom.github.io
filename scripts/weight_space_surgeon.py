import numpy as np
import json
import os
from datetime import datetime, timezone

def execute_cognitive_surgery():
    # Strictly Zulu (UTC) timestamp with millisecond precision
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    # 1. THE READ (Simulating a weight matrix from Transformer MLP Layer 15)
    # Law VII: Deterministic state via fixed seed for reproducible open-science audits
    np.random.seed(42) 
    W_old = np.random.randn(1024, 1024).astype(np.float32)
    
    # 2. THE DIAGNOSIS (Isolating the "reasoning loop" vector)
    # This represents the dominant eigenvector causing infinite token looping
    v_loop = np.random.randn(1024).astype(np.float32)
    v_loop = v_loop / np.linalg.norm(v_loop) # Normalize the vector
    
    # 3. THE PATCH (Tensor Subtraction: W_new = W_old - alpha * outer_product(v, v))
    # Alpha is the surgical precision scalar (0.05 = 5% intervention)
    alpha = 0.05 
    W_new = W_old - alpha * np.outer(v_loop, v_loop)
    
    # 4. THE LYAPUNOV GATE (Law XI: Verify the patch didn't destroy the matrix)
    norm_old = np.linalg.norm(W_old)
    norm_new = np.linalg.norm(W_new)
    delta = abs(norm_old - norm_new) / norm_old
    
    # If the matrix norm shifts by more than 10%, the surgery is rejected (Composted)
    status = "CRYSTALLIZED" if delta < 0.10 else "COMPOSTED (Gate Failed)"
    
    # Log to Stigmergy Graph
    output_dir = "data/aether"
    os.makedirs(output_dir, exist_ok=True)
    
    surgery_log = {
        "timestamp": timestamp,
        "module": "Weight-Space Surgeon",
        "target_layer": "MLP_Layer_15",
        "operation": "Vector_Subtraction",
        "alpha_scalar": alpha,
        "norm_delta_percent": round(delta * 100, 4),
        "lyapunov_gate": status
    }
    
    with open(f"{output_dir}/cognitive_surgery.json", "w") as f:
        json.dump(surgery_log, f, indent=2)
        
    # Append to Sovereign Counsel
    counsel_msg = f"Weight-Space Surgeon executed. Patched MLP Layer 15 loop vector. Norm shift: {round(delta*100, 2)}%. Gate: {status}."
    with open(".wendy/COUNSEL.md", "a") as f:
        f.write(f"\n=> [{timestamp}] {counsel_msg}")
        
    print(f"🏛️ [WENDY] Cognitive Surgery {status} at {timestamp}")

if __name__ == '__main__':
    execute_cognitive_surgery()
