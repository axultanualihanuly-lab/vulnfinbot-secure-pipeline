from app import create_app


def test_security_headers():
    client = create_app().test_client()
    r = client.get("/health")
    assert r.headers["Cache-Control"] == "no-store"
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["Server"] == "webserver"