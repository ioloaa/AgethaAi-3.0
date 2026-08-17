# config/settings.py
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        # ============================================
        # TELEGRAM
        # ============================================
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.BOT_NAME = os.getenv('BOT_NAME', 'AgethaBot')
        
        # ============================================
        # AI PROVIDER
        # ============================================
        self.AI_PROVIDER = os.getenv('AI_PROVIDER', 'deepseek').lower()
        
        # ============================================
        # GROQ
        # ============================================
        self.GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        self.GROQ_API_KEY_2 = os.getenv('GROQ_API_KEY_2')
        self.GROQ_API_KEY_3 = os.getenv('GROQ_API_KEY_3')
        self.GROQ_API_KEY_4 = os.getenv('GROQ_API_KEY_4')
        self.GROQ_API_KEY_5 = os.getenv('GROQ_API_KEY_5')
        self.GROQ_MODEL = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
        
        # ============================================
        # GEMINI
        # ============================================
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        self.GEMINI_API_KEY_2 = os.getenv('GEMINI_API_KEY_2')
        self.GEMINI_API_KEY_3 = os.getenv('GEMINI_API_KEY_3')
        self.GEMINI_API_KEY_4 = os.getenv('GEMINI_API_KEY_4')
        self.GEMINI_API_KEY_5 = os.getenv('GEMINI_API_KEY_5')
        self.GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')
        
        # ============================================
        # CEREBRAS
        # ============================================
        self.CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
        self.CEREBRAS_API_KEY_2 = os.getenv('CEREBRAS_API_KEY_2')
        self.CEREBRAS_API_KEY_3 = os.getenv('CEREBRAS_API_KEY_3')
        self.CEREBRAS_API_KEY_4 = os.getenv('CEREBRAS_API_KEY_4')
        self.CEREBRAS_API_KEY_5 = os.getenv('CEREBRAS_API_KEY_5')
        self.CEREBRAS_MODEL = os.getenv('CEREBRAS_MODEL', 'llama3.1-8b')
        
        # ============================================
        # MISTRAL AI
        # ============================================
        self.MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
        self.MISTRAL_API_KEY_2 = os.getenv('MISTRAL_API_KEY_2')
        self.MISTRAL_API_KEY_3 = os.getenv('MISTRAL_API_KEY_3')
        self.MISTRAL_API_KEY_4 = os.getenv('MISTRAL_API_KEY_4')
        self.MISTRAL_API_KEY_5 = os.getenv('MISTRAL_API_KEY_5')
        self.MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-large-latest')
        
        # ============================================
        # DEEPSEEK
        # ============================================
        self.DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
        self.DEEPSEEK_API_KEY_2 = os.getenv('DEEPSEEK_API_KEY_2')
        self.DEEPSEEK_API_KEY_3 = os.getenv('DEEPSEEK_API_KEY_3')
        self.DEEPSEEK_API_KEY_4 = os.getenv('DEEPSEEK_API_KEY_4')
        self.DEEPSEEK_API_KEY_5 = os.getenv('DEEPSEEK_API_KEY_5')
        self.DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        self.DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        
        # ============================================
        # OPENAI (опционально)
        # ============================================
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        # ============================================
        # ANTHROPIC (опционально)
        # ============================================
        self.ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
        self.ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307')
        
        # ============================================
        # ADMIN SETTINGS
        # ============================================
        admin_ids = os.getenv('ADMIN_IDS', '')
        self.ADMIN_IDS = [int(x.strip()) for x in admin_ids.split(',') if x.strip()]
        
        # Owner ID (первый админ или отдельный)
        owner_id = os.getenv('OWNER_ID', '')
        self.OWNER_ID = int(owner_id) if owner_id else (self.ADMIN_IDS[0] if self.ADMIN_IDS else None)
        
        # ============================================
        # GROUP SETTINGS
        # ============================================
        self.GROUP_CHAT_ENABLED = os.getenv('GROUP_CHAT_ENABLED', 'true').lower() == 'true'
        self.MENTION_REQUIRED = os.getenv('MENTION_REQUIRED', 'true').lower() == 'true'
        allowed_topic = os.getenv('ALLOWED_TOPIC_ID')
        self.ALLOWED_TOPIC_ID = int(allowed_topic) if allowed_topic else None
        
        # ============================================
        # ANTI-FLOOD
        # ============================================
        self.ANTI_FLOOD_SECONDS = int(os.getenv('ANTI_FLOOD_SECONDS', 15))
        self.MAX_MESSAGES_PER_MINUTE = int(os.getenv('MAX_MESSAGES_PER_MINUTE', 5))
        self.MAX_HISTORY = int(os.getenv('MAX_HISTORY', 5))
        
        # ============================================
        # LOGGING
        # ============================================
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # ============================================
    # GETTERS FOR API KEYS
    # ============================================
    
    def get_groq_keys(self) -> List[str]:
        """Получить все ключи Groq"""
        keys = [
            self.GROQ_API_KEY,
            self.GROQ_API_KEY_2,
            self.GROQ_API_KEY_3,
            self.GROQ_API_KEY_4,
            self.GROQ_API_KEY_5
        ]
        return [k.strip() for k in keys if k and k.strip()]
    
    def get_gemini_keys(self) -> List[str]:
        """Получить все ключи Gemini"""
        keys = [
            self.GEMINI_API_KEY,
            self.GEMINI_API_KEY_2,
            self.GEMINI_API_KEY_3,
            self.GEMINI_API_KEY_4,
            self.GEMINI_API_KEY_5
        ]
        return [k.strip() for k in keys if k and k.strip()]
    
    def get_gemini_key(self) -> Optional[str]:
        """Получить первый ключ Gemini (для совместимости)"""
        keys = self.get_gemini_keys()
        return keys[0] if keys else None
    
    def get_cerebras_keys(self) -> List[str]:
        """Получить все ключи Cerebras"""
        keys = [
            self.CEREBRAS_API_KEY,
            self.CEREBRAS_API_KEY_2,
            self.CEREBRAS_API_KEY_3,
            self.CEREBRAS_API_KEY_4,
            self.CEREBRAS_API_KEY_5
        ]
        return [k.strip() for k in keys if k and k.strip()]
    
    def get_mistral_keys(self) -> List[str]:
        """Получить все ключи Mistral"""
        keys = [
            self.MISTRAL_API_KEY,
            self.MISTRAL_API_KEY_2,
            self.MISTRAL_API_KEY_3,
            self.MISTRAL_API_KEY_4,
            self.MISTRAL_API_KEY_5
        ]
        return [k.strip() for k in keys if k and k.strip()]
    
    def get_deepseek_keys(self) -> List[str]:
        """Получить все ключи DeepSeek"""
        keys = [
            self.DEEPSEEK_API_KEY,
            self.DEEPSEEK_API_KEY_2,
            self.DEEPSEEK_API_KEY_3,
            self.DEEPSEEK_API_KEY_4,
            self.DEEPSEEK_API_KEY_5
        ]
        return [k.strip() for k in keys if k and k.strip()]
    
    def get_openai_keys(self) -> List[str]:
        """Получить все ключи OpenAI"""
        keys = [self.OPENAI_API_KEY]
        return [k.strip() for k in keys if k and k.strip()]
    
    def get_anthropic_keys(self) -> List[str]:
        """Получить все ключи Anthropic"""
        keys = [self.ANTHROPIC_API_KEY]
        return [k.strip() for k in keys if k and k.strip()]
    
    # ============================================
    # PROVIDER STATUS
    # ============================================
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Получить статус всех провайдеров"""
        return {
            "groq": bool(self.get_groq_keys()),
            "gemini": bool(self.get_gemini_keys()),
            "cerebras": bool(self.get_cerebras_keys()),
            "mistral": bool(self.get_mistral_keys()),
            "deepseek": bool(self.get_deepseek_keys()),
            "openai": bool(self.get_openai_keys()),
            "anthropic": bool(self.get_anthropic_keys()),
        }
    
    def get_provider_keys_count(self) -> Dict[str, int]:
        """Получить количество ключей для каждого провайдера"""
        return {
            "groq": len(self.get_groq_keys()),
            "gemini": len(self.get_gemini_keys()),
            "cerebras": len(self.get_cerebras_keys()),
            "mistral": len(self.get_mistral_keys()),
            "deepseek": len(self.get_deepseek_keys()),
            "openai": len(self.get_openai_keys()),
            "anthropic": len(self.get_anthropic_keys()),
        }
    
    def get_active_provider(self) -> str:
        """Получить активный провайдер с проверкой наличия ключей"""
        if self.AI_PROVIDER not in self.get_provider_status():
            return "groq"  # fallback
        
        if self.get_provider_status()[self.AI_PROVIDER]:
            return self.AI_PROVIDER
        
        # Если ключи для выбранного провайдера отсутствуют, ищем первый с ключами
        for provider, has_keys in self.get_provider_status().items():
            if has_keys:
                return provider
        
        return "groq"  # fallback
    
    def get_model_for_provider(self, provider: Optional[str] = None) -> str:
        """Получить модель для провайдера"""
        provider = provider or self.AI_PROVIDER
        
        models = {
            "groq": self.GROQ_MODEL,
            "gemini": self.GEMINI_MODEL,
            "cerebras": self.CEREBRAS_MODEL,
            "mistral": self.MISTRAL_MODEL,
            "deepseek": self.DEEPSEEK_MODEL,
            "openai": self.OPENAI_MODEL,
            "anthropic": self.ANTHROPIC_MODEL,
        }
        
        return models.get(provider, "mixtral-8x7b-32768")
    
    # ============================================
    # VALIDATION
    # ============================================
    
    def is_valid(self) -> bool:
        """Проверка валидности настроек"""
        if not self.TELEGRAM_BOT_TOKEN:
            return False
        
        # Проверяем, есть ли ключи для активного провайдера
        status = self.get_provider_status()
        if self.AI_PROVIDER not in status:
            return False
        
        return status[self.AI_PROVIDER]
    
    def get_missing_keys(self) -> List[str]:
        """Получить список отсутствующих ключей"""
        missing = []
        
        if not self.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        
        status = self.get_provider_status()
        if self.AI_PROVIDER in status and not status[self.AI_PROVIDER]:
            missing.append(f"{self.AI_PROVIDER.upper()}_API_KEY")
        
        return missing
    
    def get_all_models(self) -> Dict[str, str]:
        """Получить все модели"""
        return {
            "groq": self.GROQ_MODEL,
            "gemini": self.GEMINI_MODEL,
            "cerebras": self.CEREBRAS_MODEL,
            "mistral": self.MISTRAL_MODEL,
            "deepseek": self.DEEPSEEK_MODEL,
            "openai": self.OPENAI_MODEL,
            "anthropic": self.ANTHROPIC_MODEL,
        }
    
    # ============================================
    # TERMUX / ENVIRONMENT
    # ============================================
    
    def is_termux(self) -> bool:
        """Проверка, запущен ли бот в Termux"""
        try:
            return os.path.exists("/data/data/com.termux")
        except:
            return False
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Получить информацию об окружении"""
        return {
            "is_termux": self.is_termux(),
            "provider": self.AI_PROVIDER,
            "provider_status": self.get_provider_status(),
            "keys_count": self.get_provider_keys_count(),
            "active_model": self.get_model_for_provider(),
            "admin_count": len(self.ADMIN_IDS),
            "owner_id": self.OWNER_ID,
            "debug": self.DEBUG,
        }
    
    # ============================================
    # STRING REPRESENTATION
    # ============================================
    
    def __repr__(self) -> str:
        """Краткое представление настроек (без ключей)"""
        status = self.get_provider_status()
        status_str = ", ".join([f"{k}: {'✅' if v else '❌'}" for k, v in status.items()])
        
        return f"Settings(provider={self.AI_PROVIDER}, {status_str})"
    
    def to_dict(self, hide_keys: bool = True) -> Dict[str, Any]:
        """Преобразовать настройки в словарь (с возможностью скрыть ключи)"""
        data = {
            "bot_name": self.BOT_NAME,
            "ai_provider": self.AI_PROVIDER,
            "provider_status": self.get_provider_status(),
            "keys_count": self.get_provider_keys_count(),
            "models": self.get_all_models(),
            "admin_ids": self.ADMIN_IDS,
            "owner_id": self.OWNER_ID,
            "group_chat_enabled": self.GROUP_CHAT_ENABLED,
            "mention_required": self.MENTION_REQUIRED,
            "allowed_topic_id": self.ALLOWED_TOPIC_ID,
            "anti_flood_seconds": self.ANTI_FLOOD_SECONDS,
            "max_messages_per_minute": self.MAX_MESSAGES_PER_MINUTE,
            "max_history": self.MAX_HISTORY,
            "log_level": self.LOG_LEVEL,
            "debug": self.DEBUG,
            "is_termux": self.is_termux(),
        }
        
        if not hide_keys:
            # Добавляем ключи (осторожно, для отладки!)
            data["keys"] = {
                "groq": self.get_groq_keys(),
                "gemini": self.get_gemini_keys(),
                "cerebras": self.get_cerebras_keys(),
                "mistral": self.get_mistral_keys(),
                "deepseek": self.get_deepseek_keys(),
            }
        
        return data

# ============================================
# SINGLETON INSTANCE
# ============================================

settings = Settings()

# ============================================
# DEBUG OUTPUT (если включен DEBUG)
# ============================================

if settings.DEBUG:
    print("=" * 60)
    print("🔧 НАСТРОЙКИ ЗАГРУЖЕНЫ")
    print("=" * 60)
    print(f"🤖 Бот: {settings.BOT_NAME}")
    print(f"📱 Провайдер: {settings.AI_PROVIDER}")
    print(f"📊 Статус: {settings.get_provider_status()}")
    print(f"🔑 Ключей: {settings.get_provider_keys_count()}")
    print(f"👑 Владелец: {settings.OWNER_ID}")
    print(f"📱 Termux: {'✅' if settings.is_termux() else '❌'}")
    print("=" * 60)
