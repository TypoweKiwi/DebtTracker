"""Authentication routes: register, login, me.

Simple token auth: for tests and local usage we return a token equal to the user's id. For production
replace with JWT/session logic.
"""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError

from api.models import db, User
from api.auth.hash import hash_password, needs_rehash, verify_password


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or "@" not in email:
        return jsonify({"error": "invalid email"}), 400
    if len(password) < 8:
        return jsonify({"error": "password too short (min 8)"}), 400

    pw_hash = hash_password(password)

    user = User(email=email, password_hash=pw_hash)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "email already exists"}), 400

    return jsonify({"id": user.id, "email": user.email}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "invalid credentials"}), 401

    if not verify_password(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    # If hash needs rehash (e.g. parameters changed), re-hash with current params and save
    if needs_rehash(user.password_hash):
        current_app.logger.info("Rehashing password for user %s", user.id)
        user.password_hash = hash_password(password)
        db.session.add(user)
        db.session.commit()

    # Simple token: return user's id as token for tests. Replace with JWT in production.
    return jsonify({"ok": True, "token": user.id}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(None, 1)[1]
    else:
        return jsonify({"error": "missing auth"}), 401

    user = User.query.get(token)
    if not user:
        return jsonify({"error": "invalid token"}), 401

    return jsonify(user.to_dict()), 200
