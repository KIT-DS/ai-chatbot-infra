import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
N8N_QUERY_WEBHOOK_URL = os.environ["N8N_QUERY_WEBHOOK_URL"]
N8N_INGEST_WEBHOOK_URL = os.environ["N8N_INGEST_WEBHOOK_URL"]
FIRST_ADMIN_USERNAME = os.getenv("FIRST_ADMIN_USERNAME", "kirun13")
N8N_WEBHOOK_USER = os.environ["N8N_WEBHOOK_USER"]
N8N_WEBHOOK_PASS = os.environ["N8N_WEBHOOK_PASS"]

WEBHOOK_SERVER_HOST = os.getenv("WEBHOOK_SERVER_HOST", "0.0.0.0")
WEBHOOK_SERVER_PORT = int(os.getenv("WEBHOOK_SERVER_PORT", "8080"))

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
USERS_FILE = DATA_DIR / "users.json"

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".xlsx", ".csv"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
}

NAMESPACES = ["finance", "legal", "project"]
