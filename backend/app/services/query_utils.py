import re

_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

_PATTERNS = [
    re.compile(r"\btop\s+(\d+|[a-z]+)\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\s+best\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\s+(?:results?|records?|movies?|shows?|titles?|matches?)\b", re.IGNORECASE),
]

MAX_TOP_K = 25


def detect_top_k(query: str, default: int = 1) -> int:
    """Derive top_k from phrases like 'top three' or '5 best movies'.

    Falls back to `default` (1) when the query doesn't request a count.
    """
    for pattern in _PATTERNS:
        match = pattern.search(query)
        if not match:
            continue
        token = match.group(1).lower()
        value = int(token) if token.isdigit() else _NUMBER_WORDS.get(token)
        if value:
            return max(1, min(MAX_TOP_K, value))
    return default
