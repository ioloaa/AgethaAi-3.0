"""
Управление мутами чатов и пользователей
"""
import logging
from typing import Dict, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class MuteManager:
    def __init__(self):
        self._muted_chats: Set[int] = set()
        self._muted_users: Dict[int, Set[int]] = defaultdict(set)

    def mute_chat(self, chat_id: int):
        self._muted_chats.add(chat_id)
        logger.info(f"Чат {chat_id} замьючен")

    def unmute_chat(self, chat_id: int):
        self._muted_chats.discard(chat_id)
        logger.info(f"Чат {chat_id} размьючен")

    def is_muted(self, chat_id: int) -> bool:
        return chat_id in self._muted_chats

    def mute_user(self, chat_id: int, user_id: int):
        self._muted_users[chat_id].add(user_id)

    def unmute_user(self, chat_id: int, user_id: int):
        self._muted_users[chat_id].discard(user_id)

    def is_user_muted(self, chat_id: int, user_id: int) -> bool:
        return user_id in self._muted_users[chat_id]

    @property
    def muted_chats_count(self) -> int:
        return len(self._muted_chats)


mute_manager = MuteManager()
