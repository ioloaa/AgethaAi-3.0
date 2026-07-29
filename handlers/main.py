"""
AgethaAi Telegram Bot v8 — FPE Edition
Точка входа
"""
import logging

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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    """Инициализация после запуска бота"""
    bot = application.bot
    me = await bot.get_me()
    group_handler.bot_username = me.username
    logger.info(f"Бот инициализирован: @{me.username}")

    provider = settings.AI_PROVIDER
    groq_ok = bool(settings.get_groq_keys())
    gemini_ok = bool(settings.get_gemini_key())
    cerebras_ok = bool(settings.get_cerebras_key())

    if provider == "groq" and not groq_ok:
        logger.error("❌ GROQ_API_KEY не установлен!")
    elif provider == "gemini" and not gemini_ok:
        logger.error("❌ GEMINI_API_KEY не установлен!")
    elif provider == "cerebras" and not cerebras_ok:
        logger.error("❌ CEREBRAS_API_KEY не установлен!")
    else:
        logger.info(f"✅ API ключи настроены (провайдер: {provider})")

    if group_handler.allowed_topic_id is not None:
        logger.info(f"✅ Бот работает ТОЛЬКО в топике ID={group_handler.allowed_topic_id}")
    else:
        logger.info("ℹ️ Топик не ограничен — бот работает во всех темах группы")


def main():
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не найден!")
        print("\nУстанови переменную окружения:")
        print("  export TELEGRAM_BOT_TOKEN='твой_токен'")
        return

    application = Application.builder().token(token).post_init(post_init).build()

    # User commands
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("clear", cmd_clear))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("fact", cmd_fact))

    # Admin commands
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

    # Blackhat commands
    application.add_handler(CommandHandler("blackhat", cmd_blackhat))
    application.add_handler(CommandHandler("unblackhat", cmd_unblackhat))
    application.add_handler(CommandHandler("blackhatmode", cmd_blackhatmode))
    application.add_handler(CommandHandler("blackhatlist", cmd_blackhatlist))
    application.add_handler(CommandHandler("blackhatroulette", cmd_blackhatroulette))

    # Fun admin mute commands
    application.add_handler(CommandHandler("muteroulette", cmd_mute_roulette))
    application.add_handler(CommandHandler("reversemute", cmd_reverse_mute))
    application.add_handler(CommandHandler("roulette", cmd_russian_roulette))
    application.add_handler(CommandHandler("muteduel", cmd_mute_duel))
    application.add_handler(CommandHandler("randommute", cmd_random_mute))
    application.add_handler(CommandHandler("mutewheel", cmd_mute_wheel))
    application.add_handler(CommandHandler("mutelottery", cmd_mute_lottery))

    # Callbacks
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Errors
    application.add_error_handler(error_handler)

    logger.info("Бот запущен! Нажми Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
