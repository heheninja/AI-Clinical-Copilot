import json
import os
from typing import Dict

"""Simple doctor authentication helper.

This module provides a minimal, file-backed username/password check used by
the Streamlit UI. It's intentionally lightweight for development/demo use.

Security notes:
- Passwords are stored in plaintext in auth/doctors.json for convenience.
  Do NOT use this in production. Replace with hashed passwords (bcrypt) or an
  external auth provider (OAuth, identity service, etc.) before deploying.
"""

DOCTORS_FILE = os.path.join(os.path.dirname(__file__), "doctors.json")


def _load_doctors() -> Dict[str, str]:
    """Load doctors from auth/doctors.json and return a username->password map.

    If the file doesn't exist, return a sensible default for local testing.
    """

    if not os.path.exists(DOCTORS_FILE):
        # fallback/demo credentials
        return {"drkumar": "password123"}

    with open(DOCTORS_FILE, "r", encoding="utf-8") as f:
        docs = json.load(f)

    # expect a list of objects like: [{"username": "drkumar", "password": "..."}, ...]
    return {d["username"]: d["password"] for d in docs}


# simple in-memory cache so we don't read the file on every validation
_doctors_cache = None


def validate_doctor_credentials(username: str, password: str) -> bool:
    """Return True if the provided username/password are valid.

    This is an intentionally simple check for local/dev usage.
    """

    global _doctors_cache

    if not username or not password:
        return False

    if _doctors_cache is None:
        _doctors_cache = _load_doctors()

    return _doctors_cache.get(username) == password
