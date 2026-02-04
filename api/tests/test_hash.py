import os

from api.auth.argon2_hash import hash_password, verify_password, needs_rehash


def test_argon_hash_verify_and_needs_rehash(monkeypatch):
    # Create a weak hash with low Argon2 params
    monkeypatch.setenv("ARGON2_TIME_COST", "1")
    monkeypatch.setenv("ARGON2_MEMORY_COST", "1024")
    monkeypatch.setenv("ARGON2_PARALLELISM", "1")

    pw = "testpassword"
    weak_hash = hash_password(pw)

    # Verify works with the same password
    assert verify_password(weak_hash, pw)

    # Bump params to stronger values
    monkeypatch.setenv("ARGON2_TIME_COST", "3")
    monkeypatch.setenv("ARGON2_MEMORY_COST", "65536")
    monkeypatch.setenv("ARGON2_PARALLELISM", "2")

    # The existing weak hash should be considered for rehash
    assert needs_rehash(weak_hash)

    # Re-hash with current (strong) params and ensure new hash verifies
    new_hash = hash_password(pw)
    assert new_hash != weak_hash
    assert verify_password(new_hash, pw)
