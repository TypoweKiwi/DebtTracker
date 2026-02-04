"""Password hashing utilities using Argon2.

Provides: hash_password, verify_password, needs_rehash.

Pepper support: an optional secret `PASSWORD_PEPPER` may be set in env and will
be appended to the plaintext before hashing. Do NOT store the pepper in the
repo. To rotate pepper, change the env and re-hash passwords (see comment below).
"""
from __future__ import annotations

import os
from typing import Optional

from argon2 import PasswordHasher, exceptions


def _get_ph() -> PasswordHasher:
    """Create a PasswordHasher configured from environment variables.

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
    """Hash `password` using Argon2 and return the encoded hash string.

    The optional `PASSWORD_PEPPER` env var is appended before hashing. The
    resulting string contains all parameters and salt needed for verification.
    """
    ph = _get_ph()
    pw = _apply_pepper(password)
    return ph.hash(pw)


def verify_password(hash: str, password: str) -> bool:
    """Verify `password` against `hash`. Returns True if valid, False otherwise."""
    ph = _get_ph()
    pw = _apply_pepper(password)
    try:
        return ph.verify(hash, pw)
    except exceptions.VerifyMismatchError:
        return False
    except Exception:
        # For any other verification/parsing error, consider auth failed.
        return False


def needs_rehash(hash: str) -> bool:
    """Return True if `hash` was created with older parameters and needs rehash.

    This uses the same parameters as returned by `_get_ph()`.
    """
    ph = _get_ph()
    try:
        return ph.check_needs_rehash(hash)
    except Exception:
        # If the hash is not parseable by current hasher, signal rehash requirement
        return True


# Pepper rotation note:
# If you change `PASSWORD_PEPPER`, existing stored hashes will no longer verify
# because the pepper is applied before hashing. To rotate pepper safely you can:
# - Keep the old pepper available server-side and verify against both, or
# - Force users to reset passwords on next login (recommended for limited rotation), or
# - Maintain a pepper version field per-user and re-hash on next successful login.
"""Utils for password hashing using Argon2.

Provides: hash_password, verify_password, needs_rehash.
Uses optional "pepper" from env var PASSWORD_PEPPER (do not store in repo).
Argon2 parameters can be customized via env vars: ARGON2_TIME_COST, ARGON2_MEMORY_COST, ARGON2_PARALLELISM.

Note on rotating pepper: to rotate pepper, change the PASSWORD_PEPPER env var and trigger a password reset
for users or perform a migration that re-hashes passwords after verifying old pepper. Keep old pepper
available to verify existing hashes until rotation is complete.
"""
from __future__ import annotations

import os
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


def _get_hasher() -> PasswordHasher:
    """Create a PasswordHasher from env-configured parameters."""
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


def needs_rehash(hash: str) -> bool:
    """Return True if the given hash needs rehash according to current Argon2 params."""
    ph = _get_hasher()
    try:
        return ph.check_needs_rehash(hash)
    except Exception:
        # if the hash is malformed etc., prefer rehash (will fail on verify though)
        return True
