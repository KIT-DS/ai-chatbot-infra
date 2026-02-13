import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from bot.services import n8n_client
from bot.utils.access import authorized_only

logger = logging.getLogger(__name__)


@authorized_only
async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plain text messages as RAG queries."""
    message_text = update.message.text
    if not message_text or not message_text.strip():
        return

    chat_id = update.effective_chat.id
    user_name = update.effective_user.username or str(update.effective_user.id)

    await update.effective_chat.send_action(ChatAction.TYPING)

    accepted = await n8n_client.send_query(chat_id, message_text, user_name)
    if accepted:
        await update.message.reply_text(
            "🔍 *Обрабатываю ваш запрос...*\n\n"
            "Ищу информацию в наших документах, скоро отвечу.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "⚠️ *Сервис недоступен*\n\n"
            "Не удалось связаться с AI-сервисом. Попробуйте через некоторое время.\n\n"
            "_Если проблема сохраняется, обратитесь к администратору._",
            parse_mode="Markdown"
        )
