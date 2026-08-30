import json
import os
import hashlib
from datetime import datetime

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users() -> dict:
    """Return the users dict, creating an empty users.json if none exists."""
    if not os.path.exists(USERS_FILE):
        save_users({})
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users: dict) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def register_user(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    users = load_users()
    if username in users:
        return False, "That username is already taken."

    users[username] = {
        "password_hash": _hash_password(password),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_users(users)
    return True, "Account created successfully."


def verify_user(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    users = load_users()
    username = username.strip()

    if username not in users:
        return False, "No account found with that username."
    if users[username]["password_hash"] != _hash_password(password):
        return False, "Incorrect password."
    return True, "Login successful."
