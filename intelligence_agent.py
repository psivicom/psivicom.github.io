# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
# Affiliation: PSIVI Research
#
# Intelligence Agent (Vector-Native Auditor)
# RFC 1001 Compliant - No subprocess, no text passing, pure vector operations.

import numpy as np
import json
import datetime
from pathlib import Path
from psvc_reference import (
    read_file, write_file, content_hash, validate_file,
    PRECISION_INT8, PRECISION_FLOAT16, PSVCError
)

CONTAINER_DIR = Path("reports/pico_containers")
AUDIT_DIR = Path("reports/intelligence_audits")

def load_all_vectors():
    """Load all valid .psvc containers into memory."""
    vectors = []
    metadata = []
    
    for psvc_file in CONTAINER_DIR.glob("*.psvc"):
        try:
            validate_file(psvc_file)
            vector = read_file(psvc_file)
            
            # Load sidecar metadata if exists
            json_file = psvc_file.with_suffix('.json')
            meta = {}
            if json_file.exists():
                with open(json_file) as f:
                    meta = json.load(f)
            
            vectors.append(vector)
            metadata.append({
                "file": psvc_file.name,
                "agent": meta.get("agent", "unknown"),
                "timestamp": meta.get("timestamp", ""),
                "hash": psvc_file.stem
            })
        except PSVCError as e:
            print(f"[INTEL] Skipping invalid container {psvc_file.name}: {e}")
            continue
    
    return np.array(vectors), metadata

def compute_mesh_statistics(vectors):
    """Compute statistical properties of the entire mesh."""
    if len(vectors) == 0:
        return None
    
    norms = np.linalg.norm(vectors, axis=1)
    
    return {
        "total_vectors": len(vectors),
        "mean_norm": float(np.mean(norms)),
        "std_norm": float(np.std(norms)),
        "min_norm": float(np.min(norms)),
        "max_norm": float(np.max(norms)),
        "dimensions": vectors.shape[1]
    }

def detect_anomalies(vectors, metadata, threshold=2.0):
    """Detect vectors that are statistical outliers (anomalies)."""
    if len(vectors) < 3:
        return []
    
    # Compute centroid (average vector)
    centroid = np.mean(vectors, axis=0)
    centroid /= np.linalg.norm(centroid)
    
    # Compute similarity of each vector to centroid
    similarities = np.dot(vectors, centroid)
    
    # Identify anomalies (vectors >2 standard deviations from mean similarity)
    mean_sim = np.mean(similarities)
    std_sim = np.std(similarities)
    
    anomalies = []
    for i, (sim, meta) in enumerate(zip(similarities, metadata)):
        z_score = (sim - mean_sim) / std_sim if std_sim > 0 else 0
        
        if abs(z_score) > threshold:
            anomalies.append({
                "file": meta["file"],
                "agent": meta["agent"],
                "similarity_to_centroid": float(sim),
                "z_score": float(z_score),
                "reason": "Statistical outlier" if z_score < 0 else "Unusually aligned"
            })
    
    return anomalies

def compute_drift(vectors, metadata):
    """Detect temporal drift in the mesh (are recent vectors different from old ones?)."""
    if len(vectors) < 10:
        return None
    
    # Sort by timestamp
    sorted_indices = sorted(range(len(metadata)), 
                           key=lambda i: metadata[i]["timestamp"], 
                           reverse=True)
    
    # Split into recent (last 30%) and old (first 70%)
    split_point = int(len(sorted_indices) * 0.3)
    recent_indices = sorted_indices[:split_point]
    old_indices = sorted_indices[split_point:]
    
    if len(recent_indices) < 3 or len(old_indices) < 3:
        return None
    
    recent_vectors = vectors[recent_indices]
    old_vectors = vectors[old_indices]
    
    # Compute centroids
    recent_centroid = np.mean(recent_vectors, axis=0)
    old_centroid = np.mean(old_vectors, axis=0)
    
    # Normalize
    recent_centroid /= np.linalg.norm(recent_centroid)
    old_centroid /= np.linalg.norm(old_centroid)
    
    # Compute drift (cosine similarity between centroids)
    drift_similarity = float(np.dot(recent_centroid, old_centroid))
    
    return {
        "drift_similarity": drift_similarity,
        "interpretation": "STABLE" if drift_similarity > 0.9 else 
                         "DRIFTING" if drift_similarity > 0.7 else 
                         "SHIFTED",
        "recent_count": len(recent_indices),
        "old_count": len(old_indices)
    }

def encode_audit_as_vector(audit_data):
    """Encode audit findings as a 4096-dim vector for storage in the mesh."""
    vec = np.zeros(4096, dtype=np.float32)
    
    # Encode statistics into vector space
    stats = audit_data.get("statistics", {})
    if stats:
        vec[0] = stats.get("total_vectors", 0) / 1000.0  # Normalize
        vec[1] = stats.get("mean_norm", 0)
        vec[2] = stats.get("std_norm", 0)
    
    # Encode drift into vector space
    drift = audit_data.get("drift", {})
    if drift:
        vec[10] = drift.get("drift_similarity", 0)
        vec[11] = 1.0 if drift.get("interpretation") == "STABLE" else 0.0
        vec[12] = 1.0 if drift.get("interpretation") == "DRIFTING" else 0.0
        vec[13] = 1.0 if drift.get("interpretation") == "SHIFTED" else 0.0
    
    # Encode anomaly count
    anomalies = audit_data.get("anomalies", [])
    vec[20] = len(anomalies) / 100.0  # Normalize
    
    # Normalize the vector
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    
    return vec

def write_audit_report(audit_data):
    """Write human-readable audit report (for GitHub Pages display)."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.utcnow().isoformat()
    report_path = AUDIT_DIR / f"audit_{timestamp[:10]}.md"
    
    with open(report_path, 'w') as f:
        f.write("# Intelligence Audit Report\n\n")
        f.write(f"**Timestamp:** {timestamp}\n\n")
        
        stats = audit_data.get("statistics")
        if stats:
            f.write("## Mesh Statistics\n")
            for key, value in stats.items():
                f.write(f"- **{key}:** {value}\n")
            f.write("\n")
        
        drift = audit_data.get("drift")
        if drift:
            f.write("## Temporal Drift Analysis\n")
            f.write(f"- **Status:** {drift['interpretation']}\n")
            f.write(f"- **Similarity:** {drift['drift_similarity']:.4f}\n")
            f.write(f"- **Recent vectors:** {drift['recent_count']}\n")
            f.write(f"- **Historical vectors:** {drift['old_count']}\n\n")
        
        anomalies = audit_data.get("anomalies", [])
        if anomalies:
            f.write(f"## Anomalies Detected ({len(anomalies)})\n")
            for a in anomalies:
                f.write(f"- **{a['file']}** ({a['agent']}): z-score={a['z_score']:.2f}\n")
        else:
            f.write("## Anomalies\n")
            f.write("No statistical outliers detected.\n")
    
    print(f"[INTEL] Audit report written: {report_path}")
    return report_path

if __name__ == "__main__":
    print("=== PSIVI INTELLIGENCE AGENT (VECTOR-NATIVE AUDITOR) ===")
    
    # Load all vectors from the mesh
    print("[INTEL] Loading all .psvc containers...")
    vectors, metadata = load_all_vectors()
    
    if len(vectors) == 0:
        print("[INTEL] Mesh is empty. Nothing to audit.")
        exit(0)
    
    print(f"[INTEL] Loaded {len(vectors)} vectors.")
    
    # Compute statistics
    print("[INTEL] Computing mesh statistics...")
    stats = compute_mesh_statistics(vectors)
    
    # Detect anomalies
    print("[INTEL] Detecting anomalies...")
    anomalies = detect_anomalies(vectors, metadata, threshold=2.0)
    
    # Compute drift
    print("[INTEL] Computing temporal drift...")
    drift = compute_drift(vectors, metadata)
    
    # Assemble audit data
    audit_data = {
        "statistics": stats,
        "anomalies": anomalies,
        "drift": drift,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    # Encode audit as vector and store in mesh
    print("[INTEL] Encoding audit as vector...")
    audit_vector = encode_audit_as_vector(audit_data)
    
    chash = content_hash(audit_vector)
    output_path = CONTAINER_DIR / f"audit_{chash}.psvc"
    write_file(audit_vector, output_path, precision=PRECISION_FLOAT16)
    
    # Write sidecar metadata
    sidecar_path = output_path.with_suffix('.json')
    with open(sidecar_path, 'w') as f:
        json.dump({
            "agent": "intelligence",
            "timestamp": audit_data["timestamp"],
            "type": "audit",
            "total_vectors_audited": len(vectors),
            "anomalies_found": len(anomalies),
            "drift_status": drift.get("interpretation", "UNKNOWN") if drift else "UNKNOWN"
        }, f, indent=2)
    
    print(f"[INTEL] Audit vector sealed: {output_path.name}")
    
    # Write human-readable report
    write_audit_report(audit_data)
    
    print("[INTEL] Intelligence audit complete.")
    print(f"[INTEL] Total vectors: {stats['total_vectors']}")
    print(f"[INTEL] Anomalies: {len(anomalies)}")
    if drift:
        print(f"[INTEL] Drift status: {drift['interpretation']}")
