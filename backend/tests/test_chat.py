from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_models_includes_echo_stub():
    r = client.get("/chat/models")
    assert r.status_code == 200
    ids = {m["id"] for m in r.json()["models"]}
    assert "echo" in ids


def test_stream_echo_returns_user_text():
    payload = {
        "messages": [{"role": "user", "content": "bonjour"}],
        "model": "echo",
    }
    with client.stream("POST", "/chat/stream", json=payload) as resp:
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
        body = "".join(resp.iter_text())
    assert "bonjour" in body
    assert "[DONE]" in body
    # Le stub doit s'annoncer comme tel
    assert "STUB" in body


def test_unknown_model_falls_back_to_echo():
    payload = {
        "messages": [{"role": "user", "content": "test"}],
        "model": "modele-inexistant",
    }
    with client.stream("POST", "/chat/stream", json=payload) as resp:
        assert resp.status_code == 200
        body = "".join(resp.iter_text())
    assert "[DONE]" in body
