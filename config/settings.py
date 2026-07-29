"""
Конфигурация бота AgethaAi
Работает с секретами платформы (Railway, Heroku) или с .env
"""
import os
from pathlib import Path
from typing import Set, Optional, List

# Если есть .env — загрузим (для локальной разработки)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass


class Settings:
    """Централизованная конфигурация"""

    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    BOT_NAME: str = os.getenv("BOT_NAME", "Агета")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "groq").lower()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    CEREBRAS_MODEL: str = os.getenv("CEREBRAS_MODEL", "llama-3.3-70b")
    GROUP_CHAT_ENABLED: bool = os.getenv("GROUP_CHAT_ENABLED", "yes").lower() in ("yes", "true", "1")
    MENTION_REQUIRED: bool = os.getenv("MENTION_REQUIRED", "yes").lower() in ("yes", "true", "1")
    ANTI_FLOOD_SECONDS: float = float(os.getenv("ANTI_FLOOD_SECONDS", "2"))
    MAX_MESSAGES_PER_MINUTE: int = int(os.getenv("MAX_MESSAGES_PER_MINUTE", "30"))
    MAX_HISTORY: int = int(os.getenv("MAX_HISTORY", "50"))
    ADMIN_IDS: Set[int] = set()
    ALLOWED_TOPIC_ID: Optional[int] = None

    @classmethod
    def load(cls):
        topic_str = os.getenv("ALLOWED_TOPIC_ID", "").strip()
        if topic_str:
            try:
                cls.ALLOWED_TOPIC_ID = int(topic_str)
            except ValueError:
                cls.ALLOWED_TOPIC_ID = None

        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            cls.ADMIN_IDS = {
                int(x.strip()) for x in admin_ids_str.split(",")
                if x.strip().isdigit()
            }

        # Если есть config.txt рядом — подхватим (опционально)
        config_path = Path(__file__).resolve().parent.parent / "config.txt"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key == "ALLOWED_TOPIC_ID" and value:
                            try:
                                cls.ALLOWED_TOPIC_ID = int(value)
                            except ValueError:
                                pass
                        elif key == "ADMIN_IDS" and value:
                            cls.ADMIN_IDS.update(
                                int(x.strip()) for x in value.split(",")
                                if x.strip().isdigit()
                            )
        return cls

    @classmethod
    def get_groq_keys(cls) -> List[str]:
        keys = []
        for i in range(1, 11):
            key_name = f"GROQ_API_KEY_{i}" if i > 1 else "GROQ_API_KEY"
            key = os.getenv(key_name, "").strip()
            if key:
                keys.append(key)
        return keys

    @classmethod
    def get_gemini_key(cls) -> Optional[str]:
        key = os.getenv("GEMINI_API_KEY", "").strip()
        return key if key else None

    @classmethod
    def get_cerebras_keys(cls) -> List[str]:
        keys = []
        for i in range(1, 6):
            key_name = f"CEREBRAS_API_KEY_{i}" if i > 1 else "CEREBRAS_API_KEY"
            key = os.getenv(key_name, "").strip()
            if key:
                keys.append(key)
        return keys


settings = Settings.load()
