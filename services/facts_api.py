"""
Facts API — получение интересных фактов
"""
import random
import logging
import requests

logger = logging.getLogger(__name__)


class FactsAPI:
    ENDPOINTS = {
        "numbers": "http://numbersapi.com/{}/trivia",
        "useless": "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en",
        "chuck": "https://api.chucknorris.io/jokes/random",
        "year": "http://numbersapi.com/{}/year",
        "math": "http://numbersapi.com/{}/math",
        "date": "http://numbersapi.com/{}/date",
    }

    FALLBACK = [
        "Осьминоги имеют три сердца и синюю кровь!",
        "Бананы — это ягоды, а клубника — нет!",
        "Пчёлы могут распознавать человеческие лица!",
        "В космосе нет звука — там нет воздуха для передачи колебаний!",
        "Акулы существовали ещё до появления деревьев!",
        "У жирафа язык может быть длиной до 45 см!",
        "Слоны — единственные млекопитающие, которые не могут прыгать!",
        "Бабочки чувствуют вкус своими лапками!",
    ]

    @classmethod
    def get_random_fact(cls, category: str = "random") -> str | None:
        try:
            if category in ("random", "trivia"):
                num = random.randint(1, 9999)
                url = cls.ENDPOINTS["numbers"].format(num)
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    return f"Знаешь ли... {resp.text}"

            elif category == "useless":
                resp = requests.get(cls.ENDPOINTS["useless"], timeout=10)
                if resp.status_code == 200:
                    return f"Бесполезный факт: {resp.json().get('text', 'Не удалось получить факт')}"

            elif category == "chuck":
                resp = requests.get(cls.ENDPOINTS["chuck"], timeout=10)
                if resp.status_code == 200:
                    return f"Факт о Чаке Норрисе: {resp.json().get('value', 'Не удалось получить факт')}"

            elif category == "year":
                year = random.randint(1000, 2026)
                url = cls.ENDPOINTS["year"].format(year)
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    return f"В {year} году... {resp.text}"

            elif category == "math":
                num = random.randint(1, 1000)
                url = cls.ENDPOINTS["math"].format(num)
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    return f"Математический факт: {resp.text}"

            elif category == "date":
                month = random.randint(1, 12)
                day = random.randint(1, 28)
                url = cls.ENDPOINTS["date"].format(f"{month}/{day}")
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    return f"В этот день... {resp.text}"

        except Exception as e:
            logger.error(f"Ошибка получения факта: {e}")
        return None

    @classmethod
    def get_any_fact(cls) -> str:
        cats = ["numbers", "useless", "year", "math", "date"]
        random.shuffle(cats)
        for cat in cats:
            fact = cls.get_random_fact(cat)
            if fact:
                return fact
        return random.choice(cls.FALLBACK)
