"""
Основной обработчик текстовых сообщений + AI-генерация
"""
import random
import logging

from telegram import Update
from telegram.ext import ContextTypes

from config.settings import settings
from core.ai_engine import ai_engine
from core.chat_history import chat_history
from core.anti_flood import anti_flood
from managers.mute_manager import mute_manager
from managers.ban_manager import ban_manager
from managers.blackhat_manager import blackhat_manager
from services.facts_api import FactsAPI
from utils.helpers import format_mood_text, is_fact_request

logger = logging.getLogger(__name__)


class GroupChatHandler:
    """Определяет, должен ли бот отвечать в группе"""

    def __init__(self):
        self.enabled = settings.GROUP_CHAT_ENABLED
        self.mention_required = settings.MENTION_REQUIRED
        self.allowed_topic_id = settings.ALLOWED_TOPIC_ID
        self.bot_username = None

    def should_respond(self, update: Update) -> bool:
        if not update.effective_chat:
            return False
        chat = update.effective_chat
        message = update.effective_message
        if chat.type == "private":
            return True
        if not self.enabled:
            return False
        if self.allowed_topic_id is not None:
            message_topic = message.message_thread_id if message else None
            if message_topic != self.allowed_topic_id:
                logger.debug(
                    f"Игнорируем сообщение в топике {message_topic} "
                    f"(разрешён только {self.allowed_topic_id})"
                )
                return False
        if self.mention_required:
            if not message:
                return False
            if message.reply_to_message and message.reply_to_message.from_user:
                if message.reply_to_message.from_user.is_bot:
                    if self.bot_username and message.reply_to_message.from_user.username == self.bot_username:
                        return True
            if message.text and self.bot_username:
                if f"@{self.bot_username}" in message.text:
                    return True
            if message.text and message.text.startswith("/"):
                return True
            return False
        return True

    def clean_message(self, text: str) -> str:
        if self.bot_username and text:
            text = text.replace(f"@{self.bot_username}", "").strip()
        return text


group_handler = GroupChatHandler()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return

    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    chat_id = chat.id
    user_id = user.id

    # Проверка бана
    if ban_manager.is_banned(user_id, chat_id) or ban_manager.is_banned(user_id, None):
        return

    # Проверка мутов
    if mute_manager.is_muted(chat_id) or mute_manager.is_user_muted(chat_id, user_id):
        return

    # Проверка ответа (включая топик)
    if not group_handler.should_respond(update):
        return

    # Анти-флуд
    allowed, reason = anti_flood.is_allowed(user_id)
    if not allowed:
        await message.reply_text(reason)
        return

    # Очистка текста
    text = group_handler.clean_message(message.text)
    if not text.strip():
        return

    # Проверка на запрос факта
    if is_fact_request(text):
        fact = FactsAPI.get_any_fact()
        if fact:
            await message.reply_text(fact)
        else:
            await message.reply_text("Хм... Не могу вспомнить факт... Моя память глючит...")
        return

    # BLACKHAT CHECK
    if blackhat_manager.is_enabled(chat_id) and blackhat_manager.is_target(user_id, chat_id):
        insult = blackhat_manager.get_random_insult()
        await message.reply_text(f"~ {insult}")
        return

    # Показываем "печатает..."
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Добавляем в историю
    user_name = user.first_name or user.username or "друг"
    chat_history.add(chat_id, user_id, user_name, "user", text)

    # Запрос к AI
    try:
        history = chat_history.get(chat_id)
        response = ai_engine.query(text, history, user_name)

        ai_text = response.get("text", "...")
        mood = response.get("mood", "neutral")

        chat_history.add(chat_id, 0, "Агета", "assistant", ai_text, mood)

        reply_text = format_mood_text(ai_text, mood, chance=0.15)

        if chat.type == "private":
            await message.reply_text(reply_text)
        else:
            await message.reply_text(reply_text, reply_to_message_id=message.message_id)

        logger.info(f"[{chat_id}] {user_name}: {text[:50]}... -> AI: {ai_text[:50]}...")

    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        await message.reply_text("Ошибка... Система глючит... Попробуй позже...")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}", exc_info=True)
    if update and update.effective_message:
        await update.effective_message.reply_text("ОШИБКА... СИСТЕМА... ГЛЮЧИТ...")
