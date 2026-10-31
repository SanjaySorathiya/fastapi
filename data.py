import json
from pathlib import Path

from models import MenuItem

MENU_FILE = Path(__file__).parent / "menu.json"

with MENU_FILE.open(encoding="utf-8") as menu_file:
    menu_items: list[MenuItem] = [
        MenuItem.model_validate(item) for item in json.load(menu_file)
    ]
