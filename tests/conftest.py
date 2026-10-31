import pytest
from fastapi.testclient import TestClient

from main import app
from models import MenuItem


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_menu() -> list[MenuItem]:
    """Small known menu: one item per category, one sold out."""
    return [
        MenuItem(
            id=1,
            name="Test coffee",
            category="coffee",
            price="10.00",
            description="coffee",
            available=True,
        ),
        MenuItem(
            id=2,
            name="Test snack",
            category="snacks",
            price="5.00",
            description="snack",
            available=False,
        ),
        MenuItem(
            id=3,
            name="Test combo",
            category="combos",
            price="12.50",
            description="combo",
            available=True,
        ),
    ]
