from telegram import Update

from core.anti_flood import anti_flood


async def admin_only(update: Update) -> bool:
    """Проверяет, является ли пользователь админом"""
    user_id = update.effective_user.id
    if not anti_flood.is_admin(user_id):
        await update.message.reply_text("Только для админов. Ты кто такой?")
        return False
    return True
