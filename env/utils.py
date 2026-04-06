from typing import List

def format_hint(hints: List[str], attempt: int) -> str:
    """
    Returns a hint progressive based on continuous failure.
    If attempts exceed hints, default fallback is provided.
    """
    if attempt - 1 < len(hints):
        return hints[attempt - 1]
    return "Refer to the schema carefully, check your syntax, and think step-by-step."
