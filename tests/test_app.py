import pytest
from app import create_app
from app.routes import MAX_MESSAGE_LENGTH


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "healthy"}


def test_chat_success(client):
    r = client.post("/api/chat", json={"message": "How can I manage my budget?"})
    assert r.status_code == 200
    assert "response" in r.get_json()


def test_empty_message(client):
    r = client.post("/api/chat", json={"message": "   "})
    assert r.status_code == 400


def test_missing_message(client):
    r = client.post("/api/chat", json={})
    assert r.status_code == 400


def test_invalid_json(client):
    r = client.post("/api/chat", data="{not json", content_type="application/json")
    assert r.status_code == 400


def test_message_too_long(client):
    r = client.post("/api/chat", json={"message": "a" * (MAX_MESSAGE_LENGTH + 1)})
    assert r.status_code == 413


@pytest.mark.parametrize("bad", [123, ["hi"], {"a": 1}, True])
def test_unexpected_type(client, bad):
    r = client.post("/api/chat", json={"message": bad})
    assert r.status_code == 400