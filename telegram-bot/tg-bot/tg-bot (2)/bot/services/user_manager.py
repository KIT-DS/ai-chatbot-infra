import json
import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from bot.config import DATA_DIR, USERS_FILE, FIRST_ADMIN_USERNAME

logger = logging.getLogger(__name__)


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_users() -> dict:
    """Load users from JSON file. Bootstrap if file doesn't exist."""
    _ensure_data_dir()
    if not USERS_FILE.exists():
        logger.info("users.json not found — bootstrapping with first admin: %s", FIRST_ADMIN_USERNAME)
        now = datetime.now(timezone.utc).isoformat()
        data = {
            "admins": {
                FIRST_ADMIN_USERNAME: {"added_by": "system", "added_at": now}
            },
            "users": {
                FIRST_ADMIN_USERNAME: {"added_by": "system", "added_at": now}
            },
        }
        save_users(data)
        return data

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data: dict):
    """Atomically write users data to disk."""
    _ensure_data_dir()
    tmp_fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".json")
    try:
        with open(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        Path(tmp_path).replace(USERS_FILE)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


def is_authorized(username: str) -> bool:
    if not username:
        return False
    data = load_users()
    return username.lower() in {k.lower() for k in data.get("users", {})}


def is_admin(username: str) -> bool:
    if not username:
        return False
    data = load_users()
    return username.lower() in {k.lower() for k in data.get("admins", {})}


def add_user(username: str, added_by: str) -> tuple[bool, str]:
    """Add a user. Returns (success, message)."""
    username = username.lower().lstrip("@")
    data = load_users()
    if username in {k.lower() for k in data["users"]}:
        return False, f"⚠️ Пользователь @{username} уже авторизован."
    now = datetime.now(timezone.utc).isoformat()
    data["users"][username] = {"added_by": added_by, "added_at": now}
    save_users(data)
    return True, f"✅ Пользователь @{username} добавлен."


def remove_user(username: str, removed_by: str) -> tuple[bool, str]:
    """Remove a user (and admin status). Returns (success, message)."""
    username = username.lower().lstrip("@")
    if username == removed_by.lower():
        return False, "⚠️ Вы не можете удалить самого себя."
    data = load_users()
    # Find actual key (case-insensitive)
    user_key = next((k for k in data["users"] if k.lower() == username), None)
    if user_key is None:
        return False, f"⚠️ Пользователь @{username} не найден."
    del data["users"][user_key]
    # Also remove from admins if present
    admin_key = next((k for k in data["admins"] if k.lower() == username), None)
    if admin_key:
        del data["admins"][admin_key]
    save_users(data)
    return True, f"✅ Пользователь @{username} удалён."


def add_admin(username: str, added_by: str) -> tuple[bool, str]:
    """Promote a user to admin. Returns (success, message)."""
    username = username.lower().lstrip("@")
    data = load_users()
    if username not in {k.lower() for k in data["users"]}:
        return False, f"⚠️ @{username} не является авторизованным пользователем. Сначала добавьте через /adduser."
    if username in {k.lower() for k in data["admins"]}:
        return False, f"⚠️ @{username} уже является администратором."
    now = datetime.now(timezone.utc).isoformat()
    data["admins"][username] = {"added_by": added_by, "added_at": now}
    save_users(data)
    return True, f"✅ @{username} назначен администратором."


def remove_admin(username: str, removed_by: str) -> tuple[bool, str]:
    """Demote an admin to regular user. Returns (success, message)."""
    username = username.lower().lstrip("@")
    data = load_users()
    admin_key = next((k for k in data["admins"] if k.lower() == username), None)
    if admin_key is None:
        return False, f"⚠️ @{username} не является администратором."
    if len(data["admins"]) <= 1:
        return False, "⚠️ Невозможно удалить последнего администратора."
    del data["admins"][admin_key]
    save_users(data)
    return True, f"✅ @{username} понижен до обычного пользователя."


def list_all_users() -> str:
    """Return a formatted string of all users and their roles."""
    data = load_users()
    admin_set = {k.lower() for k in data.get("admins", {})}
    lines = ["📋 *Авторизованные пользователи:*\n"]
    for username in sorted(data.get("users", {}).keys(), key=str.lower):
        role = "👑 Админ" if username.lower() in admin_set else "👤 Пользователь"
        lines.append(f"  • @{username} — {role}\n")
    if len(lines) == 1:
        lines.append("  _Нет зарегистрированных пользователей._\n")
    return "".join(lines)
