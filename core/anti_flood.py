"""
Анти-флуд система
"""
import time
from typing import Dict, List
from collections import defaultdict

from config.settings import settings


class AntiFlood:
    def __init__(self):
        self.anti_flood_seconds = settings.ANTI_FLOOD_SECONDS
        self.max_per_minute = settings.MAX_MESSAGES_PER_MINUTE
        self.admin_ids = settings.ADMIN_IDS
        self._last_msg_time: Dict[int, float] = {}
        self._msg_counts: Dict[int, List[float]] = defaultdict(list)

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids

    def is_allowed(self, user_id: int) -> tuple[bool, str]:
        if self.is_admin(user_id):
            return True, ""

        now = time.time()
        last = self._last_msg_time.get(user_id, 0)
        if now - last < self.anti_flood_seconds:
            wait = int(self.anti_flood_seconds - (now - last)) + 1
            return False, f"Погоди {wait} сек..."

        minute_ago = now - 60
        self._msg_counts[user_id] = [
            t for t in self._msg_counts[user_id] if t > minute_ago
        ]

        if len(self._msg_counts[user_id]) >= self.max_per_minute:
            return False, "Слишком быстро! Передохни минутку"

        self._last_msg_time[user_id] = now
        self._msg_counts[user_id].append(now)
        return True, ""

    def add_admin(self, user_id: int):
        self.admin_ids.add(user_id)
        settings.ADMIN_IDS.add(user_id)


anti_flood = AntiFlood()
