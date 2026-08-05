"""
auth.py — User Authentication & Account Management Engine
==========================================================
Handles user registration, password hashing (SHA-256), login validation,
and persistence to a users.json database.
"""

import hashlib
import json
import logging
from pathlib import Path

from email_notifier import send_registration_notification

logger = logging.getLogger(__name__)

USER_DB_FILE = Path("users.json")


def _hash_password(password: str) -> str:
    """Return SHA-256 hash of password string."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_user_db():
    """Ensure user database exists with default admin account."""
    if not USER_DB_FILE.exists():
        default_db = {
            "admin": {
                "name": "Recruiter Admin",
                "username": "admin",
                "password_hash": _hash_password("password123"),
                "created_at": "2026-08-05T00:00:00",
            }
        }
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, indent=2)
        logger.info("Initialized default users.json database with admin user")


def load_users() -> dict:
    """Load user dictionary from users.json."""
    init_user_db()
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading users.json: {e}")
        return {}


def save_users(users: dict):
    """Save user dictionary to users.json."""
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def authenticate_user(username_or_email: str, password: str) -> tuple[bool, dict | str]:
    """
    Authenticate a user by username/email and password.

    Returns:
        (True, user_data_dict) if valid, or (False, error_message) if invalid.
    """
    username_clean = username_or_email.strip().lower()
    if not username_clean or not password:
        return False, "Please enter both username and password."

    users = load_users()
    user = users.get(username_clean)

    if not user:
        return False, "User account not found. Please register or check username."

    pass_hash = _hash_password(password)
    if user.get("password_hash") == pass_hash:
        return True, user
    else:
        return False, "Incorrect password. Please try again."


def register_user(name: str, username_or_email: str, password: str) -> tuple[bool, str]:
    """
    Register a new user account.

    Returns:
        (True, "Success message") or (False, "Error message").
    """
    name_clean = name.strip()
    username_clean = username_or_email.strip().lower()

    if not name_clean:
        return False, "Full Name is required."
    if not username_clean:
        return False, "Username or Email is required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."

    users = load_users()
    if username_clean in users:
        return False, f"Username '{username_clean}' already exists. Please choose another."

    new_user_data = {
        "name": name_clean,
        "username": username_clean,
        "password_hash": _hash_password(password),
    }
    users[username_clean] = new_user_data

    save_users(users)
    logger.info(f"Registered new user account: {username_clean}")

    # Trigger admin email notification in background
    try:
        send_registration_notification(new_user_data)
    except Exception as e:
        logger.warning(f"Could not trigger registration email: {e}")

    return True, f"Account for {name_clean} created successfully! You can now sign in."
