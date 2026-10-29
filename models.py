from decimal import Decimal
from typing import Literal
from pydantic import BaseModel

Category = Literal["coffee", "snacks", "combos"]


class MenuItem(BaseModel):
    id: int
    name: str
    category: Category
    price: Decimal
    description: str
    available: bool


class MenuResponse(BaseModel):
    status: str = "success"
    count: int
    items: list[MenuItem]
