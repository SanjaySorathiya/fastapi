def test_404_uses_error_envelope(client):
    body = client.get("/menu/999").json()
    assert set(body) == {"status", "message"}
    assert body["status"] == "error"


def test_422_uses_error_envelope_with_errors_list(client):
    body = client.get("/menu", params={"category": "unknown"}).json()
    assert body["status"] == "error"
    assert body["message"] == "Invalid request"
    assert isinstance(body["errors"], list)
    assert body["errors"]


def test_unknown_route_uses_error_envelope(client):
    response = client.get("/no-such-route")
    assert response.status_code == 404
    assert response.json()["status"] == "error"


def test_error_bodies_do_not_leak_internals(client):
    text = client.get("/menu/999").text + client.get("/menu/abc").text
    for leak in ("Traceback", ".py", "Exception"):
        assert leak not in text
