"""CRUD routes for debts."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from models import db, Debt


debts_bp = Blueprint("debts", __name__, url_prefix="/debts")

ALLOWED_STATUSES = {"open", "settled", "cancelled"}


def _auth_user_id() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(None, 1)[1]
    return None


@debts_bp.route("", methods=["GET"])
def list_debts():
    created_by = request.args.get("created_by")
    status = request.args.get("status")

    query = Debt.query
    if created_by:
        query = query.filter_by(created_by=created_by)
    if status:
        query = query.filter_by(status=status)

    debts = [debt.to_dict() for debt in query.order_by(Debt.created_at.desc()).all()]
    return jsonify({"items": debts}), 200


@debts_bp.route("", methods=["POST"])
def create_debt():
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip() or None
    status = (data.get("status") or "open").strip().lower()

    created_by = (data.get("created_by") or "").strip() or _auth_user_id()

    if not title:
        return jsonify({"error": "title is required"}), 400
    if not created_by:
        return jsonify({"error": "created_by is required"}), 400
    if status not in ALLOWED_STATUSES:
        return jsonify({"error": "invalid status"}), 400

    debt = Debt(
        title=title,
        description=description,
        created_by=created_by,
        status=status,
    )
    db.session.add(debt)
    db.session.commit()

    return jsonify(debt.to_dict()), 201


@debts_bp.route("/<debt_id>", methods=["GET"])
def get_debt(debt_id: str):
    debt = Debt.query.get(debt_id)
    if not debt:
        return jsonify({"error": "not found"}), 404
    return jsonify(debt.to_dict()), 200


@debts_bp.route("/<debt_id>", methods=["PUT"])
def update_debt(debt_id: str):
    debt = Debt.query.get(debt_id)
    if not debt:
        return jsonify({"error": "not found"}), 404

    data = request.get_json() or {}
    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400
        debt.title = title
    if "description" in data:
        description = (data.get("description") or "").strip()
        debt.description = description or None
    if "status" in data:
        status = (data.get("status") or "").strip().lower()
        if status not in ALLOWED_STATUSES:
            return jsonify({"error": "invalid status"}), 400
        debt.status = status

    db.session.add(debt)
    db.session.commit()
    return jsonify(debt.to_dict()), 200


@debts_bp.route("/<debt_id>", methods=["DELETE"])
def delete_debt(debt_id: str):
    debt = Debt.query.get(debt_id)
    if not debt:
        return jsonify({"error": "not found"}), 404

    db.session.delete(debt)
    db.session.commit()
    return jsonify({"ok": True}), 200
