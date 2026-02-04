import os

import pytest

from api.app import app as _app
from api.models import db, User
from api.auth.hash import hash_password


@pytest.fixture
def app():
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with _app.app_context():
        db.create_all()
        yield _app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_stores_hash_not_plain(client):
    resp = client.post("/auth/register", json={"email": "a@example.com", "password": "supersecret"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "password" not in data

    user = User.query.filter_by(email="a@example.com").first()
    assert user is not None
    assert user.password_hash != "supersecret"
    assert user.password_hash is not None


def test_register_existing_email_returns_400(client):
    client.post("/auth/register", json={"email": "a@example.com", "password": "supersecret"})
    resp = client.post("/auth/register", json={"email": "a@example.com", "password": "anotherpass"})
    assert resp.status_code == 400


def test_login_success_and_token_returned(client):
    client.post("/auth/register", json={"email": "b@example.com", "password": "mypassword"})
    resp = client.post("/auth/login", json={"email": "b@example.com", "password": "mypassword"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("ok") is True
    assert "token" in data


def test_login_bad_password_returns_401(client):
    client.post("/auth/register", json={"email": "c@example.com", "password": "rightone"})
    resp = client.post("/auth/login", json={"email": "c@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_rehashes_when_needed(client, monkeypatch):
    # Create an old weak hash (simulate previous params)
    monkeypatch.setenv("ARGON2_TIME_COST", "1")
    monkeypatch.setenv("ARGON2_MEMORY_COST", "1024")
    monkeypatch.setenv("ARGON2_PARALLELISM", "1")

    weak_hash = hash_password("rehashme")

    # Insert user with weak hash directly
    user = User(email="rehash@example.com", password_hash=weak_hash)
    db.session.add(user)
    db.session.commit()

    # Now bump Argon2 params to stronger values so needs_rehash() becomes True
    monkeypatch.setenv("ARGON2_TIME_COST", "3")
    monkeypatch.setenv("ARGON2_MEMORY_COST", "65536")
    monkeypatch.setenv("ARGON2_PARALLELISM", "2")

    # Login should succeed and trigger rehash
    resp = client.post("/auth/login", json={"email": "rehash@example.com", "password": "rehashme"})
    assert resp.status_code == 200

    user_after = User.query.filter_by(email="rehash@example.com").first()
    assert user_after is not None
    assert user_after.password_hash != weak_hash
    # And new hash still verifies
    from api.auth.hash import verify_password

    assert verify_password(user_after.password_hash, "rehashme")


def test_password_hash_not_equal_plaintext_unit():
    h = hash_password("somepass")
    assert h != "somepass"
