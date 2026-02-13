import logging
import os
import tempfile
import uuid

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from bot.config import ALLOWED_EXTENSIONS, NAMESPACES
from bot.services import n8n_client
from bot.services.text_extractor import UnsupportedFormatError, extract_text
from bot.utils.access import admin_only

logger = logging.getLogger(__name__)

NAMESPACE_CALLBACK_PREFIX = "ns:"


@admin_only
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file uploads for document ingestion."""
    document = update.message.document
    if not document:
        return

    file_name = document.file_name or "unknown"
    ext = os.path.splitext(file_name)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        await update.message.reply_text(
            f"⚠️ *Неподдерживаемый формат файла:* `{ext}`\n\n"
            f"*Допустимые форматы:* {allowed}",
            parse_mode="Markdown",
        )
        return

    await update.effective_chat.send_action(ChatAction.TYPING)

    # Download file to temp directory
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, file_name)

    try:
        tg_file = await document.get_file()
        await tg_file.download_to_drive(tmp_path)

        text = extract_text(tmp_path, file_name)
        char_count = len(text)

        # Store extracted data for callback
        doc_id = str(uuid.uuid4())[:8]
        context.user_data[doc_id] = {
            "text": text,
            "doc_title": file_name,
            "tmp_path": tmp_path,
            "tmp_dir": tmp_dir,
        }

        # Build namespace selection keyboard
        buttons = [
            InlineKeyboardButton(ns.capitalize(), callback_data=f"{NAMESPACE_CALLBACK_PREFIX}{doc_id}:{ns}")
            for ns in NAMESPACES
        ]
        keyboard = InlineKeyboardMarkup([buttons])

        safe_name = escape_markdown(file_name, version=2)
        await update.message.reply_text(
            f"📄 *Документ:* {safe_name}\n\n"
            f"✅ Извлечено *{char_count:,}* символов\.\n\n"
            f"*Выберите целевое пространство:*",
            reply_markup=keyboard,
            parse_mode="MarkdownV2",
        )

    except UnsupportedFormatError as e:
        await update.message.reply_text(f"⚠️ {e}")
        _cleanup(tmp_path, tmp_dir)
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
        _cleanup(tmp_path, tmp_dir)
    except Exception:
        logger.exception("Error processing uploaded file")
        await update.message.reply_text("⚠️ Не удалось обработать файл. Пожалуйста, попробуйте снова.")
        _cleanup(tmp_path, tmp_dir)


async def handle_namespace_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle namespace selection callback from inline buttons."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data or not data.startswith(NAMESPACE_CALLBACK_PREFIX):
        return

    payload = data[len(NAMESPACE_CALLBACK_PREFIX):]
    doc_id, namespace = payload.split(":", 1)

    doc_data = context.user_data.pop(doc_id, None)
    if doc_data is None:
        await query.edit_message_text("⚠️ Сессия истекла. Пожалуйста, загрузите файл заново.")
        return

    text = doc_data["text"]
    doc_title = doc_data["doc_title"]
    tmp_path = doc_data.get("tmp_path")
    tmp_dir = doc_data.get("tmp_dir")

    try:
        chat_id = update.effective_chat.id
        user_name = update.effective_user.username or str(update.effective_user.id)

        accepted = await n8n_client.send_document(chat_id, text, namespace, doc_title, user_name)

        if accepted:
            safe_title = escape_markdown(doc_title, version=2)
            safe_ns = escape_markdown(namespace, version=2)
            await query.edit_message_text(
                f"⏳ *Обработка документа*\n\n"
                f"📄 *Файл:* {safe_title}\n"
                f"📁 *Пространство:* `{safe_ns}`\n\n"
                f"Документ отправлен на обработку\. Вы получите уведомление по завершении\.",
                parse_mode="MarkdownV2",
            )
        else:
            await query.edit_message_text(
                "⚠️ *Сервис недоступен*\n\n"
                "Не удалось связаться с сервером обработки. Попробуйте позже.",
                parse_mode="Markdown"
            )
    except Exception:
        logger.exception("Error during document ingestion")
        await query.edit_message_text("⚠️ Не удалось обработать документ. Попробуйте снова.")
    finally:
        _cleanup(tmp_path, tmp_dir)


def _cleanup(tmp_path: str | None, tmp_dir: str | None):
    """Remove temp file and directory."""
    try:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        if tmp_dir and os.path.exists(tmp_dir):
            os.rmdir(tmp_dir)
    except OSError:
        pass
