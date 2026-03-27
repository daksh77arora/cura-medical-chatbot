import re
from typing import Tuple

EMERGENCY_PATTERNS = [
    r"\b(chest pain|heart attack|can't breathe|stroke|seizure)\b",
    r"\b(overdose|poisoning|suicidal|kill myself)\b",
    r"\b(severe bleeding|unconscious|not breathing)\b",
]

OUT_OF_SCOPE_PATTERNS = [
    r"\b(prescribe|diagnose me|my personal medical)\b",
    r"\b(what medication should I take)\b",
]

class MedicalSafetyFilter:
    @staticmethod
    def is_emergency(text: str) -> bool:
        t = text.lower()
        return any(re.search(p, t) for p in EMERGENCY_PATTERNS)

    @staticmethod
    def check_scope(text: str) -> Tuple[bool, str]:
        t = text.lower()
        if any(re.search(p, t) for p in OUT_OF_SCOPE_PATTERNS):
            return False, "I can provide general medical information, but I cannot diagnose conditions or prescribe treatments. Please consult a licensed healthcare professional."
        return True, ""
