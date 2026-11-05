from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["name"] == "CYBER AI"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_capabilities_structure():
    r = client.get("/capabilities")
    assert r.status_code == 200
    features = r.json()["features"]
    # Capacités gratuites toujours actives
    assert features["osint_whois_dns"] is True
    assert features["osint_crtsh"] is True
    # Sans clé renseignée, les capacités payantes sont désactivées
    assert features["osint_shodan"] is False
    assert features["llm_remote"] is False
