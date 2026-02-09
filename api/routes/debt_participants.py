"""CRUD routes for debt participants."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from models import db, Debt, DebtParticipant


debt_participants_bp = Blueprint("debt_participants", __name__, url_prefix="/debt-participants")

ALLOWED_STATUSES = {"open", "settled"}


def _auth_user_id() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(None, 1)[1]
    return None


def _parse_amount(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if amount <= 0:
        return None
    return amount


@debt_participants_bp.route("", methods=["GET"])
def list_participants():
    debt_id = request.args.get("debt_id")
    from_user_id = request.args.get("from_user_id")
    to_user_id = request.args.get("to_user_id")
    status = request.args.get("status")

    query = DebtParticipant.query
    if debt_id:
        query = query.filter_by(debt_id=debt_id)
    if from_user_id:
        query = query.filter_by(from_user_id=from_user_id)
    if to_user_id:
        query = query.filter_by(to_user_id=to_user_id)
    if status:
        query = query.filter_by(status=status)

    participants = [item.to_dict() for item in query.order_by(DebtParticipant.created_at.desc()).all()]
    return jsonify({"items": participants}), 200


@debt_participants_bp.route("", methods=["POST"])
def create_participant():
    data = request.get_json() or {}
    debt_id = (data.get("debt_id") or "").strip()
    from_user_id = (data.get("from_user_id") or "").strip() or _auth_user_id()
    to_user_id = (data.get("to_user_id") or "").strip()
    description = (data.get("description") or "").strip() or None
    status = (data.get("status") or "open").strip().lower()
    amount = _parse_amount(data.get("amount"))

    if not debt_id:
        return jsonify({"error": "debt_id is required"}), 400
    if not from_user_id:
        return jsonify({"error": "from_user_id is required"}), 400
    if not to_user_id:
        return jsonify({"error": "to_user_id is required"}), 400
    if amount is None:
        return jsonify({"error": "amount must be > 0"}), 400
    if status not in ALLOWED_STATUSES:
        return jsonify({"error": "invalid status"}), 400

    if not Debt.query.get(debt_id):
        return jsonify({"error": "debt not found"}), 404

    participant = DebtParticipant(
        debt_id=debt_id,
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        amount=amount,
        description=description,
        status=status,
    )
    db.session.add(participant)
    db.session.commit()

    return jsonify(participant.to_dict()), 201


@debt_participants_bp.route("/<participant_id>", methods=["GET"])
def get_participant(participant_id: str):
    participant = DebtParticipant.query.get(participant_id)
    if not participant:
        return jsonify({"error": "not found"}), 404
    return jsonify(participant.to_dict()), 200


@debt_participants_bp.route("/<participant_id>", methods=["PUT"])
def update_participant(participant_id: str):
    participant = DebtParticipant.query.get(participant_id)
    if not participant:
        return jsonify({"error": "not found"}), 404

    data = request.get_json() or {}
    if "from_user_id" in data:
        from_user_id = (data.get("from_user_id") or "").strip()
        if not from_user_id:
            return jsonify({"error": "from_user_id cannot be empty"}), 400
        participant.from_user_id = from_user_id
    if "to_user_id" in data:
        to_user_id = (data.get("to_user_id") or "").strip()
        if not to_user_id:
            return jsonify({"error": "to_user_id cannot be empty"}), 400
        participant.to_user_id = to_user_id
    if "amount" in data:
        amount = _parse_amount(data.get("amount"))
        if amount is None:
            return jsonify({"error": "amount must be > 0"}), 400
        participant.amount = amount
    if "description" in data:
        description = (data.get("description") or "").strip()
        participant.description = description or None
    if "status" in data:
        status = (data.get("status") or "").strip().lower()
        if status not in ALLOWED_STATUSES:
            return jsonify({"error": "invalid status"}), 400
        participant.status = status

    db.session.add(participant)
    db.session.commit()
    return jsonify(participant.to_dict()), 200


@debt_participants_bp.route("/<participant_id>", methods=["DELETE"])
def delete_participant(participant_id: str):
    participant = DebtParticipant.query.get(participant_id)
    if not participant:
        return jsonify({"error": "not found"}), 404

    db.session.delete(participant)
    db.session.commit()
    return jsonify({"ok": True}), 200
