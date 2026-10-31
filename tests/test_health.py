def test_root_returns_welcome_message(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Barista Coffee Point Menu API"}


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_lists_documented_paths_and_category_parameter(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    for path in ("/", "/health", "/menu", "/menu/{item_id}"):
        assert path in schema["paths"]
    params = {p["name"] for p in schema["paths"]["/menu"]["get"]["parameters"]}
    assert {"category", "available_only"} <= params


def test_write_methods_are_not_allowed(client):
    for method in ("post", "put", "patch", "delete"):
        assert getattr(client, method)("/menu").status_code == 405
