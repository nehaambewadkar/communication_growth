import re
from typing import Dict, List, Any

# Pre-defined grammar rule patterns for common English mistakes
GRAMMAR_RULES = [
    {
        "category": "Subject-Verb Agreement",
        "pattern": r'\b(he|she|it)\s+(have|do|go|say)\b',
        "replacement": r'\1 has/does/goes/says',
        "explanation": "Third-person singular subjects (he, she, it) require singular verb forms."
    },
    {
        "category": "Subject-Verb Agreement",
        "pattern": r'\b(they|we|you)\s+(is|was)\b',
        "replacement": r'\1 are/were',
        "explanation": "Plural subjects (they, we, you) require plural verb forms."
    },
    {
        "category": "Article Usage",
        "pattern": r'\ba\s+([aeiouAEIOU]\w+)\b',
        "replacement": r'an \1',
        "explanation": "Use 'an' before words starting with a vowel sound."
    },
    {
        "category": "Article Usage",
        "pattern": r'\ban\s+([bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]\w+)\b',
        "replacement": r'a \1',
        "explanation": "Use 'a' before words starting with a consonant sound."
    },
    {
        "category": "Tenses & Aspect",
        "pattern": r'\bdid\s+(\w+ed|\w+s)\b',
        "replacement": "did + base form of verb",
        "explanation": "'did' should be followed by the base form of the verb (e.g. 'did go' instead of 'did went')."
    },
    {
        "category": "Prepositions",
        "pattern": r'\bdiscuss(ed|es|ing)?\s+about\b',
        "replacement": r'discuss\1',
        "explanation": "'Discuss' already means 'talk about'. Avoid using 'discuss about'."
    },
    {
        "category": "Prepositions",
        "pattern": r'\bdepend(s|ed|ing)?\s+of\b',
        "replacement": r'depend\1 on',
        "explanation": "The correct preposition is 'depend on'."
    },
    {
        "category": "Redundancy",
        "pattern": r'\brepeat\s+again\b',
        "replacement": "repeat",
        "explanation": "'Repeat' implies doing something again; 'again' is redundant."
    }
]

# Advanced vocabulary replacement dictionary
VOCAB_IMPROVEMENTS = {
    "good": ["exceptional", "exemplary", "commendable", "proficient"],
    "bad": ["suboptimal", "deficient", "detrimental", "unsatisfactory"],
    "big": ["substantial", "significant", "extensive", "prominent"],
    "important": ["pivotal", "crucial", "paramount", "vital"],
    "show": ["demonstrate", "illustrate", "exemplify", "manifest"],
    "use": ["utilize", "harness", "deploy", "leverage"],
    "think": ["perceive", "deliberate", "conclude", "postulate"],
    "help": ["assist", "facilitate", "foster", "empower"]
}

class GrammarCoach:
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes written text for grammatical errors, error categorization,
        vocabulary improvements, and overall writing score.
        """
        error_categories = {
            "Subject-Verb Agreement": 0,
            "Article Usage": 0,
            "Tenses & Aspect": 0,
            "Prepositions": 0,
            "Redundancy": 0
        }
        
        detected_issues = []
        corrected_text = text

        for rule in GRAMMAR_RULES:
            matches = list(re.finditer(rule["pattern"], text, flags=re.IGNORECASE))
            if matches:
                category = rule["category"]
                error_categories[category] += len(matches)
                for m in matches:
                    detected_issues.append({
                        "category": category,
                        "found": m.group(0),
                        "explanation": rule["explanation"]
                    })
                corrected_text = re.sub(rule["pattern"], rule["replacement"], corrected_text, flags=re.IGNORECASE)

        # Vocabulary enhancement suggestions
        suggestions = []
        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            if word in VOCAB_IMPROVEMENTS:
                alt = VOCAB_IMPROVEMENTS[word][0]
                suggestions.append(f"Consider replacing '{word}' with a stronger term like '{alt}'.")

        # Deduplicate suggestions
        suggestions = list(set(suggestions))[:5]

        # Calculate scores
        total_errors = sum(error_categories.values())
        word_count = max(len(words), 1)
        
        grammar_score = max(30.0, round(100.0 - (total_errors * 12.0), 1))
        vocab_score = min(98.0, round(60.0 + (len(set(words)) / word_count) * 40, 1))
        overall_score = round((grammar_score * 0.6) + (vocab_score * 0.4), 1)

        feedback = (
            "Your writing is clear and structured well." if total_errors == 0 
            else f"Identified {total_errors} grammatical issue(s). Focus on {max(error_categories, key=error_categories.get)}."
        )

        return {
            "original_text": text,
            "corrected_text": corrected_text,
            "error_categories": error_categories,
            "detected_issues": detected_issues,
            "suggestions": suggestions,
            "grammar_score": grammar_score,
            "vocabulary_score": vocab_score,
            "overall_score": overall_score,
            "feedback": feedback
        }

grammar_coach = GrammarCoach()
