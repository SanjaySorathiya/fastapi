from typing import TypedDict

class MenuItemData(TypedDict):
    id: int
    name: str
    category: str
    price: float
    description: str
    available: bool

menu_items: list[MenuItemData] = [
    {
        "id": 1,
        "name": "Masala coffee",
        "category": "coffee",
        "price": 30.0,
        "description": "Classic Indian spiced coffee with ginger and cardamom",
        "available": True,
    },
    {
        "id": 2,
        "name": "Adrak coffee",
        "category": "coffee",
        "price": 35.0,
        "description": "Extra ginger coffee for cold evenings",
        "available": True,
    },
    {
        "id": 3,
        "name": "Elaichi coffee",
        "category": "coffee",
        "price": 40.0,
        "description": "Cardamom-infused premium coffee",
        "available": True,
    },
    {
        "id": 4,
        "name": "Cutting coffee",
        "category": "coffee",
        "price": 15.0,
        "description": "Half-size strong coffee, Mumbai tapri style",
        "available": True,
    },
    {
        "id": 5,
        "name": "Samosa",
        "category": "snacks",
        "price": 25.0,
        "description": "Crispy potato-filled pastry with mint chutney",
        "available": True,
    },
    {
        "id": 6,
        "name": "Vada Pav",
        "category": "snacks",
        "price": 30.0,
        "description": "Spicy potato fritter in a bun with garlic chutney",
        "available": False,
    },
    {
        "id": 7,
        "name": "Bun Maska",
        "category": "snacks",
        "price": 35.0,
        "description": "Soft bun with generous butter, Irani cafe style",
        "available": True,
    },
    {
        "id": 8,
        "name": "Coffee + Samosa Combo",
        "category": "combos",
        "price": 50.0,
        "description": "Masala coffee paired with a fresh samosa",
        "available": True,
    },
    {
        "id": 9,
        "name": "Coffee + Bun Maska Combo",
        "category": "combos",
        "price": 60.0,
        "description": "Elaichi coffee with warm bun maska",
        "available": True,
    },
    {
        "id": 10,
        "name": "Office Party Pack",
        "category": "combos",
        "price": 250.0,
        "description": "5 masala coffees + 5 samosas for team meetings",
        "available": True,
    },
]
