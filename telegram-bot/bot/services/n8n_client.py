import logging
import httpx

from bot.config import N8N_QUERY_WEBHOOK_URL, N8N_INGEST_WEBHOOK_URL, N8N_WEBHOOK_USER, N8N_WEBHOOK_PASS

logger = logging.getLogger(__name__)

BASIC_AUTH = (N8N_WEBHOOK_USER, N8N_WEBHOOK_PASS)


async def send_query(chat_id: int, message_text: str, user_name: str) -> bool:
    """Send a user query to n8n. Returns True if n8n accepted it."""
    payload = {
        "chat_id": chat_id,
        "query": message_text,
        "user_name": user_name,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(N8N_QUERY_WEBHOOK_URL, json=payload, auth=BASIC_AUTH)
            resp.raise_for_status()
            return True
    except httpx.TimeoutException:
        logger.error("n8n query webhook timed out")
        return False
    except httpx.HTTPStatusError as e:
        logger.error("n8n query webhook returned %s", e.response.status_code)
        return False
    except Exception:
        logger.exception("Unexpected error calling n8n query webhook")
        return False


async def send_document(
    chat_id: int, text: str, namespace: str, doc_title: str, user_name: str
) -> bool:
    """Send extracted document text to n8n for ingestion. Returns True if accepted."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "namespace": namespace,
        "doc_title": doc_title,
        "user_name": user_name,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(N8N_INGEST_WEBHOOK_URL, json=payload, auth=BASIC_AUTH)
            resp.raise_for_status()
            return True
    except httpx.TimeoutException:
        logger.error("n8n ingest webhook timed out")
        return False
    except httpx.HTTPStatusError as e:
        logger.error("n8n ingest webhook returned %s", e.response.status_code)
        return False
    except Exception:
        logger.exception("Unexpected error calling n8n ingest webhook")
        return False
