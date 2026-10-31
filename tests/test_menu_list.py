import pytest

import main


def test_get_menu_returns_all_items(client):
    response = client.get("/menu")
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "success"
    assert body["count"] == 10
    assert len(body["items"]) == 10


@pytest.mark.parametrize(
    ("category", "expected_count"),
    [("coffee", 4), ("snacks", 3), ("combos", 3)],
)
def test_get_menu_filters_by_category(client, category, expected_count):
    body = client.get("/menu", params={"category": category}).json()
    assert body["count"] == expected_count
    assert len(body["items"]) == body["count"]
    assert {item["category"] for item in body["items"]} == {category}


@pytest.mark.parametrize("category", ["COFFEE", "unknown", "snack"])
def test_get_menu_rejects_invalid_category(client, category):
    response = client.get("/menu", params={"category": category})
    assert response.status_code == 422
    assert response.json()["status"] == "error"


def test_get_menu_available_only_hides_sold_out_items(client):
    body = client.get("/menu", params={"available_only": "true"}).json()
    assert body["count"] == 9
    assert all(item["available"] for item in body["items"])


def test_get_menu_includes_sold_out_items_by_default(client):
    items = client.get("/menu").json()["items"]
    assert any(not item["available"] for item in items)


def test_get_menu_combines_category_and_available_only(client):
    body = client.get(
        "/menu", params={"category": "snacks", "available_only": "true"}
    ).json()
    assert body["count"] == 2
    assert {item["category"] for item in body["items"]} == {"snacks"}
    assert all(item["available"] for item in body["items"])


def test_get_menu_rejects_invalid_available_only(client):
    response = client.get("/menu", params={"available_only": "notabool"})
    assert response.status_code == 422


def test_get_menu_returns_404_for_category_with_no_items(
    client, monkeypatch, sample_menu
):
    monkeypatch.setattr(main, "menu_items", [sample_menu[0]])
    response = client.get("/menu", params={"category": "combos"})
    assert response.status_code == 404
    assert response.json() == {
        "status": "error",
        "message": "No item found in category: combos",
    }


def test_get_menu_uses_patched_data(client, monkeypatch, sample_menu):
    monkeypatch.setattr(main, "menu_items", sample_menu)
    body = client.get("/menu").json()
    assert body["count"] == 3
    assert [item["id"] for item in body["items"]] == [1, 2, 3]
