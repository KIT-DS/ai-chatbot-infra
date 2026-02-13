import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services import user_manager
from bot.utils.access import admin_only

logger = logging.getLogger(__name__)


def _parse_username(args: list[str]) -> str | None:
    """Extract username from command arguments like '/adduser @name' or '/adduser name'."""
    if not args:
        return None
    return args[0].lower().lstrip("@").strip()


@admin_only
async def add_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = _parse_username(context.args)
    if not username:
        await update.message.reply_text("Использование: /adduser @username")
        return
    admin = update.effective_user.username
    success, msg = user_manager.add_user(username, added_by=admin)
    await update.message.reply_text(msg)


@admin_only
async def remove_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = _parse_username(context.args)
    if not username:
        await update.message.reply_text("Использование: /removeuser @username")
        return
    admin = update.effective_user.username
    success, msg = user_manager.remove_user(username, removed_by=admin)
    await update.message.reply_text(msg)


@admin_only
async def add_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = _parse_username(context.args)
    if not username:
        await update.message.reply_text("Использование: /addadmin @username")
        return
    admin = update.effective_user.username
    success, msg = user_manager.add_admin(username, added_by=admin)
    await update.message.reply_text(msg)


@admin_only
async def remove_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = _parse_username(context.args)
    if not username:
        await update.message.reply_text("Использование: /removeadmin @username")
        return
    admin = update.effective_user.username
    success, msg = user_manager.remove_admin(username, removed_by=admin)
    await update.message.reply_text(msg)


@admin_only
async def list_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = user_manager.list_all_users()
    await update.message.reply_text(text, parse_mode="Markdown")
