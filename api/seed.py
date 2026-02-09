"""Seed mock data for local development."""
from __future__ import annotations

from datetime import datetime

from app import app
from auth.argon2_hash import hash_password
from models import db, User, Debt, DebtParticipant


def seed():
    with app.app_context():
        db.create_all()

        demo_email = "demo@example.com"
        roommate_email = "roommate@example.com"

        demo = User.query.filter_by(email=demo_email).first()
        if not demo:
            demo = User(email=demo_email, password_hash=hash_password("password123"))
            db.session.add(demo)

        roommate = User.query.filter_by(email=roommate_email).first()
        if not roommate:
            roommate = User(email=roommate_email, password_hash=hash_password("password123"))
            db.session.add(roommate)

        db.session.commit()

        existing_debt = Debt.query.filter_by(title="January Rent").first()
        if not existing_debt:
            debt = Debt(
                title="January Rent",
                description="Shared rent for January",
                created_by=demo.id,
                status="open",
                created_at=datetime.utcnow(),
            )
            db.session.add(debt)
            db.session.commit()

            participant = DebtParticipant(
                debt_id=debt.id,
                from_user_id=demo.id,
                to_user_id=roommate.id,
                amount=500,
                description="Rent split",
                status="open",
            )
            db.session.add(participant)
            db.session.commit()

        print("Mock data ready.")


if __name__ == "__main__":
    seed()
