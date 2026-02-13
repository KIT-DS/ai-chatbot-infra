import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services import user_manager
from bot.utils.access import authorized_only

logger = logging.getLogger(__name__)


@authorized_only
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    is_admin = user_manager.is_admin(username)

    text = (
        "👋 *Добро пожаловать в корпоративного RAG-ассистента!*\n\n"
        "Отправьте мне вопрос, и я найду ответ в наших внутренних документах.\n\n"
        "📝 *Доступные команды:*\n"
        "• /help — Показать доступные команды\n"
    )
    if is_admin:
        text += (
            "\n👑 *Команды администратора:*\n"
            "• /adduser @username — Авторизовать пользователя\n"
            "• /removeuser @username — Удалить пользователя\n"
            "• /addadmin @username — Назначить администратором\n"
            "• /removeadmin @username — Снять права администратора\n"
            "• /listusers — Показать всех пользователей\n\n"
            "📎 Загрузите документ (PDF, DOCX, TXT, XLSX, CSV) для добавления в базу знаний."
        )

    await update.message.reply_text(text, parse_mode="Markdown")


@authorized_only
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    is_admin = user_manager.is_admin(username)

    text = (
        "ℹ️ *Помощь*\n\n"
        "Просто отправьте мне текстовое сообщение с вашим вопросом, "
        "и я найду ответ в нашей внутренней базе знаний.\n\n"
        "📝 *Команды:*\n"
        "• /start — Приветственное сообщение\n"
        "• /help — Это сообщение помощи\n"
    )
    if is_admin:
        text += (
            "\n*Команды администратора:*\n"
            "• /adduser @username — Авторизовать пользователя\n"
            "• /removeuser @username — Удалить пользователя\n"
            "• /addadmin @username — Назначить администратором\n"
            "• /removeadmin @username — Снять права администратора\n"
            "• /listusers — Показать всех пользователей\n\n"
            "📎 *Загрузка документов:*\n"
            "Загрузите файл (PDF, DOCX, TXT, XLSX, CSV) и "
            "выберите целевое пространство (Финансы, Юридический, Проект)."
        )

    await update.message.reply_text(text, parse_mode="Markdown")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled exception:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ *Непредвиденная ошибка*\n\n"
            "Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.\n\n"
            "_Если проблема сохраняется, обратитесь к администратору._",
            parse_mode="Markdown"
        )
