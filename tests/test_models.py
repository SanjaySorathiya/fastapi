from decimal import Decimal

import pytest
from pydantic import ValidationError

from models import MenuItem, MenuResponse

VALID = {
    "id": 1,
    "name": "Masala coffee",
    "category": "coffee",
    "price": "30.00",
    "description": "desc",
    "available": True,
}


def test_menu_item_accepts_valid_data_and_parses_price_as_decimal():
    item = MenuItem.model_validate(VALID)
    assert item.price == Decimal("30.00")


@pytest.mark.parametrize("field", list(VALID))
def test_menu_item_rejects_missing_field(field):
    data = {k: v for k, v in VALID.items() if k != field}
    with pytest.raises(ValidationError):
        MenuItem.model_validate(data)


def test_menu_item_rejects_unknown_category():
    with pytest.raises(ValidationError):
        MenuItem.model_validate({**VALID, "category": "drinks"})


def test_menu_item_rejects_wrong_type_for_id():
    with pytest.raises(ValidationError):
        MenuItem.model_validate({**VALID, "id": "not-a-number"})


def test_menu_response_status_defaults_to_success():
    response = MenuResponse(count=0, items=[])
    assert response.status == "success"
