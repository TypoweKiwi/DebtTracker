from __future__ import annotations

"""Password hashing utilities using Argon2.

Provides: hash_password, verify_password, needs_rehash.

Pepper support: an optional secret `PASSWORD_PEPPER` may be set in env and will
be appended to the plaintext before hashing. Do NOT store the pepper in the
repo. To rotate pepper, change the env and re-hash passwords (see comment below).
"""

import os
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


def _get_hasher() -> PasswordHasher:
    """Create a PasswordHasher from env-configured parameters.

    Env vars (optional): ARGON2_TIME_COST, ARGON2_MEMORY_COST, ARGON2_PARALLELISM
    """
    time_cost = int(os.getenv("ARGON2_TIME_COST", "2"))
    memory_cost = int(os.getenv("ARGON2_MEMORY_COST", "102400"))
    parallelism = int(os.getenv("ARGON2_PARALLELISM", "8"))
    return PasswordHasher(time_cost=time_cost, memory_cost=memory_cost, parallelism=parallelism)


def _apply_pepper(password: str) -> str:
    pepper = os.getenv("PASSWORD_PEPPER", "")
    return password + pepper if pepper else password


def hash_password(password: str) -> str:
    """Hash a plaintext password and return the encoded hash."""
    ph = _get_hasher()
    pwd = _apply_pepper(password)
    return ph.hash(pwd)


def verify_password(hash: str, password: str) -> bool:
    """Verify a plaintext password against a stored Argon2 hash."""
    ph = _get_hasher()
    pwd = _apply_pepper(password)
    try:
        return ph.verify(hash, pwd)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def needs_rehash(hash: str) -> bool:
    """Return True if the given hash needs rehash according to current Argon2 params."""
    ph = _get_hasher()
    try:
        return ph.check_needs_rehash(hash)
    except Exception:
        # if the hash is malformed etc., prefer rehash (will fail on verify though)
        return True
