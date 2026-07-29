"""
Управление банами пользователей
"""
import time
import logging
from typing import Dict, List, Set, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class BanManager:
    def __init__(self):
        self._banned_users: Set[int] = set()
        self._chat_bans: Dict[int, Set[int]] = defaultdict(set)
        self._ban_history: List[Dict] = []

    def ban_user(self, user_id: int, chat_id: Optional[int] = None,
                 admin_id: Optional[int] = None, reason: str = "") -> bool:
        if chat_id is None:
            self._banned_users.add(user_id)
        else:
            self._chat_bans[chat_id].add(user_id)

        self._ban_history.append({
            "user_id": user_id,
            "chat_id": chat_id,
            "admin_id": admin_id,
            "action": "ban",
            "reason": reason,
            "timestamp": time.time()
        })
        return True

    def unban_user(self, user_id: int, chat_id: Optional[int] = None) -> bool:
        if chat_id is None:
            self._banned_users.discard(user_id)
        else:
            self._chat_bans[chat_id].discard(user_id)

        self._ban_history.append({
            "user_id": user_id,
            "chat_id": chat_id,
            "action": "unban",
            "timestamp": time.time()
        })
        return True

    def is_banned(self, user_id: int, chat_id: Optional[int] = None) -> bool:
        if user_id in self._banned_users:
            return True
        if chat_id and user_id in self._chat_bans.get(chat_id, set()):
            return True
        return False

    def get_banned_list(self, chat_id: Optional[int] = None) -> List[Dict]:
        banned = []

        for user_id in self._banned_users:
            banned.append({
                "user_id": user_id,
                "chat_id": None,
                "type": "global",
                "timestamp": self._get_ban_time(user_id, None)
            })

        if chat_id:
            for user_id in self._chat_bans.get(chat_id, set()):
                banned.append({
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "type": "chat",
                    "timestamp": self._get_ban_time(user_id, chat_id)
                })
        else:
            for cid, users in self._chat_bans.items():
                for user_id in users:
                    banned.append({
                        "user_id": user_id,
                        "chat_id": cid,
                        "type": "chat",
                        "timestamp": self._get_ban_time(user_id, cid)
                    })

        return banned

    def get_recent_bans(self, limit: int = 10) -> List[Dict]:
        return [r for r in self._ban_history if r["action"] == "ban"][-limit:]

    def _get_ban_time(self, user_id: int, chat_id: Optional[int]) -> float:
        for record in reversed(self._ban_history):
            if (record["user_id"] == user_id and
                record["chat_id"] == chat_id and
                record["action"] == "ban"):
                return record["timestamp"]
        return 0.0

    @property
    def global_banned_count(self) -> int:
        return len(self._banned_users)

    @property
    def total_chat_bans(self) -> int:
        return sum(len(users) for users in self._chat_bans.values())


ban_manager = BanManager()
