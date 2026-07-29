"""
Вспомогательные функции
"""
import random


MOOD_SYMBOLS = {
    "glitch": "~",
    "violent": "!",
    "dark": "...",
    "playful": "~",
    "observant": "...",
    "kind": "",
    "neutral": "",
}


def format_mood_text(text: str, mood: str, chance: float = 0.15) -> str:
    symbol = MOOD_SYMBOLS.get(mood, "")
    if symbol and random.random() < chance:
        return f"{symbol} {text}"
    return text


def is_fact_request(text: str) -> bool:
    lower = text.lower()
    keywords = ["факт", "факты", "fact", "интересно", "знаешь ли", "расскажи"]
    return any(word in lower for word in keywords) and len(text) < 50
