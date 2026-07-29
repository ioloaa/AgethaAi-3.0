"""
Админские команды
"""
import os
import time
import asyncio
import logging
from datetime import datetime

from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

from handlers import admin_only
from config.settings import settings
from core.chat_history import chat_history
from core.anti_flood import anti_flood
from managers.mute_manager import mute_manager
from managers.ban_manager import ban_manager
from utils.system_monitor import SystemMonitor

logger = logging.getLogger(__name__)


async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    if context.args:
        try:
            chat_id = int(context.args[0])
        except ValueError:
            pass
    mute_manager.mute_chat(chat_id)
    await update.message.reply_text(f"Чат {chat_id} замьючен. Я больше не отвечаю там.")


async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    if context.args:
        try:
            chat_id = int(context.args[0])
        except ValueError:
            pass
    mute_manager.unmute_chat(chat_id)
    await update.message.reply_text(f"Чат {chat_id} размьючен. Я снова здесь!")


async def cmd_reboot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    await update.message.reply_text("Перезагрузка... Скоро вернусь!")
    logger.info("Админ запросил перезагрузку")

    async def _reboot():
        await asyncio.sleep(2)
        os._exit(0)

    asyncio.create_task(_reboot())


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    if not context.args:
        await update.message.reply_text("Использование: /broadcast текст сообщения")
        return
    message = " ".join(context.args)
    sent_count = 0
    all_chats = list(chat_history._history.keys())
    for chat_id in all_chats:
        try:
            await context.bot.send_message(chat_id, f"Сообщение от админа:\n\n{message}")
            sent_count += 1
        except Exception as e:
            logger.error(f"Не удалось отправить в {chat_id}: {e}")
    await update.message.reply_text(f"Отправлено в {sent_count} чатов")


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    topic_info = f"ID={settings.ALLOWED_TOPIC_ID}" if settings.ALLOWED_TOPIC_ID is not None else "не ограничен"
    stats = f"""Статистика бота:

Чатов: {chat_history.total_chats}
Сообщений в истории: {chat_history.total_messages}
Замьюченных чатов: {mute_manager.muted_chats_count}
Забаненных глобально: {ban_manager.global_banned_count}
Забаненных в чатах: {ban_manager.total_chat_bans}
Groq API: {"✅" if settings.get_groq_keys() else "❌"}
Gemini API: {"✅" if settings.get_gemini_key() else "❌"}
Cerebras API: {"✅" if settings.get_cerebras_keys() else "❌"}
Разрешённый топик: {topic_info}
Аптайм: работает

Админы: {settings.ADMIN_IDS or "не указаны"}"""
    await update.message.reply_text(stats)


async def cmd_addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    if not context.args:
        await update.message.reply_text("Использование: /addadmin 123456789")
        return
    try:
        new_admin_id = int(context.args[0])
        anti_flood.add_admin(new_admin_id)
        await update.message.reply_text(f"Пользователь {new_admin_id} теперь админ!")
    except ValueError:
        await update.message.reply_text("Неверный ID пользователя")


async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    if not context.args:
        await update.message.reply_text("Использование: /ban user_id [причина]\nПример: /ban 123456789 спам")
        return
    try:
        user_id = int(context.args[0])
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else ""
        chat_id = update.effective_chat.id
        admin_id = update.effective_user.id
        if reason == "-g":
            ban_manager.ban_user(user_id, None, admin_id, "Глобальный бан")
            await update.message.reply_text(f"Пользователь {user_id} забанен ГЛОБАЛЬНО.\nБот не будет отвечать ему ни в одном чате.")
        else:
            ban_manager.ban_user(user_id, chat_id, admin_id, reason)
            await update.message.reply_text(f"Пользователь {user_id} забанен в этом чате.\nПричина: {reason if reason else 'не указана'}")
        logger.info(f"Админ {admin_id} забанил пользователя {user_id}")
    except ValueError:
        await update.message.reply_text("Неверный ID пользователя. Используй: /ban 123456789")


async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    if not context.args:
        await update.message.reply_text("Использование: /unban 123456789")
        return
    try:
        user_id = int(context.args[0])
        chat_id = update.effective_chat.id
        if user_id in ban_manager._banned_users:
            ban_manager.unban_user(user_id, None)
            await update.message.reply_text(f"Пользователь {user_id} разбанен глобально.")
        else:
            ban_manager.unban_user(user_id, chat_id)
            await update.message.reply_text(f"Пользователь {user_id} разбанен в этом чате.")
        logger.info(f"Админ {update.effective_user.id} разбанил пользователя {user_id}")
    except ValueError:
        await update.message.reply_text("Неверный ID пользователя. Используй: /unban 123456789")


async def cmd_banlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    global_banned = ban_manager._banned_users
    chat_banned = ban_manager._chat_bans.get(chat_id, set())
    text = "Список забаненных:\n\n"
    if global_banned:
        text += "Глобально забаненные:\n"
        for uid in global_banned:
            text += f"  - {uid} (все чаты)\n"
        text += "\n"
    if chat_banned:
        text += f"Забаненные в этом чате ({chat_id}):\n"
        for uid in chat_banned:
            text += f"  - {uid}\n"
        text += "\n"
    if not global_banned and not chat_banned:
        text += "Нет забаненных пользователей."
    history = ban_manager.get_recent_bans(10)
    if history:
        text += "\nПоследние баны:\n"
        for record in reversed(history):
            ts = time.strftime("%H:%M:%S", time.localtime(record["timestamp"]))
            chat_info = f"чат {record['chat_id']}" if record['chat_id'] else "глобально"
            text += f"  [{ts}] {record['user_id']} — {chat_info}\n"
    await update.message.reply_text(text)


async def cmd_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /phone - показать состояние телефона/системы"""
    if not await admin_only(update):
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    # Собираем данные ПРЯМО СЕЙЧАС
    state = SystemMonitor.collect_now()

    if not state:
        await update.message.reply_text("⚠️ Не удалось собрать данные о системе.")
        return

    message = SystemMonitor.get_formatted_state(state)

    if len(message) > 4000:
        parts = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for part in parts:
            await update.message.reply_text(part, parse_mode="Markdown")
    else:
        await update.message.reply_text(message, parse_mode="Markdown")
