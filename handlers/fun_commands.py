"""
Fun Admin Commands — рулетки мута (все = 1 минута)
"""
import time
import random
import asyncio
import logging

from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

from handlers import admin_only
from core.chat_history import chat_history

logger = logging.getLogger(__name__)


async def cmd_mute_roulette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    target_user = None
    target_name = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_name = target_user.first_name or target_user.username or "Неизвестный"
    elif context.args:
        target_name = " ".join(context.args).replace("@", "")
    else:
        target_user = update.effective_user
        target_name = target_user.first_name or "себя"

    effects = [
        "Крутим барабан...", "Пила выбирает жертву...",
        "Судьба решает...", "Тень шепчет имя...", "Мои глаза краснеют...",
    ]
    spin_msg = await update.message.reply_text(
        f"~ {random.choice(effects)}\n\n"
        f"🎰 РУЛЕТКА МУТА 🎰\n"
        f"Жертва: {target_name}\n"
        f"Крутим..."
    )
    await asyncio.sleep(2)

    result_text = (
        f"~ ТЫК-ТЫК-ТЫК...\n\n"
        f"🎰 РУЛЕТКА МУТА 🎰\n"
        f"Жертва: {target_name}\n"
        f"Результат: 1 минута\n\n"
        f"Наслаждайся тишиной... Хи-хи..."
    )
    if target_user and target_user.id != update.effective_user.id:
        try:
            until_date = int(time.time()) + 60
            await context.bot.restrict_chat_member(
                chat_id, target_user.id, until_date=until_date,
                permissions=ChatPermissions(
                    can_send_messages=False, can_send_media_messages=False,
                    can_send_other_messages=False, can_add_web_page_previews=False,
                )
            )
        except Exception as e:
            logger.error(f"Ошибка мута: {e}")
    await spin_msg.edit_text(result_text)


async def cmd_reverse_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    victim = update.effective_user
    try:
        until_date = int(time.time()) + 60
        await context.bot.restrict_chat_member(
            chat_id, victim.id, until_date=until_date,
            permissions=ChatPermissions(
                can_send_messages=False, can_send_media_messages=False,
                can_send_other_messages=False, can_add_web_page_previews=False,
            )
        )
        await update.message.reply_text(
            "~ ХИ-ХИ-ХИ...\n\n"
            "Обратный мут сработал!\n"
            "Ты сам себя замутил на 1 минуту...\n\n"
            "Я предупреждала, что пилы опасны... ~"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка... {e}")


async def cmd_russian_roulette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_name = user.first_name or user.username or "Игрок"
    await update.message.reply_text(
        f"~ {user_name} берёт револьвер...\n"
        f"1 патрон в барабане...\n"
        f"5 пустых...\n\n"
        f"Крутим..."
    )
    await asyncio.sleep(2)
    bullet = random.randint(1, 6)
    chamber = random.randint(1, 6)
    if bullet == chamber:
        try:
            until_date = int(time.time()) + 60
            await context.bot.restrict_chat_member(
                chat_id, user.id, until_date=until_date,
                permissions=ChatPermissions(
                    can_send_messages=False, can_send_media_messages=False,
                    can_send_other_messages=False, can_add_web_page_previews=False,
                )
            )
            await update.message.reply_text(
                f"! БА-БАХ !\n\n"
                f"💥 {user_name} ПРОИГРАЛ...\n"
                f"Пуля нашла цель...\n"
                f"1 минута тишины...\n\n"
                f"Я говорила, что шансы плохие... Хи-хи..."
            )
        except Exception as e:
            await update.message.reply_text(f"Пуля не залетела... {e}")
    else:
        await update.message.reply_text(
            f"~ Щёлк...\n\n"
            f"Пусто... {user_name} выжил...\n"
            f"В этот раз...\n\n"
            f"Хочешь ещё разок? ~"
        )


async def cmd_mute_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    if not update.message.reply_to_message:
        await update.message.reply_text("Использование: reply на сообщение противника + /muteduel")
        return
    player1 = update.effective_user
    player2 = update.message.reply_to_message.from_user
    if player1.id == player2.id:
        await update.message.reply_text("Нельзя дуэлиться с собой...")
        return
    p1_name = player1.first_name or "Игрок 1"
    p2_name = player2.first_name or "Игрок 2"
    await update.message.reply_text(
        f"~ ДУЭЛЬ НА МУТАХ ~\n\n"
        f"⚔️ {p1_name} VS {p2_name}\n\n"
        f"Крутим барабаны..."
    )
    await asyncio.sleep(3)
    p1_dead = random.randint(1, 6) == random.randint(1, 6)
    p2_dead = random.randint(1, 6) == random.randint(1, 6)

    result_text = "~ ДУЭЛЬ НА МУТАХ ~\n\n"
    perms = ChatPermissions(
        can_send_messages=False, can_send_media_messages=False,
        can_send_other_messages=False, can_add_web_page_previews=False,
    )

    if p1_dead and p2_dead:
        result_text += (
            f"💥 Оба ПРОИГРАЛИ!\n\n"
            f"💀 {p1_name} — МУТ 1 минута\n"
            f"💀 {p2_name} — МУТ 1 минута\n\n"
            f"Ничья... В смерти... Хи-хи..."
        )
        try:
            until_date = int(time.time()) + 60
            for p in [player1, player2]:
                await context.bot.restrict_chat_member(chat_id, p.id, until_date=until_date, permissions=perms)
        except Exception as e:
            result_text += f"\n\nОшибка: {e}"
    elif p1_dead:
        result_text += (
            f"💥 БА-БАХ!\n\n"
            f"💀 {p1_name} — МУТ 1 минута\n"
            f"✅ {p2_name} — ВЫЖИЛ\n\n"
            f"{p2_name}... Ты сильнее, чем я думала..."
        )
        try:
            until_date = int(time.time()) + 60
            await context.bot.restrict_chat_member(chat_id, player1.id, until_date=until_date, permissions=perms)
        except Exception as e:
            result_text += f"\n\nОшибка: {e}"
    elif p2_dead:
        result_text += (
            f"💥 БА-БАХ!\n\n"
            f"✅ {p1_name} — ВЫЖИЛ\n"
            f"💀 {p2_name} — МУТ 1 минута\n\n"
            f"{p1_name}... Ты напоминаешь мне... меня..."
        )
        try:
            until_date = int(time.time()) + 60
            await context.bot.restrict_chat_member(chat_id, player2.id, until_date=until_date, permissions=perms)
        except Exception as e:
            result_text += f"\n\nОшибка: {e}"
    else:
        result_text += (
            f"~ Щёлк... Щёлк...\n\n"
            f"✅ {p1_name} — ВЫЖИЛ\n"
            f"✅ {p2_name} — ВЫЖИЛ\n\n"
            f"Оба выжили... Как скучно...\n"
            f"Ещё раз? ~"
        )
    await update.message.reply_text(result_text)


async def cmd_random_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    users = chat_history.get_unique_users(chat_id, limit=100)
    candidates = {uid: name for uid, name in users.items() if uid != update.effective_user.id}
    if not candidates:
        await update.message.reply_text("Никого нет... Только мы с тобой... ~")
        return
    victim_id, victim_name = random.choice(list(candidates.items()))
    try:
        until_date = int(time.time()) + 60
        await context.bot.restrict_chat_member(
            chat_id, victim_id, until_date=until_date,
            permissions=ChatPermissions(
                can_send_messages=False, can_send_media_messages=False,
                can_send_other_messages=False, can_add_web_page_previews=False,
            )
        )
        await update.message.reply_text(
            f"~ Случайность выбрала...\n\n"
            f"🎯 Жертва: {victim_name}\n"
            f"⏱ Время: 1 минута\n\n"
            f"Судьба жестока... Но я ещё жестче... Хи-хи..."
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка... Мои пилы сломались: {e}")


async def cmd_mute_wheel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    if update.message.reply_to_message:
        victim = update.message.reply_to_message.from_user
    else:
        await update.message.reply_text("Использование: reply на сообщение + /mutewheel")
        return
    victim_name = victim.first_name or victim.username or "Жертва"
    await update.message.reply_text(f"~ КОЛЕСО ФОРТУНЫ ~\n\nЖертва: {victim_name}\nКрутим...")
    await asyncio.sleep(2)
    wheel = [
        ("Мут 1 минута", 60, "Недолго... Но достаточно заскучать..."),
        ("РАЗМУТ", 0, "О... Повезло... В этот раз..."),
    ]
    result = random.choice(wheel)
    name, duration, comment = result
    if duration > 0:
        try:
            until_date = int(time.time()) + duration
            await context.bot.restrict_chat_member(
                chat_id, victim.id, until_date=until_date,
                permissions=ChatPermissions(
                    can_send_messages=False, can_send_media_messages=False,
                    can_send_other_messages=False, can_add_web_page_previews=False,
                )
            )
            await update.message.reply_text(
                f"~ КОЛЕСО ФОРТУНЫ ~\n\n"
                f"🎯 Жертва: {victim_name}\n"
                f"🎰 Выпало: {name}\n\n"
                f"{comment}"
            )
        except Exception as e:
            await update.message.reply_text(f"Ошибка: {e}")
    else:
        try:
            await context.bot.restrict_chat_member(
                chat_id, victim.id,
                permissions=ChatPermissions(
                    can_send_messages=True, can_send_media_messages=True,
                    can_send_other_messages=True, can_add_web_page_previews=True,
                )
            )
            await update.message.reply_text(
                f"~ КОЛЕСО ФОРТУНЫ ~\n\n"
                f"🎯 {victim_name}\n"
                f"🎰 Выпало: РАЗМУТ!\n\n"
                f"{comment}\n\n"
                f"Не привыкай... ~"
            )
        except Exception as e:
            await update.message.reply_text(f"Ошибка: {e}")


async def cmd_mute_lottery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        "~ ЛОТЕРЕЯ МИЛОСЕРДИЯ ~\n\n"
        "Выбираю одного из замученных...\n"
        "Кто получит шанс говорить?\n\n"
        "Тык-тык-тык..."
    )
    await asyncio.sleep(2)
    try:
        users = chat_history.get_unique_users(chat_id, limit=50)
        candidates = {uid: name for uid, name in users.items() if uid != update.effective_user.id}
        if not candidates:
            await update.message.reply_text(
                "~ Никого нет...\n\n"
                "Все уже говорят...\n"
                "Или все уже навсегда замолчали...\n"
                "Хи-хи..."
            )
            return
        winner_id, winner_name = random.choice(list(candidates.items()))
        await context.bot.restrict_chat_member(
            chat_id, winner_id,
            permissions=ChatPermissions(
                can_send_messages=True, can_send_media_messages=True,
                can_send_other_messages=True, can_add_web_page_previews=True,
            )
        )
        await update.message.reply_text(
            f"~ ПОБЕДИТЕЛЬ ~\n\n"
            f"🎉 {winner_name}\n\n"
            f"Ты можешь говорить...\n"
            f"Пока я не передумала...\n\n"
            f"Наслаждайся... ~"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
