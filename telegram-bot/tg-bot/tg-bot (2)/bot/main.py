import asyncio
import logging

from aiohttp import web
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.config import TELEGRAM_BOT_TOKEN, WEBHOOK_SERVER_HOST, WEBHOOK_SERVER_PORT
from bot.handlers.admin import (
    add_admin_cmd,
    add_user_cmd,
    list_users_cmd,
    remove_admin_cmd,
    remove_user_cmd,
)
from bot.handlers.common import error_handler, help_cmd, start_cmd
from bot.handlers.document import (
    NAMESPACE_CALLBACK_PREFIX,
    handle_document,
    handle_namespace_callback,
)
from bot.handlers.query import handle_query
from bot.services.user_manager import load_users
from bot.webhook_server import create_webhook_app, set_bot_app

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def run():
    # Bootstrap users.json on first run
    load_users()
    logger.info("User database loaded.")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # General commands
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))

    # Admin commands
    app.add_handler(CommandHandler("adduser", add_user_cmd))
    app.add_handler(CommandHandler("removeuser", remove_user_cmd))
    app.add_handler(CommandHandler("addadmin", add_admin_cmd))
    app.add_handler(CommandHandler("removeadmin", remove_admin_cmd))
    app.add_handler(CommandHandler("listusers", list_users_cmd))

    # Document upload
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Query (plain text)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))

    # Namespace selection callback
    app.add_handler(
        CallbackQueryHandler(handle_namespace_callback, pattern=f"^{NAMESPACE_CALLBACK_PREFIX}")
    )

    # Error handler
    app.add_error_handler(error_handler)

    # Initialize the telegram app so the bot instance is available
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Give the webhook server access to the bot
    set_bot_app(app)

    # Start the webhook HTTP server for n8n callbacks
    webhook_app = create_webhook_app()
    runner = web.AppRunner(webhook_app)
    await runner.setup()
    site = web.TCPSite(runner, WEBHOOK_SERVER_HOST, WEBHOOK_SERVER_PORT)
    await site.start()
    logger.info("Webhook server listening on %s:%s", WEBHOOK_SERVER_HOST, WEBHOOK_SERVER_PORT)

    logger.info("Bot started. Press Ctrl+C to stop.")

    # Keep running until interrupted
    try:
        await asyncio.Event().wait()
    finally:
        logger.info("Shutting down...")
        await site.stop()
        await runner.cleanup()
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
