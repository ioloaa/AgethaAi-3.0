cat > telegram_bot.py << 'EOF'
"""
AgethaAi Telegram Bot v8 — FPE Edition
Точка входа с поддержкой монитора состояния телефона
"""

import logging
import sys
import os

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters,
)

from config.settings import settings
from handlers.user_commands import cmd_start, cmd_help, cmd_clear, cmd_status, cmd_fact
from handlers.admin_commands import (
    cmd_mute, cmd_unmute, cmd_reboot, cmd_broadcast,
    cmd_stats, cmd_addadmin, cmd_ban, cmd_unban, cmd_banlist, cmd_phone
)
from handlers.blackhat_commands import (
    cmd_blackhat, cmd_unblackhat, cmd_blackhatmode,
    cmd_blackhatlist, cmd_blackhatroulette
)
from handlers.fun_commands import (
    cmd_mute_roulette, cmd_reverse_mute, cmd_russian_roulette,
    cmd_mute_duel, cmd_random_mute, cmd_mute_wheel, cmd_mute_lottery
)
from handlers.callbacks import handle_callback
from handlers.messages import handle_message, error_handler, group_handler

# Импорт монитора телефона
try:
    from phone_monitor import PhoneState, start_monitor, get_formatted_status
    PHONE_MONITOR_AVAILABLE = True
except ImportError:
    PHONE_MONITOR_AVAILABLE = False
    print("⚠️ phone_monitor.py не найден. Мониторинг телефона отключен.")

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)


# === НОВАЯ КОМАНДА ДЛЯ СТАТУСА ТЕЛЕФОНА ===
async def cmd_phone_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /phonestatus - показать состояние телефона"""
    
    if not PHONE_MONITOR_AVAILABLE:
        await update.message.reply_text("❌ Мониторинг телефона не доступен")
        return
    
    # Проверка прав (только админы)
    if update.effective_user.id not in settings.ADMIN_IDS:
        await update.message.reply_text("❌ Только для администраторов!")
        return
    
    try:
        status = PhoneState.get_formatted_status()
        await update.message.reply_text(status, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка получения статуса: {e}")


# === КОМАНДА ДЛЯ БАТАРЕИ ===
async def cmd_battery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /battery - показать состояние батареи"""
    
    if not PHONE_MONITOR_AVAILABLE:
        await update.message.reply_text("❌ Мониторинг телефона не доступен")
        return
    
    try:
        battery = PhoneState.get_battery()
        
        if "error" in battery:
            await update.message.reply_text(f"❌ Ошибка: {battery['error']}")
            return
        
        percent = battery.get("percent", 0)
        status = battery.get("status", "UNKNOWN")
        is_charging = battery.get("is_charging", False)
        temp = battery.get("temperature", 0)
        
        # Эмодзи для батареи
        if percent >= 80:
            emoji = "🟢"
        elif percent >= 50:
            emoji = "🟡"
        elif percent >= 20:
            emoji = "🟠"
        else:
            emoji = "🔴"
        
        msg = f"**🔋 Состояние батареи**\n"
        msg += f"━━━━━━━━━━━━━━━━\n\n"
        msg += f"{emoji} **Заряд:** {percent}%\n"
        msg += f"**Статус:** {status}\n"
        msg += f"**Зарядка:** {'✅ Да' if is_charging else '❌ Нет'}\n"
        if temp:
            msg += f"**Температура:** {temp}°C\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


# === КОМАНДА ДЛЯ ХРАНИЛИЩА ===
async def cmd_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /storage - показать состояние хранилища"""
    
    if not PHONE_MONITOR_AVAILABLE:
        await update.message.reply_text("❌ Мониторинг телефона не доступен")
        return
    
    try:
        storage = PhoneState.get_storage()
        
        if "error" in storage:
            await update.message.reply_text(f"❌ Ошибка: {storage['error']}")
            return
        
        msg = f"**💾 Состояние хранилища**\n"
        msg += f"━━━━━━━━━━━━━━\n\n"
        msg += f"**Всего:** {storage.get('total', 'N/A')}\n"
        msg += f"**Использовано:** {storage.get('used', 'N/A')}\n"
        msg += f"**Свободно:** {storage.get('free', 'N/A')}\n"
        msg += f"**Заполнено:** {storage.get('percent', '0%')}\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


# === КОМАНДА ДЛЯ СЕТИ ===
async def cmd_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /network - показать состояние сети"""
    
    if not PHONE_MONITOR_AVAILABLE:
        await update.message.reply_text("❌ Мониторинг телефона не доступен")
        return
    
    try:
        network = PhoneState.get_network()
        
        if "error" in network:
            await update.message.reply_text(f"❌ Ошибка: {network['error']}")
            return
        
        msg = f"**📶 Состояние сети**\n"
        msg += f"━━━━━━━━━━━━━━\n\n"
        msg += f"**Wi-Fi:** {network.get('wifi', 'N/A')}\n"
        msg += f"**IP адрес:** {network.get('ip', 'N/A')}\n"
        msg += f"**Сигнал:** {network.get('signal', 0)} dBm\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


async def post_init(application: Application):
    """Инициализация после запуска бота"""
    
    # Запуск монитора телефона
    if PHONE_MONITOR_AVAILABLE:
        try:
            start_monitor()
            logger.info("📱 Монитор телефона запущен")
        except Exception as e:
            logger.error(f"❌ Ошибка запуска монитора: {e}")
    
    bot = application.bot
    me = await bot.get_me()
    group_handler.bot_username = me.username
    logger.info(f"🤖 Бот инициализирован: @{me.username}")

    # Проверка провайдеров
    provider = settings.AI_PROVIDER
    provider_status = settings.get_provider_status()
    
    if provider not in provider_status:
        logger.error(f"❌ Неизвестный провайдер: {provider}")
        return
    
    if not provider_status[provider]:
        logger.error(f"❌ API ключи для {provider} не настроены!")
        logger.info("📝 Добавьте API ключ в .env файл")
        return
    
    logger.info(f"✅ API ключи настроены (провайдер: {provider})")
    
    # Статус всех провайдеров
    for p, status in provider_status.items():
        if status:
            logger.info(f"   ✅ {p}: настроен")
        else:
            logger.info(f"   ⚠️ {p}: не настроен")

    if group_handler.allowed_topic_id is not None:
        logger.info(f"✅ Бот работает ТОЛЬКО в топике ID={group_handler.allowed_topic_id}")
    else:
        logger.info("ℹ️ Топик не ограничен — бот работает во всех темах группы")


def main():
    # Проверка токена
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN не найден!")
        print("\n❌ Установите TELEGRAM_BOT_TOKEN в .env файле:")
        print("   TELEGRAM_BOT_TOKEN='твой_токен'")
        sys.exit(1)
    
    # Проверка валидности настроек
    if not settings.is_valid():
        logger.error("❌ Настройки не валидны!")
        print("\n❌ Проверьте .env файл:")
        print(f"   - AI_PROVIDER: {settings.AI_PROVIDER}")
        print(f"   - API ключи настроены: {settings.get_provider_status()}")
        sys.exit(1)

    application = Application.builder().token(token).post_init(post_init).build()

    # === User commands ===
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("clear", cmd_clear))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("fact", cmd_fact))

    # === Admin commands ===
    application.add_handler(CommandHandler("mute", cmd_mute))
    application.add_handler(CommandHandler("unmute", cmd_unmute))
    application.add_handler(CommandHandler("reboot", cmd_reboot))
    application.add_handler(CommandHandler("broadcast", cmd_broadcast))
    application.add_handler(CommandHandler("stats", cmd_stats))
    application.add_handler(CommandHandler("addadmin", cmd_addadmin))
    application.add_handler(CommandHandler("ban", cmd_ban))
    application.add_handler(CommandHandler("unban", cmd_unban))
    application.add_handler(CommandHandler("banlist", cmd_banlist))
    application.add_handler(CommandHandler("phone", cmd_phone))

    # === Phone monitor commands (НОВЫЕ!) ===
    application.add_handler(CommandHandler("phonestatus", cmd_phone_status))
    application.add_handler(CommandHandler("battery", cmd_battery))
    application.add_handler(CommandHandler("storage", cmd_storage))
    application.add_handler(CommandHandler("network", cmd_network))

    # === Blackhat commands ===
    application.add_handler(CommandHandler("blackhat", cmd_blackhat))
    application.add_handler(CommandHandler("unblackhat", cmd_unblackhat))
    application.add_handler(CommandHandler("blackhatmode", cmd_blackhatmode))
    application.add_handler(CommandHandler("blackhatlist", cmd_blackhatlist))
    application.add_handler(CommandHandler("blackhatroulette", cmd_blackhatroulette))

    # === Fun admin mute commands ===
    application.add_handler(CommandHandler("muteroulette", cmd_mute_roulette))
    application.add_handler(CommandHandler("reversemute", cmd_reverse_mute))
    application.add_handler(CommandHandler("roulette", cmd_russian_roulette))
    application.add_handler(CommandHandler("muteduel", cmd_mute_duel))
    application.add_handler(CommandHandler("randommute", cmd_random_mute))
    application.add_handler(CommandHandler("mutewheel", cmd_mute_wheel))
    application.add_handler(CommandHandler("mutelottery", cmd_mute_lottery))

    # === Callbacks ===
    application.add_handler(CallbackQueryHandler(handle_callback))

    # === Messages ===
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # === Errors ===
    application.add_error_handler(error_handler)

    logger.info("🚀 Бот запущен! Нажми Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
EOF
