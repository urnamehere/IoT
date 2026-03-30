"""Tests for the IoT Security Learning Tool."""

import pytest

from app import create_app, db
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"IoT Security" in response.data


def test_modules_page(client):
    response = client.get("/modules/")
    assert response.status_code == 200


def test_labs_page(client):
    response = client.get("/labs/")
    assert response.status_code == 200


def test_challenges_page(client):
    response = client.get("/challenges/")
    assert response.status_code == 200


def test_register(client):
    response = client.post("/register", data={
        "username": "testuser",
        "password": "testpass123",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Account created" in response.data


def test_login_logout(client):
    # Register first
    client.post("/register", data={
        "username": "testuser",
        "password": "testpass123",
    })

    # Logout
    client.get("/logout", follow_redirects=True)

    # Login
    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpass123",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_progress_api_requires_auth(client):
    response = client.post("/api/progress", json={
        "item_type": "module",
        "item_id": "01-iot-fundamentals",
        "status": "completed",
    })
    # Should redirect to login since not authenticated
    assert response.status_code in (302, 401)


def test_module_detail_404(client):
    response = client.get("/modules/nonexistent-module")
    assert response.status_code == 404
