import json
from decimal import Decimal
from pathlib import Path
from typing import get_args

from data import menu_items
from models import Category, MenuItem

MENU_FILE = Path(__file__).parent.parent / "menu.json"


def test_menu_file_entries_all_validate_as_menu_item():
    raw = json.loads(MENU_FILE.read_text(encoding="utf-8"))
    assert len(raw) == 10
    for entry in raw:
        MenuItem.model_validate(entry)


def test_data_module_loads_all_items():
    assert len(menu_items) == 10
    assert all(isinstance(item, MenuItem) for item in menu_items)


def test_ids_are_unique():
    ids = [item.id for item in menu_items]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"duplicate ids: {duplicates}"


def test_categories_are_allowed_values():
    allowed = set(get_args(Category))
    bad = [item.name for item in menu_items if item.category not in allowed]
    assert not bad, f"invalid category on: {bad}"


def test_prices_are_positive():
    bad = [item.name for item in menu_items if item.price <= Decimal(0)]
    assert not bad, f"non-positive price on: {bad}"


def test_names_are_not_empty():
    bad = [item.id for item in menu_items if not item.name.strip()]
    assert not bad, f"empty name on ids: {bad}"
