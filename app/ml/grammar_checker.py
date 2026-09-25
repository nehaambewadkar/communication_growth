"""
grammar_checker.py
------------------
High-accuracy grammar correction module.

Primary engine  : LanguageTool public REST API (https://api.languagetool.org/v2/check)
                  — no Java, no local install required, 3000+ grammar rules.
Fallback engine : Curated regex rules for offline / API-unreachable scenarios.

Rules covered by the API engine:
  Subject-verb agreement, article usage, tenses, punctuation, spelling,
  confused words, collocations, style, redundancy, word choice, and more.
"""

import re
from typing import Any, Dict, List, Optional

try:
    import requests as _http
    _HTTP_AVAILABLE = True
except ImportError:
    _HTTP_AVAILABLE = False

# LanguageTool free public API endpoint (no key needed, rate-limited to ~20 req/min)
_LT_API_URL = "https://api.languagetool.org/v2/check"
_LT_TIMEOUT = 8  # seconds


# ---------------------------------------------------------------------------
# Vocabulary improvement suggestions
# ---------------------------------------------------------------------------

VOCAB_IMPROVEMENTS: Dict[str, List[str]] = {
    "good":      ["exceptional", "exemplary", "commendable", "proficient"],
    "bad":       ["suboptimal", "deficient", "detrimental", "unsatisfactory"],
    "big":       ["substantial", "significant", "extensive", "prominent"],
    "important": ["pivotal", "crucial", "paramount", "vital"],
    "show":      ["demonstrate", "illustrate", "exemplify", "manifest"],
    "use":       ["utilize", "harness", "deploy", "leverage"],
    "think":     ["perceive", "deliberate", "conclude", "postulate"],
    "help":      ["assist", "facilitate", "foster", "empower"],
    "make":      ["construct", "fabricate", "formulate", "devise"],
    "get":       ["obtain", "acquire", "procure", "attain"],
    "very":      ["extremely", "remarkably", "exceptionally", "considerably"],
    "many":      ["numerous", "abundant", "myriad", "extensive"],
    "often":     ["frequently", "consistently", "regularly", "repeatedly"],
    "start":     ["initiate", "commence", "inaugurate", "launch"],
    "end":       ["conclude", "finalise", "terminate", "complete"],
}

# ---------------------------------------------------------------------------
# Regex-based fallback rules (used when LanguageTool is unavailable)
# ---------------------------------------------------------------------------

_FALLBACK_RULES = [
    {
        "category": "Subject-Verb Agreement",
        "pattern": r'\b(he|she|it)\s+(have|do|go|say)\b',
        "replacement": None,
        "explanation": "Third-person singular subjects (he, she, it) require singular verb forms.",
    },
    {
        "category": "Subject-Verb Agreement",
        "pattern": r'\b(they|we|you)\s+(is|was)\b',
        "replacement": None,
        "explanation": "Plural subjects (they, we, you) require plural verb forms.",
    },
    {
        "category": "Article Usage",
        "pattern": r'\ba\s+([aeiouAEIOU]\w+)\b',
        "replacement": r'an \1',
        "explanation": "Use 'an' before words starting with a vowel sound.",
    },
    {
        "category": "Article Usage",
        "pattern": r'\ban\s+([bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]\w+)\b',
        "replacement": r'a \1',
        "explanation": "Use 'a' before words starting with a consonant sound.",
    },
    {
        "category": "Tenses & Aspect",
        "pattern": r'\bdid\s+(\w+ed|\w+s)\b',
        "replacement": None,
        "explanation": "'did' should be followed by the base form of the verb.",
    },
    {
        "category": "Prepositions",
        "pattern": r'\bdiscuss(ed|es|ing)?\s+about\b',
        "replacement": r'discuss\1',
        "explanation": "'Discuss' already means 'talk about'. Avoid using 'discuss about'.",
    },
    {
        "category": "Prepositions",
        "pattern": r'\bdepend(s|ed|ing)?\s+of\b',
        "replacement": r'depend\1 on',
        "explanation": "The correct preposition is 'depend on'.",
    },
    {
        "category": "Redundancy",
        "pattern": r'\brepeat\s+again\b',
        "replacement": "repeat",
        "explanation": "'Repeat' implies doing something again; 'again' is redundant.",
    },
    {
        "category": "Capitalization",
        "pattern": r'\bi\b',
        "replacement": "I",
        "explanation": "The pronoun 'I' should always be capitalized.",
    },
    {
        "category": "Spelling/Typo",
        "pattern": r'([a-zA-Z])\1{2,}',
        "replacement": r'\1',
        "explanation": "Avoid repeating a letter unnecessarily (e.g., 'hiii' to 'hi').",
    },
]

# LanguageTool rule-category -> our display category mapping
_LT_CATEGORY_MAP: Dict[str, str] = {
    "GRAMMAR":        "Grammar",
    "TYPOS":          "Spelling/Typo",
    "PUNCTUATION":    "Punctuation",
    "CASING":         "Capitalization",
    "STYLE":          "Style",
    "REDUNDANCY":     "Redundancy",
    "CONFUSED_WORDS": "Word Choice",
    "COLLOCATIONS":   "Collocations",
    "COMPOUNDING":    "Compounding",
    "TYPOGRAPHY":     "Typography",
    "MISC":           "Miscellaneous",
    "SEMANTICS":      "Semantics",
    "AGREEMENT":      "Subject-Verb Agreement",
    "ARTICLES":       "Article Usage",
    "PREPOSITIONS":   "Prepositions",
    "TENSE":          "Tenses & Aspect",
    "VERB":           "Tenses & Aspect",
}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _map_lt_category(lt_category: str) -> str:
    """Map a LanguageTool category id to a user-friendly display label."""
    return _LT_CATEGORY_MAP.get(lt_category.upper(), lt_category.capitalize())


def _apply_api_corrections(text: str, raw_matches: List[Dict[str, Any]]) -> str:
    """
    Apply LanguageTool API match replacements to *text* in a single pass
    (iterating from the end to keep offsets stable).
    raw_matches: list of match dicts from the LanguageTool JSON response.
    """
    corrected = text
    for m in sorted(raw_matches, key=lambda x: x.get("offset", 0), reverse=True):
        replacements = m.get("replacements", [])
        if replacements:
            best = replacements[0]["value"]
            offset = m.get("offset", 0)
            length = m.get("length", 0)
            corrected = corrected[:offset] + best + corrected[offset + length:]
    return corrected


def _vocab_suggestions(text: str) -> List[str]:
    """Return a deduplicated list of vocabulary improvement suggestions."""
    words = re.findall(r'\b\w+\b', text.lower())
    seen: set = set()
    suggestions: List[str] = []
    for word in words:
        if word in VOCAB_IMPROVEMENTS and word not in seen:
            seen.add(word)
            alt = VOCAB_IMPROVEMENTS[word][0]
            suggestions.append(
                f"Consider replacing '{word}' with a stronger term like '{alt}'."
            )
    return suggestions[:5]


def _calculate_scores(
    total_errors: int,
    word_count: int,
    unique_word_count: int,
) -> Dict[str, float]:
    """
    Compute grammar, vocabulary, and overall scores.

    Grammar score:
      - Proportional deduction per error relative to word count.
      - Clamped to [30, 100].

    Vocabulary score:
      - Lexical diversity (unique / total), scaled to [40, 100].
    """
    error_rate = total_errors / max(word_count, 1)
    grammar_score = max(30.0, round(100.0 - error_rate * 100.0, 1))

    diversity = unique_word_count / max(word_count, 1)
    vocab_score = min(100.0, round(40.0 + diversity * 60.0, 1))

    overall_score = round(grammar_score * 0.65 + vocab_score * 0.35, 1)

    return {
        "grammar_score":    grammar_score,
        "vocabulary_score": vocab_score,
        "overall_score":    overall_score,
    }


# ---------------------------------------------------------------------------
# Main GrammarCoach class
# ---------------------------------------------------------------------------

class GrammarCoach:
    """
    High-accuracy grammar analysis and correction coach.

    Primary  : LanguageTool public REST API (3000+ rules, no Java needed).
    Fallback : Curated regex rules when the API is unreachable.
    """

    def __init__(self) -> None:
        pass  # no local engine to initialise

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyse *text* for grammatical errors.

        Returns a dict with:
        - original_text       : the unmodified input
        - corrected_text      : best-effort corrected version
        - error_categories    : counts per category  {category: count}
        - detected_issues     : list of detailed issue dicts
        - suggestions         : vocabulary improvement hints
        - grammar_score       : 0-100
        - vocabulary_score    : 0-100
        - overall_score       : 0-100
        - feedback            : one-sentence human-readable summary
        - engine              : "languagetool-api" | "regex-fallback"
        """
        if not text or not text.strip():
            return self._empty_result()

        if _HTTP_AVAILABLE:
            api_result = self._analyze_with_api(text)
            if api_result is not None:
                return api_result

        return self._analyze_with_regex(text)

    def correct(self, text: str) -> str:
        """Return only the corrected text (convenience wrapper)."""
        return self.analyze(text)["corrected_text"]

    # ------------------------------------------------------------------
    # LanguageTool REST API path
    # ------------------------------------------------------------------

    def _analyze_with_api(self, text: str) -> Optional[Dict[str, Any]]:
        """Call the free LanguageTool API. Returns None on any error."""
        try:
            resp = _http.post(
                _LT_API_URL,
                data={"text": text, "language": "en-US"},
                timeout=_LT_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return None

        raw_matches = data.get("matches", [])

        error_categories: Dict[str, int] = {}
        detected_issues: List[Dict[str, Any]] = []

        for m in raw_matches:
            raw_cat = (
                m.get("rule", {}).get("category", {}).get("id", "MISC")
            )
            category = _map_lt_category(raw_cat)
            error_categories[category] = error_categories.get(category, 0) + 1

            offset = m.get("offset", 0)
            length = m.get("length", 0)
            replacements = [r["value"] for r in m.get("replacements", [])[:3]]

            detected_issues.append({
                "category":    category,
                "found":       text[offset: offset + length],
                "explanation": m.get("message", ""),
                "suggestions": replacements,
                "offset":      offset,
                "length":      length,
                "rule_id":     m.get("rule", {}).get("id", ""),
            })

        corrected_text = _apply_api_corrections(text, raw_matches)

        words = re.findall(r'\b\w+\b', text.lower())
        word_count = max(len(words), 1)
        unique_word_count = len(set(words))
        total_errors = len(raw_matches)

        scores = _calculate_scores(total_errors, word_count, unique_word_count)
        suggestions = _vocab_suggestions(text)
        feedback = self._build_feedback(
            total_errors, error_categories, scores["grammar_score"]
        )

        return {
            "original_text":    text,
            "corrected_text":   corrected_text,
            "error_categories": error_categories,
            "detected_issues":  detected_issues,
            "suggestions":      suggestions,
            "grammar_score":    scores["grammar_score"],
            "vocabulary_score": scores["vocabulary_score"],
            "overall_score":    scores["overall_score"],
            "feedback":         feedback,
            "engine":           "languagetool-api",
        }

    # ------------------------------------------------------------------
    # Regex fallback path
    # ------------------------------------------------------------------

    def _analyze_with_regex(self, text: str) -> Dict[str, Any]:
        error_categories: Dict[str, int] = {}
        detected_issues: List[Dict[str, Any]] = []
        corrected_text = text

        for rule in _FALLBACK_RULES:
            pattern = rule["pattern"]
            flags = re.IGNORECASE
            found = list(re.finditer(pattern, text, flags=flags))
            if found:
                cat = rule["category"]
                error_categories[cat] = error_categories.get(cat, 0) + len(found)
                for m in found:
                    detected_issues.append({
                        "category":    cat,
                        "found":       m.group(0),
                        "explanation": rule["explanation"],
                        "suggestions": [],
                        "offset":      m.start(),
                        "length":      len(m.group(0)),
                        "rule_id":     "REGEX",
                    })
                if rule["replacement"] is not None:
                    corrected_text = re.sub(
                        pattern, rule["replacement"], corrected_text, flags=flags
                    )

        words = re.findall(r'\b\w+\b', text.lower())
        word_count = max(len(words), 1)
        unique_word_count = len(set(words))
        total_errors = sum(error_categories.values())

        scores = _calculate_scores(total_errors, word_count, unique_word_count)
        suggestions = _vocab_suggestions(text)
        feedback = self._build_feedback(
            total_errors, error_categories, scores["grammar_score"]
        )

        return {
            "original_text":    text,
            "corrected_text":   corrected_text,
            "error_categories": error_categories,
            "detected_issues":  detected_issues,
            "suggestions":      suggestions,
            "grammar_score":    scores["grammar_score"],
            "vocabulary_score": scores["vocabulary_score"],
            "overall_score":    scores["overall_score"],
            "feedback":         feedback,
            "engine":           "regex-fallback",
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_feedback(
        total_errors: int,
        error_categories: Dict[str, int],
        grammar_score: float,
    ) -> str:
        if total_errors == 0:
            return (
                "Excellent! No grammatical issues were detected. "
                "Your writing is polished and accurate."
            )
        top_category = max(error_categories, key=lambda k: error_categories[k])
        if grammar_score >= 85:
            level = "minor"
        elif grammar_score >= 65:
            level = "moderate"
        else:
            level = "significant"
        return (
            f"Found {total_errors} {level} grammatical issue(s). "
            f"Main area to improve: {top_category}. "
            f"Review the detected issues above for detailed corrections."
        )

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            "original_text":    "",
            "corrected_text":   "",
            "error_categories": {},
            "detected_issues":  [],
            "suggestions":      [],
            "grammar_score":    100.0,
            "vocabulary_score": 100.0,
            "overall_score":    100.0,
            "feedback":         "No text provided.",
            "engine":           "none",
        }


# ---------------------------------------------------------------------------
# Module-level singleton (imported by API routes)
# ---------------------------------------------------------------------------

grammar_coach = GrammarCoach()
