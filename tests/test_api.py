import pytest
from app.ml.nlp_analyzer import nlp_analyzer
from app.ml.grammar_checker import grammar_coach
from app.ml.score_predictor import ml_model

def test_nlp_analyzer():
    transcript = "Um, hello everyone. Like, I am going to talk about, you know, machine learning today."
    results = nlp_analyzer.analyze(transcript, duration_seconds=30.0)
    
    assert results["word_count"] > 0
    assert results["filler_count"] >= 3
    assert "um" in results["filler_words"] or "like" in results["filler_words"]
    assert 0 <= results["overall_score"] <= 100

def test_grammar_coach():
    text = "He have a good project and we discussed about the architecture."
    results = grammar_coach.analyze(text)
    
    assert results["error_categories"]["Subject-Verb Agreement"] > 0
    assert results["error_categories"]["Prepositions"] > 0
    assert "discuss" in results["corrected_text"]

def test_ml_score_predictor():
    sample_metrics = {
        "wpm": 140,
        "filler_ratio": 2.0,
        "pause_count": 3,
        "lexical_diversity": 0.7,
        "avg_sentence_length": 14.0,
        "grammar_score": 85.0,
        "fluency_score": 80.0,
        "vocabulary_score": 75.0,
        "clarity_score": 85.0,
        "confidence_score": 82.0
    }
    prediction = ml_model.predict(sample_metrics)
    assert 0 <= prediction["predicted_score"] <= 100
    assert prediction["predicted_level"] in ["Beginner", "Basic", "Intermediate", "Advanced", "Professional"]
