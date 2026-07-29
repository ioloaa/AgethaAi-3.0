"""
System Monitor — мониторинг состояния системы/телефона
"""
from datetime import datetime
from typing import Dict, Optional


class SystemMonitor:
    _state: Dict = {}
    _last_update: str = ""

    @classmethod
    def update_state(cls, state: Dict):
        cls._state = state
        cls._last_update = datetime.now().isoformat()
        cls._state["last_update"] = cls._last_update

    @classmethod
    def get_state(cls) -> Optional[Dict]:
        if not cls._state:
            try:
                import platform
                return {
                    "platform": platform.system(),
                    "python_version": platform.python_version(),
                    "last_update": datetime.now().isoformat(),
                    "note": "Монитор не запущен. Запусти bot_monitor.py для полной статистики."
                }
            except Exception:
                return None
        return dict(cls._state)

    @classmethod
    def get_formatted_state(cls) -> str:
        state = cls.get_state()
        if not state:
            return "⚠️ Нет данных о состоянии системы."
        lines = ["📱 *Состояние системы*", ""]
        for key, value in state.items():
            if key == "last_update":
                lines.append(f"🕐 *Последнее обновление:* `{value}`")
            elif isinstance(value, (int, float)):
                lines.append(f"• {key}: `{value:.2f}`" if isinstance(value, float) else f"• {key}: `{value}`")
            else:
                lines.append(f"• {key}: `{value}`")
        return "\n".join(lines)
