import functools
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services import user_manager

logger = logging.getLogger(__name__)


def _get_username(update: Update) -> str | None:
    user = update.effective_user
    if user is None:
        return None
    return user.username


def authorized_only(func):
    """Decorator: only allow authorized users."""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        username = _get_username(update)
        if not username:
            await update.effective_message.reply_text(
                "⚠️ Пожалуйста, установите имя пользователя Telegram в настройках профиля, чтобы использовать этого бота."
            )
            return
        if not user_manager.is_authorized(username):
            await update.effective_message.reply_text(
                "🚫 Доступ запрещён. Обратитесь к администратору для получения доступа."
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


def admin_only(func):
    """Decorator: only allow admin users."""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        username = _get_username(update)
        if not username:
            await update.effective_message.reply_text(
                "⚠️ Пожалуйста, установите имя пользователя Telegram в настройках профиля, чтобы использовать этого бота."
            )
            return
        if not user_manager.is_admin(username):
            await update.effective_message.reply_text(
                "🚫 Эта команда доступна только администраторам."
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper
