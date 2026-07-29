"""
Управление историей сообщений чатов
"""
import time
from typing import Dict, List
from collections import defaultdict

from config.settings import settings


class ChatHistory:
    def __init__(self, max_history: int = None):
        self.max_history = max_history or settings.MAX_HISTORY
        self._history: Dict[int, List[Dict]] = defaultdict(list)

    def add(self, chat_id: int, user_id: int, user_name: str,
            role: str, content: str, topic: str = "general"):
        self._history[chat_id].append({
            "user_id": user_id,
            "name": user_name,
            "role": role,
            "content": content,
            "topic": topic,
            "timestamp": time.time()
        })
        if len(self._history[chat_id]) > self.max_history:
            self._history[chat_id] = self._history[chat_id][-self.max_history:]

    def get(self, chat_id: int) -> List[Dict]:
        return list(self._history.get(chat_id, []))

    def clear(self, chat_id: int):
        self._history[chat_id] = []

    def get_unique_users(self, chat_id: int, limit: int = 50) -> dict:
        users = {}
        for msg in reversed(self._history.get(chat_id, [])[-limit:]):
            uid = msg.get("user_id")
            if uid and uid != 0:
                users[uid] = msg.get("name", "Кто-то")
        return users

    @property
    def total_chats(self) -> int:
        return len(self._history)

    @property
    def total_messages(self) -> int:
        return sum(len(h) for h in self._history.values())


chat_history = ChatHistory()
