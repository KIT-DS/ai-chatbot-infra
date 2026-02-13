import base64
import logging
import re

from aiohttp import web
from telegram.constants import ParseMode

from bot.config import N8N_WEBHOOK_USER, N8N_WEBHOOK_PASS

logger = logging.getLogger(__name__)

# Will be set by main.py after the Application is built
_bot_app = None

# Telegram message length limit
MAX_MESSAGE_LENGTH = 4096


def set_bot_app(app):
    """Store reference to the telegram Application for sending messages."""
    global _bot_app
    _bot_app = app


def _format_response(response_text: str) -> str:
    """
    Format response text for better readability in Telegram.
    Converts plain text citations to Markdown format.
    """
    # Clean up extra whitespace
    response_text = re.sub(r'\n{3,}', '\n\n', response_text)
    
    # Format sources section
    if '📚 Sources:' in response_text or '⚖️ Legal Sources:' in response_text or '📋 Project Sources:' in response_text:
        # Add separator before sources
        response_text = re.sub(
            r'(\n\n)(📚|⚖️|📋) (Sources|Legal Sources|Project Sources):',
            r'\n\n━━━━━━━━━━━━━━━\n\2 \3:',
            response_text
        )
    
    # Make source filenames bold
    response_text = re.sub(
        r'([\w\-]+\.(pdf|docx|txt|xlsx|csv))',
        r'*\1*',
        response_text
    )
    
    # Escape special Markdown characters in main text (but not in already formatted parts)
    # This is a simplified approach - you might need more sophisticated escaping
    
    return response_text.strip()


def _split_long_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list:
    """
    Split long messages into chunks that fit Telegram's limit.
    Tries to split at paragraph boundaries.
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by paragraphs
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        # If single paragraph is too long, split by sentences
        if len(para) > max_length:
            sentences = re.split(r'([.!?]\s+)', para)
            for i in range(0, len(sentences), 2):
                sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '')
                
                if len(current_chunk) + len(sentence) + 2 > max_length:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += ('\n\n' if current_chunk else '') + sentence
        else:
            if len(current_chunk) + len(para) + 2 > max_length:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += ('\n\n' if current_chunk else '') + para
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def _check_basic_auth(request: web.Request) -> bool:
    """Validate Basic Auth credentials from the request."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
        username, password = decoded.split(":", 1)
        return username == N8N_WEBHOOK_USER and password == N8N_WEBHOOK_PASS
    except Exception:
        return False


async def handle_n8n_response(request: web.Request) -> web.Response:
    """
    Receive async responses from n8n and forward them to the Telegram user.

    Expected JSON payload:
    {
        "chat_id": 123456789,
        "response": "Answer text from RAG pipeline...",
        "status": "success" | "clarification" | "error"  (optional)
    }
    """
    if not _check_basic_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)

    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    chat_id = data.get("chat_id")
    response_text = data.get("response") or data.get("output") or data.get("message") or data.get("answer")
    status = data.get("status", "success")

    if not chat_id or not response_text:
        logger.warning("Webhook received incomplete payload: %s", data)
        return web.json_response(
            {"error": "Missing 'chat_id' or 'response' field"}, status=400
        )

    if _bot_app is None:
        logger.error("Bot application not initialized")
        return web.json_response({"error": "Bot not ready"}, status=503)

    try:
        # Format response
        formatted_text = _format_response(response_text)
        
        # Add status emoji
        if status == "error":
            formatted_text = f"⚠️ *Error*\n\n{formatted_text}"
        elif status == "clarification":
            formatted_text = f"❓ *Clarification Needed*\n\n{formatted_text}"
        
        # Split if too long
        message_chunks = _split_long_message(formatted_text)
        
        # Send all chunks
        for i, chunk in enumerate(message_chunks):
            if i > 0:
                # Add continuation indicator
                chunk = f"*...continued*\n\n{chunk}"
            
            await _bot_app.bot.send_message(
                chat_id=chat_id,
                text=chunk,
                parse_mode=ParseMode.MARKDOWN
            )
        
        logger.info("Forwarded n8n response to chat_id=%s (status=%s, chunks=%d)", chat_id, status, len(message_chunks))
        return web.json_response({"status": "delivered", "chunks": len(message_chunks)})
    except Exception:
        logger.exception("Failed to send message to chat_id=%s", chat_id)
        return web.json_response({"error": "Failed to deliver message"}, status=500)


async def handle_n8n_ingest_response(request: web.Request) -> web.Response:
    """
    Receive ingestion result from n8n and forward to the admin.

    Expected JSON payload:
    {
        "chat_id": 123456789,
        "message": "Document ingested: 12 chunks stored in 'finance' namespace.",
        "status": "success" | "error"
    }
    """
    if not _check_basic_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)

    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    chat_id = data.get("chat_id")
    message = data.get("message") or data.get("response", "")
    status = data.get("status", "success")

    if not chat_id:
        return web.json_response({"error": "Missing 'chat_id'"}, status=400)

    if _bot_app is None:
        return web.json_response({"error": "Bot not ready"}, status=503)

    if not message:
        message = "✅ *Document ingested successfully*" if status == "success" else "⚠️ *Ingestion failed*"
    else:
        # Format the message
        message = _format_response(message)
        if status == "error":
            message = f"❌ *Error*\n\n{message}"

    try:
        await _bot_app.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info("Forwarded ingestion result to chat_id=%s (status=%s)", chat_id, status)
        return web.json_response({"status": "delivered"})
    except Exception:
        logger.exception("Failed to send ingestion result to chat_id=%s", chat_id)
        return web.json_response({"error": "Failed to deliver message"}, status=500)


async def handle_health(request: web.Request) -> web.Response:
    """Health check endpoint."""
    return web.json_response({"status": "ok"})


def create_webhook_app() -> web.Application:
    """Create the aiohttp web application with routes."""
    app = web.Application()
    app.router.add_post("/webhook/response", handle_n8n_response)
    app.router.add_post("/webhook/ingest-result", handle_n8n_ingest_response)
    app.router.add_get("/health", handle_health)
    return app
