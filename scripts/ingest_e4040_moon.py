# scripts/ingest_e4040_moon.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import json
import fitz  # PyMuPDF (requires 'pymupdf' in requirements.txt)

def ingest_moon_report():
    print("🧠 Initiating Bio-Mathematical Ingestion of E4040 Fall 2016 MOON Report...")
    
    # Define exact, absolute paths relative to the GitHub workspace
    workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())
    pdf_path = os.path.join(workspace, "data", "raw", "E4040.2016Fall.MOON.report.xl2533.yz2866.zy2233.pdf")
    output_dir = os.path.join(workspace, "data", "knowledge_base")
    output_path = os.path.join(output_dir, "e4040_moon_2016_dna.json")
    
    if not os.path.exists(pdf_path):
        print(f"❌ CRITICAL: PDF not found at {pdf_path}")
        return False

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    extracted_dna = {
        "metadata": {
            "course": "ECBM E4040 Neural Networks and Deep Learning",
            "institution": "Columbia University",
            "semester": "Fall 2016",
            "project": "MOON",
            "authors": ["xl2533", "yz2866", "zy2233"],
            "dimension": "Synthetic Nervous System Integration"
        },
        "layers": {
            "architectures": [],          # CNN/LSTM topologies (Protein Math)
            "mathematical_functions": [], # Loss functions/Optimization (Genetic Math)
            "domain_knowledge": []        # Lunar/Orbital/Signal data (Dimensional Substrate)
        }
    }
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").lower()
        
        # Extracting the "Proteins" (Architectures)
        if any(term in text for term in ["cnn", "convolutional", "lstm", "rnn", "recurrent", "network"]):
            extracted_dna["layers"]["architectures"].append({"page": page_num + 1, "signal": "Deep Learning Topology Detected"})
            
        # Extracting the "Genetics" (Math & Optimization)
        if any(term in text for term in ["loss", "cross-entropy", "mse", "gradient", "backpropagation", "optimization"]):
            extracted_dna["layers"]["mathematical_functions"].append({"page": page_num + 1, "signal": "Optimization Logic Detected"})
            
        # Extracting the "Dimensional Data" (Domain Knowledge)
        if any(term in text for term in ["moon", "lunar", "crater", "phase", "orbit", "objective", "telemetry"]):
            extracted_dna["layers"]["domain_knowledge"].append({"page": page_num + 1, "signal": "Domain Physics Detected"})
            
    # Collapse into Wendy's Cellular Memory (Layer 4)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_dna, f, indent=2)
        
    print(f"✅ MOON report successfully collapsed into Wendy's dimensional substrate at: {output_path}")
    return True

if __name__ == "__main__":
    success = ingest_moon_report()
    exit(0 if success else 1)
