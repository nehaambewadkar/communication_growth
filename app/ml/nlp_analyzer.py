import re
from typing import Dict, List, Any

# Common filler words and phrases
FILLER_WORDS = [
    "um", "uh", "like", "actually", "basically", "you know",
    "i mean", "sort of", "kind of", "literally", "honestly",
    "right", "so yeah", "basically speaking", "as in"
]

class SpeechNLPAnalyzer:
    def __init__(self):
        self.filler_patterns = [re.compile(r'\b' + re.escape(w) + r'\b', re.IGNORECASE) for w in FILLER_WORDS]

    def analyze(self, transcript: str, duration_seconds: float) -> Dict[str, Any]:
        """
        Analyzes a spoken transcript and audio metadata.
        Returns a dictionary of raw speech/NLP metrics and sub-scores.
        """
        cleaned_transcript = transcript.strip()
        words = re.findall(r'\b\w+\b', cleaned_transcript.lower())
        word_count = len(words)
        
        # 1. Words Per Minute (WPM)
        minutes = max(duration_seconds / 60.0, 0.05)
        wpm = round(word_count / minutes, 1)

        # 2. Filler Word Detection
        detected_fillers = []
        filler_count = 0
        for word in words:
            if word in FILLER_WORDS:
                detected_fillers.append(word)
                filler_count += 1
                
        # Also check phrase fillers
        lower_transcript = cleaned_transcript.lower()
        for phrase in ["you know", "i mean", "sort of", "kind of", "so yeah"]:
            phrase_matches = len(re.findall(r'\b' + re.escape(phrase) + r'\b', lower_transcript))
            if phrase_matches > 0:
                detected_fillers.extend([phrase] * phrase_matches)
                filler_count += phrase_matches

        filler_ratio = round((filler_count / max(word_count, 1)) * 100, 1)

        # 3. Repeated Words Detection
        repeated_words = []
        for i in range(len(words) - 1):
            if words[i] == words[i + 1] and len(words[i]) > 2:
                repeated_words.append(words[i])
        repetition_count = len(repeated_words)

        # 4. Lexical Diversity (Type-Token Ratio)
        unique_words = set(words)
        lexical_diversity = round(len(unique_words) / max(word_count, 1), 2)

        # 5. Sentence Structure & Complexity
        sentences = [s.strip() for s in re.split(r'[.!?]+', cleaned_transcript) if s.strip()]
        sentence_count = max(len(sentences), 1)
        avg_sentence_length = round(word_count / sentence_count, 1)

        # 6. Estimate Pauses (based on punctuation & ellipses in transcript)
        pause_count = len(re.findall(r'(\.\.\.|,|;|--)', cleaned_transcript))
        average_pause_duration = 1.2 if pause_count > 0 else 0.5

        # 7. Calculate Derived Sub-Scores (0 to 100 scale)
        
        # Fluency Score: optimal WPM is 120-160, penalize fillers and repetitions
        if 110 <= wpm <= 160:
            base_fluency = 90
        elif 90 <= wpm < 110 or 160 < wpm <= 180:
            base_fluency = 75
        elif 70 <= wpm < 90 or 180 < wpm <= 200:
            base_fluency = 60
        else:
            base_fluency = 45
            
        fluency_penalty = (filler_ratio * 2.5) + (repetition_count * 3.0)
        fluency_score = round(max(0, min(100, base_fluency - fluency_penalty)), 1)

        # Vocabulary Score: based on lexical diversity and word variety
        vocab_score = round(max(0, min(100, (lexical_diversity * 90) + 15)), 1)

        # Clarity Score: penalize very long/convoluted or extremely short sentences
        if 10 <= avg_sentence_length <= 22:
            clarity_score = round(max(50, 95 - (filler_ratio * 2)), 1)
        else:
            clarity_score = round(max(40, 80 - (filler_ratio * 2)), 1)

        # Confidence Score: balanced WPM, low fillers, steady pace
        confidence_score = round(max(0, min(100, fluency_score * 0.6 + clarity_score * 0.4)), 1)

        # Overall Score
        overall_score = round(
            (fluency_score * 0.3) + (clarity_score * 0.25) + (vocab_score * 0.25) + (confidence_score * 0.2), 
            1
        )

        from app.ml.grammar_checker import grammar_coach
        grammar_score = grammar_coach.analyze(transcript)["grammar_score"]

        return {
            "transcript": transcript,
            "word_count": word_count,
            "duration": duration_seconds,
            "wpm": wpm,
            "filler_count": filler_count,
            "filler_ratio": filler_ratio,
            "filler_words": detected_fillers,
            "pause_count": pause_count,
            "average_pause_duration": average_pause_duration,
            "repetition_count": repetition_count,
            "lexical_diversity": lexical_diversity,
            "avg_sentence_length": avg_sentence_length,
            "fluency_score": fluency_score,
            "grammar_score": grammar_score,
            "vocabulary_score": vocab_score,
            "clarity_score": clarity_score,
            "confidence_score": confidence_score,
            "overall_score": overall_score,
        }

nlp_analyzer = SpeechNLPAnalyzer()
