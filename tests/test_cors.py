import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

import main

ALLOWED = "https://kiosk.example.com"
OTHER = "https://evil.example.com"


def load_app(monkeypatch, origins: str | None):
    """Load a private copy of main.py so CORS_ALLOWED_ORIGINS is re-read.

    The env var is read at import time, and the shared `main` module must
    stay untouched for the other tests.
    """
    if origins is None:
        monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("CORS_ALLOWED_ORIGINS", origins)
    spec = importlib.util.spec_from_file_location("main_cors_copy", Path(main.__file__))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return TestClient(module.app)


def test_no_cors_header_when_env_var_unset(monkeypatch):
    client = load_app(monkeypatch, None)
    response = client.get("/menu", headers={"Origin": ALLOWED})
    assert "access-control-allow-origin" not in response.headers


def test_configured_origin_receives_cors_header(monkeypatch):
    client = load_app(monkeypatch, ALLOWED)
    response = client.get("/menu", headers={"Origin": ALLOWED})
    assert response.headers["access-control-allow-origin"] == ALLOWED


def test_other_origin_does_not_receive_cors_header(monkeypatch):
    client = load_app(monkeypatch, ALLOWED)
    response = client.get("/menu", headers={"Origin": OTHER})
    assert "access-control-allow-origin" not in response.headers


def test_multiple_origins_are_comma_separated(monkeypatch):
    client = load_app(monkeypatch, f"{ALLOWED}, {OTHER}")
    for origin in (ALLOWED, OTHER):
        response = client.get("/menu", headers={"Origin": origin})
        assert response.headers["access-control-allow-origin"] == origin


def test_preflight_for_post_is_rejected(monkeypatch):
    client = load_app(monkeypatch, ALLOWED)
    response = client.options(
        "/menu",
        headers={
            "Origin": ALLOWED,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 400
    assert "POST" not in response.headers.get("access-control-allow-methods", "")
