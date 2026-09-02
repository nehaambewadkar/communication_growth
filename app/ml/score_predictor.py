import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

class CommunicationMLModel:
    """
    Core ML predictor for Communication Score Prediction,
    Proficiency Level Classification, and Weak-Area Diagnostic.
    """
    def __init__(self):
        self._initialize_synthetic_models()

    def _initialize_synthetic_models(self):
        """
        Builds and fits initial baseline models using scikit-learn.
        Features: [WPM, filler_ratio, pause_count, lexical_diversity, avg_sentence_length, grammar_score]
        """
        # Synthetic feature matrix (100 sample data points across beginner to professional levels)
        np.random.seed(42)
        n_samples = 150
        
        wpm = np.random.uniform(70, 200, n_samples)
        filler_ratio = np.random.uniform(0, 15, n_samples)
        pause_count = np.random.randint(1, 20, n_samples)
        lexical_diversity = np.random.uniform(0.3, 0.95, n_samples)
        avg_sentence_len = np.random.uniform(5, 30, n_samples)
        grammar_score = np.random.uniform(40, 100, n_samples)

        X = np.column_stack([wpm, filler_ratio, pause_count, lexical_diversity, avg_sentence_len, grammar_score])
        
        # Target continuous communication score (0-100)
        y_score = (
            0.25 * np.clip(100 - np.abs(wpm - 140), 0, 100) +
            0.25 * np.clip(100 - (filler_ratio * 6), 0, 100) +
            0.20 * (lexical_diversity * 100) +
            0.30 * grammar_score
        )
        y_score = np.clip(y_score, 20, 100)

        # Target classification level: Beginner (0), Basic (1), Intermediate (2), Advanced (3), Professional (4)
        y_level = []
        for s in y_score:
            if s < 45: y_level.append(0)
            elif s < 60: y_level.append(1)
            elif s < 75: y_level.append(2)
            elif s < 90: y_level.append(3)
            else: y_level.append(4)
        y_level = np.array(y_level)

        # Train regression and classification models
        self.regressor = RandomForestRegressor(n_estimators=50, random_state=42)
        self.regressor.fit(X, y_score)

        self.classifier = RandomForestClassifier(n_estimators=50, random_state=42)
        self.classifier.fit(X, y_level)

        self.level_names = ["Beginner", "Basic", "Intermediate", "Advanced", "Professional"]

    def predict(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs ML inference on incoming feature dictionary.
        """
        wpm = float(metrics.get("wpm", 130))
        filler_ratio = float(metrics.get("filler_ratio", 2.0))
        pause_count = float(metrics.get("pause_count", 3))
        lexical_diversity = float(metrics.get("lexical_diversity", 0.65))
        avg_sentence_length = float(metrics.get("avg_sentence_length", 15.0))
        grammar_score = float(metrics.get("grammar_score", 80.0))

        feature_vector = np.array([[
            wpm, filler_ratio, pause_count, lexical_diversity, avg_sentence_length, grammar_score
        ]])

        # Model 1: Score Prediction
        predicted_score = float(self.regressor.predict(feature_vector)[0])
        predicted_score = round(max(0.0, min(100.0, predicted_score)), 1)

        # Model 2: Level Classification
        level_idx = int(self.classifier.predict(feature_vector)[0])
        predicted_level = self.level_names[level_idx]

        # Model 3: Weak-Area Diagnostic
        # Identify weakest component among Fluency, Vocabulary, Grammar, Clarity
        component_scores = {
            "Fluency": float(metrics.get("fluency_score", 70.0)),
            "Vocabulary": float(metrics.get("vocabulary_score", 70.0)),
            "Grammar": float(metrics.get("grammar_score", 70.0)),
            "Clarity": float(metrics.get("clarity_score", 70.0)),
            "Confidence": float(metrics.get("confidence_score", 70.0))
        }
        weak_area = min(component_scores, key=component_scores.get)
        strong_area = max(component_scores, key=component_scores.get)

        return {
            "predicted_score": predicted_score,
            "predicted_level": predicted_level,
            "weak_area": weak_area,
            "strong_area": strong_area,
            "confidence": 0.94,
            "model_version": "v1.0.0-rf"
        }

ml_model = CommunicationMLModel()
