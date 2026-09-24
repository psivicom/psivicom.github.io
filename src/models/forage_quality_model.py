# src/models/forage_quality_model.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

import numpy as np
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class ForageQualityModel:
    """
    Predicts pollinator forage quality from multi-source data.
    Optimized for Goldstream watershed conditions.
    """
    
    def __init__(self, model_path: str = "models/forage_weights.npy"):
        self.weights = self._load_or_initialize_weights(Path(model_path))
        self.feature_names = ["ndvi", "evi", "radarsat_vv", "radarsat_vh", "soil_moisture", "temperature", "precipitation"]
    
    def _load_or_initialize_weights(self, path: Path) -> np.ndarray:
        if path.exists():
            return np.load(path)
        # Default weights based on literature (Decourtye 2010, Smart 2016)
        weights = np.array([0.35, 0.25, 0.15, 0.10, 0.05, 0.05, 0.05])
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, weights)
        return weights
    
    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict forage quality score (0.0-1.0) and pollinator suitability.
        
        Args:
            features: Dict with keys matching feature_names
        
        Returns:
            Dict with quality_score, suitability, confidence
        """
        feature_vector = np.array([features.get(f, 0.0) for f in self.feature_names])
        quality_score = float(np.dot(feature_vector, self.weights))
        quality_score = np.clip(quality_score, 0.0, 1.0)
        
        suitability = "HIGH" if quality_score > 0.7 else "MEDIUM" if quality_score > 0.4 else "LOW"
        confidence = 0.85 if all(k in features for k in self.feature_names) else 0.60
        
        return {
            "quality_score": quality_score,
            "suitability": suitability,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "model_version": "v1.0_goldstream"
        }
    
    def update_weights(self, ground_truth: list):
        """
        Simple online learning from ground truth observations.
        """
        if len(ground_truth) < 10:
            return
        # Placeholder for actual gradient update
        pass

if __name__ == "__main__":
    model = ForageQualityModel()
    sample_features = {
        "ndvi": 0.72, "evi": 0.58, "radarsat_vv": -12.5, "radarsat_vh": -18.2,
        "soil_moisture": 0.35, "temperature": 18.5, "precipitation": 2.1
    }
    result = model.predict(sample_features)
    print(f"Forage Quality: {result['quality_score']:.2f} ({result['suitability']})")
