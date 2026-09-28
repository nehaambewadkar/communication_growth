import random
from typing import Dict, List, Any

RECOMMENDED_EXERCISES = {
    "Fluency": [
        {"title": "Filler-Free Challenge", "type": "Timed Speaking", "duration": "2 mins", "description": "Speak for 2 minutes on a random topic keeping filler words below 2%"},
        {"title": "Pacing & Speed Control", "type": "Speech Rate", "duration": "3 mins", "description": "Maintain a target 130-150 WPM pace without rushing"}
    ],
    "Vocabulary": [
        {"title": "Lexical Elevation Exercise", "type": "Vocabulary", "duration": "5 mins", "description": "Replace 5 basic words with advanced context-appropriate alternatives"},
        {"title": "Storytelling with Target Words", "type": "Storytelling", "duration": "3 mins", "description": "Construct a coherent story incorporating 3 new vocabulary terms"}
    ],
    "Grammar": [
        {"title": "Tense & Agreement Sprint", "type": "Writing Coach", "duration": "5 mins", "description": "Rewrite 5 complex sentences fixing subject-verb agreement and tense shifts"},
        {"title": "Professional Email Polish", "type": "Writing Practice", "duration": "5 mins", "description": "Refine informal text into polished corporate communication"}
    ],
    "Clarity": [
        {"title": "Concise Summary Drill", "type": "Impromptu", "duration": "2 mins", "description": "Explain a complex concept in under 90 seconds using structured points"},
        {"title": "Picture Description Practice", "type": "Visual Speaking", "duration": "3 mins", "description": "Describe an abstract image clearly focusing on visual spatial relationships"}
    ],
    "Confidence": [
        {"title": "Elevator Pitch Simulator", "type": "Self Introduction", "duration": "1 min", "description": "Deliver a 60-second professional self-introduction with strong prosody"},
        {"title": "Debate Rebuttal Challenge", "type": "Debate", "duration": "3 mins", "description": "Deliver a compelling rebuttal counter-arguing an opposing AI position"}
    ]
}

class AdaptiveLearningEngine:
    def get_recommendation(self, weak_area: str, user_level: str = "Intermediate") -> Dict[str, Any]:
        """
        Generates a targeted exercise recommendation based on identified weak area.
        """
        exercises = RECOMMENDED_EXERCISES.get(weak_area, RECOMMENDED_EXERCISES["Fluency"])
        chosen = random.choice(exercises)
        return {
            "exercise_type": chosen["type"],
            "title": chosen["title"],
            "description": chosen["description"],
            "duration": chosen["duration"],
            "target_weakness": weak_area,
            "recommended_difficulty": "Adaptive (" + user_level + ")"
        }

    def generate_7_day_plan(self, weak_area: str, user_type: str = "Student") -> List[Dict[str, Any]]:
        """
        Generates a personalized 7-day practice schedule tailored to goals and weaknesses.
        """
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        plan = []
        for i, day in enumerate(days):
            focus = weak_area if i % 2 == 0 else ("Vocabulary" if i % 3 == 0 else "Confidence")
            ex_list = RECOMMENDED_EXERCISES.get(focus, RECOMMENDED_EXERCISES["Fluency"])
            ex = ex_list[i % len(ex_list)]
            plan.append({
                "day": day,
                "focus_area": focus,
                "activity": ex["title"],
                "type": ex["type"],
                "duration": ex["duration"]
            })
        return plan

adaptive_engine = AdaptiveLearningEngine()
