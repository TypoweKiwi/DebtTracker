import os

import pytest

from api.app import app as _app
from api.models import db


@pytest.fixture
def app():
    os.environ["USE_SQLITE"] = "1"
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
