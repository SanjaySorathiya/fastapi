import json
from pathlib import Path

import pytest

MENU_FILE = Path(__file__).parent.parent / "menu.json"


def test_get_item_returns_matching_record(client):
    expected = next(i for i in json.loads(MENU_FILE.read_text("utf-8")) if i["id"] == 1)
    response = client.get("/menu/1")
    body = response.json()
    assert response.status_code == 200
    assert body["id"] == 1
    assert body["name"] == expected["name"]
    assert body["category"] == expected["category"]
    assert body["available"] is expected["available"]


def test_get_item_price_is_json_string(client):
    # Pydantic v2 serialises Decimal as a string; this is part of the API contract.
    assert client.get("/menu/1").json()["price"] == "30.00"


@pytest.mark.parametrize("item_id", [999, 0, -1])
def test_get_item_returns_404_for_unknown_id(client, item_id):
    response = client.get(f"/menu/{item_id}")
    assert response.status_code == 404
    assert response.json() == {
        "status": "error",
        "message": f"Menu item with id {item_id} not found",
    }


def test_get_item_returns_422_for_non_integer_id(client):
    response = client.get("/menu/abc")
    assert response.status_code == 422
    assert response.json()["status"] == "error"
