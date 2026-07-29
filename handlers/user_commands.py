"""
Пользовательские команды
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config.settings import settings
from core.chat_history import chat_history
from services.facts_api import FactsAPI


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_name = settings.BOT_NAME
    user = update.effective_user
    welcome = f"""Привет, {user.first_name}...

Я {bot_name}. Ты нашёл меня.

Могу поболтать, ответить на вопросы, или рассказать что-то интересное.

Просто напиши мне. ~"""
    keyboard = [
        [InlineKeyboardButton("Настроение", callback_data="mood_menu")],
        [InlineKeyboardButton("Факт", callback_data="get_fact")],
        [InlineKeyboardButton("Помощь", callback_data="help")],
        [InlineKeyboardButton("Очистить историю", callback_data="clear_history")]
    ]
    await update.message.reply_text(welcome, reply_markup=InlineKeyboardMarkup(keyboard))


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """Команды:

/start — Начать (или перезапустить)
/help — Помощь
/clear — Очистить историю
/status — Статус бота
/fact — Случайный интересный факт

Админские:
/mute — Замьютить чат
/unmute — Размьютить чат
/ban — Забанить пользователя
/unban — Разбанить пользователя
/banlist — Список забаненных
/reboot — Перезагрузить бота
/broadcast — Сообщение всем чатам
/stats — Статистика
/addadmin — Добавить админа
/phone — Состояние системы

Blackhat (система ненависти):
/blackhat — Добавить жертву (reply)
/unblackhat — Убрать жертву (reply)
/blackhatmode on/off — Включить/выключить режим
/blackhatlist — Список жертв
/blackhatroulette — Рулетка оскорбления

Рулетки и приколы с мутами (все = 1 минута):
/muteroulette — Рулетка мута (reply на жертву)
/reversemute — Обратный мут (мутит себя)
/roulette — Русская рулетка (1/6 шанс)
/muteduel — Дуэль на мутах (reply на противника)
/randommute — Случайный мут случайного человека
/mutewheel — Колесо фортуны (1 минута или размут)
/mutelottery — Лотерея размута

В группах:
- Упомяни @username бота
- Или ответь (reply) на моё сообщение
- Я отвечу только если обратятся ко мне
- И только в разрешённом топике (если настроен)

Анти-флуд: не более 30 сообщений в минуту"""
    await update.message.reply_text(help_text)


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_history.clear(chat_id)
    await update.message.reply_text("История очищена... Но я всё равно помню...")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from core.ai_engine import ai_engine
    from core.anti_flood import anti_flood
    from managers.mute_manager import mute_manager
    provider = settings.AI_PROVIDER
    model = settings.GROQ_MODEL
    history_len = len(chat_history.get(update.effective_chat.id))
    groq_status = "✅" if settings.get_groq_keys() else "❌"
    gemini_status = "✅" if settings.get_gemini_key() else "❌"
    cerebras_status = "✅" if settings.get_cerebras_key() else "❌"
    topic_info = f"ID={settings.ALLOWED_TOPIC_ID}" if settings.ALLOWED_TOPIC_ID is not None else "не ограничен"
    status = f"""Статус:

Провайдер: {provider}
Модель: {model}
Groq API: {groq_status}
Gemini API: {gemini_status}
Cerebras API: {cerebras_status}
Сообщений: {history_len}
Анти-флуд: {anti_flood.anti_flood_seconds} сек
Группы: {'включены' if settings.GROUP_CHAT_ENABLED else 'выключены'}
Разрешённый топик: {topic_info}
Мут: {'да' if mute_manager.is_muted(update.effective_chat.id) else 'нет'}

Я наблюдаю..."""
    await update.message.reply_text(status)


async def cmd_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    fact = FactsAPI.get_any_fact()
    if fact:
        await update.message.reply_text(fact)
    else:
        await update.message.reply_text("Хм... Не могу вспомнить факт... Моя память глючит...")
