# scripts/ingest_knowledge_base.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import os
import json
import glob
import fitz  # PyMuPDF (requires 'pymupdf' in requirements.txt)

def extract_dna_from_pdf(pdf_path):
    """Extracts bio-mathematical signals from a single PDF."""
    doc = fitz.open(pdf_path)
    extracted_dna = {
        "source_file": os.path.basename(pdf_path),
        "total_pages": len(doc),
        "layers": {
            "architectures": [],          # CNN/LSTM topologies (Protein Math)
            "mathematical_functions": [], # Loss functions/Optimization (Genetic Math)
            "domain_knowledge": []        # Physics/Telemetry/Domain data (Dimensional Substrate)
        }
    }
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").lower()
        
        # Extracting the "Proteins" (Architectures)
        if any(term in text for term in ["cnn", "convolutional", "lstm", "rnn", "recurrent", "network", "transformer"]):
            extracted_dna["layers"]["architectures"].append({"page": page_num + 1, "signal": "Deep Learning Topology Detected"})
            
        # Extracting the "Genetics" (Math & Optimization)
        if any(term in text for term in ["loss", "cross-entropy", "mse", "gradient", "backpropagation", "optimization", "eigenvalue"]):
            extracted_dna["layers"]["mathematical_functions"].append({"page": page_num + 1, "signal": "Optimization Logic Detected"})
            
        # Extracting the "Dimensional Data" (Domain Knowledge)
        if any(term in text for term in ["moon", "lunar", "crater", "phase", "orbit", "objective", "telemetry", "vector", "tensor"]):
            extracted_dna["layers"]["domain_knowledge"].append({"page": page_num + 1, "signal": "Domain Physics Detected"})
            
    return extracted_dna

def main():
    print("🧠 Initiating Batch Bio-Mathematical Ingestion...")
    
    workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())
    raw_dir = os.path.join(workspace, "data", "raw")
    output_dir = os.path.join(workspace, "data", "knowledge_base")
    
    # Ensure directories exist
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Find ALL pdf files in the raw directory
    pdf_files = glob.glob(os.path.join(raw_dir, "*.pdf"))
    
    if not pdf_files:
        print("ℹ️ No PDF files found in data/raw/. Nothing to ingest.")
        return True

    print(f"🔍 Found {len(pdf_files)} PDF(s) to digest.")
    processed_count = 0
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"  📥 Digesting: {filename}...")
        
        try:
            dna = extract_dna_from_pdf(pdf_path)
            
            # Create a matching JSON filename (e.g., report.pdf -> report.pdf.json)
            output_filename = f"{filename}.json"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(dna, f, indent=2)
                
            print(f"  ✅ Successfully collapsed {filename} into dimensional substrate.")
            processed_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to process {filename}: {str(e)}")
            
    print(f"🏁 Batch ingestion complete. {processed_count}/{len(pdf_files)} files processed.")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
