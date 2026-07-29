"""
Blackhat команды — управление списком жертв
"""
import random

from telegram import Update
from telegram.ext import ContextTypes

from handlers import admin_only
from managers.blackhat_manager import blackhat_manager


async def cmd_blackhat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить жертву в blackhat (/blackhat reply или ID)"""
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        target_id = target.id
        target_name = target.first_name or target.username or "Жертва"
    elif context.args:
        try:
            target_id = int(context.args[0])
            target_name = f"ID:{target_id}"
        except ValueError:
            await update.message.reply_text("~ Нужен reply на сообщение жертвы... \\\nИли используй ID: /blackhat 123456789")
            return
    else:
        await update.message.reply_text("Использование: reply на сообщение + /blackhat \\\nИли: /blackhat 123456789")
        return
    blackhat_manager.add_target(chat_id, target_id)
    await update.message.reply_text(f"~ ЖЕРТВА ДОБАВЛЕНА ~\n\n🎯 {target_name}\nТеперь я всегда буду помнить...\nИ ненавидеть... Хи-хи...")


async def cmd_unblackhat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Убрать жертву из blackhat"""
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        target_id = target.id
        target_name = target.first_name or target.username or "Кто-то"
    elif context.args:
        try:
            target_id = int(context.args[0])
            target_name = f"ID:{target_id}"
        except ValueError:
            await update.message.reply_text("Использование: reply на сообщение + /unblackhat")
            return
    else:
        await update.message.reply_text("Использование: reply на сообщение + /unblackhat")
        return
    blackhat_manager.remove_target(chat_id, target_id)
    await update.message.reply_text(f"~ МИЛОСЕРДИЕ? ~\n\n🎯 {target_name} убран из списка...\nВ этот раз... Не привыкай...")


async def cmd_blackhatmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Включить/выключить blackhat режим"""
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    if not context.args:
        current = blackhat_manager.is_enabled(chat_id)
        status = "ВКЛЮЧЕН" if current else "ВЫКЛЮЧЕН"
        await update.message.reply_text(f"~ BLACKHAT MODE ~\n\nСтатус: {status}\n\nИспользование: /blackhatmode on | off")
        return
    arg = context.args[0].lower()
    if arg in ("on", "1", "yes", "true"):
        blackhat_manager.set_enabled(chat_id, True)
        await update.message.reply_text("~ BLACKHAT MODE ВКЛЮЧЕН ~\n\nЯ буду жестокой...\nК тем, кто заслуживает...\nХи-хи...")
    elif arg in ("off", "0", "no", "false"):
        blackhat_manager.set_enabled(chat_id, False)
        await update.message.reply_text("~ BLACKHAT MODE ВЫКЛЮЧЕН ~\n\nМилосердие?..\nВременно...")
    else:
        await update.message.reply_text("Использование: /blackhatmode on | off")


async def cmd_blackhatlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список жертв"""
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    targets = blackhat_manager.get_targets(chat_id)
    if not targets:
        await update.message.reply_text("~ СПИСОК ПУСТ ~\n\nНет жертв...\nПока...")
        return
    text = "~ BLACKHAT LIST ~\n\n"
    text += f"Жертв в чате: {len(targets)}\n\n"
    for uid in targets:
        text += f"  🎯 {uid}\n"
    text += f"\nРежим: {'ВКЛЮЧЕН' if blackhat_manager.is_enabled(chat_id) else 'ВЫКЛЮЧЕН'}"
    await update.message.reply_text(text)


async def cmd_blackhatroulette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Рулетка оскорбления для жертвы"""
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    targets = blackhat_manager.get_targets(chat_id)
    if not targets:
        await update.message.reply_text("~ НЕТ ЖЕРТВ ~\n\nДобавь кого-то в blackhat сначала...\n/blackhat (reply на сообщение)")
        return
    victim_id = random.choice(list(targets))
    insult = blackhat_manager.get_random_insult()
    await update.message.reply_text(f"~ BLACKHAT ROULETTE ~\n\n🎯 Жертва ID: {victim_id}\n\n{insult}\n\nХи-хи...")
