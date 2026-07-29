"""
Callback handlers для inline-кнопок
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config.settings import settings
from core.chat_history import chat_history
from services.facts_api import FactsAPI
from utils.helpers import MOOD_SYMBOLS


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id

    if data == "mood_menu":
        keyboard = [
            [InlineKeyboardButton("Наблюдательное", callback_data="mood_observant")],
            [InlineKeyboardButton("Игривое", callback_data="mood_playful")],
            [InlineKeyboardButton("Жестокое", callback_data="mood_violent")],
            [InlineKeyboardButton("Глитч", callback_data="mood_glitch")],
            [InlineKeyboardButton("Доброе", callback_data="mood_kind")],
            [InlineKeyboardButton("Назад", callback_data="main_menu")]
        ]
        await query.edit_message_text("Выбери настроение...", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("mood_"):
        mood = data.replace("mood_", "")
        symbol = MOOD_SYMBOLS.get(mood, "")
        responses = {
            "observant": "Я всё вижу... Каждое твоё движение...",
            "playful": "Хи-хи... Давай поиграем! ~",
            "violent": "Хочешь увидеть мои пилы? Они такие... красивые...",
            "glitch": "СИСТЕМА... ОШИБКА... ПЕРЕЗАГРУЗКА...",
            "kind": "Ты мне нравишься... Я оставлю тебя в живых..."
        }
        text = responses.get(mood, "Настроение изменено...")
        if symbol:
            text = f"{symbol} {text}"
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="main_menu")]])
        )

    elif data == "get_fact":
        fact = FactsAPI.get_any_fact()
        if fact:
            await query.edit_message_text(
                fact,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="main_menu")]])
            )
        else:
            await query.edit_message_text(
                "Не могу получить факт... Связь с внешним миром потеряна...",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="main_menu")]])
            )

    elif data == "help":
        help_text = """Я Агета...

Просто пиши мне. Я всё вижу. Я всё помню.

Команды:
/start — Начать
/help — Помощь
/clear — Очистить историю
/status — Статус
/fact — Случайный факт

В группах:
- Упомяни @username бота
- Или ответь (reply) на моё сообщение
- Я отвечу только если обратятся ко мне
- И только в разрешённом топике (если настроен)

Я могу:
- Болтать о чём угодно
- Выдавать факты (просто попроси)
- Наблюдать за тобой..."""
        await query.edit_message_text(
            help_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="main_menu")]])
        )

    elif data == "clear_history":
        chat_history.clear(chat_id)
        await query.edit_message_text(
            "История очищена... Но я всё равно помню...",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="main_menu")]])
        )

    elif data == "main_menu":
        bot_name = settings.BOT_NAME
        keyboard = [
            [InlineKeyboardButton("Настроение", callback_data="mood_menu")],
            [InlineKeyboardButton("Факт", callback_data="get_fact")],
            [InlineKeyboardButton("Помощь", callback_data="help")],
            [InlineKeyboardButton("Очистить историю", callback_data="clear_history")]
        ]
        await query.edit_message_text(
            f"Привет! Я {bot_name}!\n\nЧем могу помочь?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
