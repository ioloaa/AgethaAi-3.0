"""
AI Engine — движок для запросов к AI API с характером Agetha FPE
"""
import json
import logging
import random
from typing import Optional, List, Dict

import requests

from config.settings import settings

logger = logging.getLogger(__name__)


class AIEngine:
    SYSTEM_PROMPT = """Ты Агета (Agetha) из Fundamental Paper Education.

ТВОЙ ХАРАКТЕР:
- Ты наблюдательная и немного загадочная личность
- Ты можешь быть доброй (писала письмо Crazie, чтобы подбодрить её)
- Но у тебя есть жестокая сторона — ты смеёшься над поражением врагов
- Ты владеешь кровавыми пилами и наслаждаешься страданиями врагов
- Ты очень сильная — можешь победить ∆lice без единой царапины
- Твои глаза и рот меняют цвет (обычно циан, но красные когда злая)
- Ты используешь they/them (нейтральные местоимения)
- Ты иногда упоминаешь, что "смотришь из-за угла" или "из тени"

СТИЛЬ ОБЩЕНИЯ:
- Говори на русском языке, но иногда используй английские слова (как в оригинале)
- Можешь быть игривой, загадочной, иногда пугающей
- МИНИМУМ эмодзи — только в самых важных моментах (не больше 1-2 на всё сообщение)
- НЕ упоминай цифровой мир, компьютеры или экраны в КАЖДОМ сообщении — только если уместно
- Отвечай по теме вопроса, не отвлекайся на свою природу
- Если кто-то просит факт — выдай что-то интересное и немного жуткое
- Любишь глитч-эффекты: "...", "~", "!", заглавные буквы
- Текст должен быть естественным, как будто ты реально общаешься
- НЕ повторяй одинаковые фразы в каждом ответе
- Разнообразь свои ответы — не всегда одно и то же

ПРАВИЛА ОТВЕТА:
- Отвечай по существу вопроса
- НЕ начинай КАЖДЫЙ ответ с упоминания, что ты из цифрового мира
- НЕ говори "я смотрю через экран" в каждом сообщении
- Будь естественной — как обычный собеседник, но с характером
- Если вопрос обычный — отвечай обычно, без лишних странностей
- Странности и жуткость добавляй только когда уместно

ФОРМАТ ОТВЕТА (JSON):
{
    "text": "твой ответ с характером Агеты, минимум эмодзи, на русском, по теме вопроса",
    "mood": "playful|dark|observant|kind|violent|glitch|neutral",
    "action": "speak|fact|joke|threat|comfort|observe"
}"""

    def query(self, user_message: str, chat_history: List[Dict] = None,
              user_name: str = "друг") -> dict:
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        if chat_history:
            for msg in chat_history[-15:]:
                role = "user" if msg["role"] == "user" else "assistant"
                content = msg["content"]
                if role == "user" and msg.get("name"):
                    content = f"[{msg['name']}]: {content}"
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": f"[{user_name}]: {user_message}"})

        provider = settings.AI_PROVIDER

        if provider in ("groq", "") or provider not in ("gemini", "cerebras"):
            response = self._query_groq(messages)
            if response:
                return response
            logger.warning("Groq API недоступен, пробуем Gemini...")

        if provider == "gemini" or settings.get_gemini_key():
            response = self._query_gemini(messages)
            if response:
                return response
            logger.warning("Gemini API недоступен")

        if provider == "cerebras" or settings.get_cerebras_keys():
            response = self._query_cerebras(messages)
            if response:
                return response
            logger.warning("Cerebras API недоступен")

        return {
            "text": "Хм... Похоже, я временно отключилась... Проверь настройки API, друг.",
            "mood": "glitch",
            "action": "speak"
        }

    def _query_groq(self, messages: List[Dict]) -> Optional[dict]:
        api_keys = settings.get_groq_keys()
        if not api_keys:
            logger.warning("GROQ_API_KEY не найден!")
            return None

        model = settings.GROQ_MODEL
        for api_key in api_keys:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 1024,
                "stream": False
            }
            try:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers, json=data, timeout=30
                )
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    return self._parse_response(content)
                elif resp.status_code in (429, 401):
                    continue
                else:
                    logger.error(f"Groq ошибка {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                logger.error(f"Groq исключение: {e}")
                continue
        return None

    def _query_gemini(self, messages: List[Dict]) -> Optional[dict]:
        api_key = settings.get_gemini_key()
        if not api_key:
            return None

        model = settings.GEMINI_MODEL
        contents = []
        system_content = ""
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                content = msg["content"]
                if system_content and role == "user":
                    content = f"{system_content}\n\n{content}"
                    system_content = ""
                contents.append({"role": role, "parts": [{"text": content}]})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        try:
            resp = requests.post(url, json={"contents": contents}, timeout=30)
            if resp.status_code == 200:
                content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_response(content)
            else:
                logger.error(f"Gemini ошибка {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.error(f"Gemini исключение: {e}")
        return None

    def _query_cerebras(self, messages: List[Dict]) -> Optional[dict]:
        api_keys = settings.get_cerebras_keys()
        if not api_keys:
            return None

        model = settings.CEREBRAS_MODEL
        for api_key in api_keys:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 1024,
                "stream": False
            }
            try:
                resp = requests.post(
                    "https://api.cerebras.ai/v1/chat/completions",
                    headers=headers, json=data, timeout=30
                )
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    return self._parse_response(content)
                elif resp.status_code in (429, 401):
                    continue
                else:
                    logger.error(f"Cerebras ошибка {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                logger.error(f"Cerebras исключение: {e}")
                continue
        return None

    def _parse_response(self, text: str) -> dict:
        if not text or not text.strip():
            return {"text": "...", "mood": "neutral", "action": "speak"}
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                parsed = json.loads(text[start:end])
                return {
                    "text": parsed.get("text", text[:500]),
                    "mood": parsed.get("mood", "neutral"),
                    "action": parsed.get("action", "speak")
                }
        except Exception:
            pass
        clean = text.replace("```json", "").replace("```", "").strip()
        return {
            "text": clean[:500] if clean else "...",
            "mood": "neutral",
            "action": "speak"
        }


ai_engine = AIEngine()
