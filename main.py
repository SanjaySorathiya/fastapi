from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from models import Category, MenuItem, MenuResponse
from data import menu_items

app = FastAPI(
    title="Barista Coffee Point menu API",
    description="Read only menu API for Kiosk displays and mobile app"
)


def error_response(
    status_code: int,
    message: str,
    errors: Sequence[Any] | None = None,
) -> JSONResponse:
    body = {"status": "error", "message": message}
    if errors is not None:
        body["errors"] = jsonable_encoder(errors)
    return JSONResponse(status_code=status_code, content=body)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return error_response(exc.status_code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(422, "Invalid request", exc.errors())


@app.get("/")
def root():
    return {"message": "Welcome to Barista Coffee Point Menu API"}


@app.get("/menu", response_model=MenuResponse)
def get_menu(
    category: Category | None = Query(None, description="Filter by coffee, snacks or combos"),
    available_only: bool = Query(False, description="Hide items that are sold out"),
):
    items = menu_items
    if category:
        items = [item for item in items if item.category == category]
        if not items:
            raise HTTPException(status_code=404, detail=f"No item found in category: {category}")
    if available_only:
        items = [item for item in items if item.available]

    items = [MenuItem.model_validate(item) for item in items]
    return MenuResponse(count=len(items), items=items)


@app.get("/menu/{item_id}", response_model=MenuItem)
def get_item(item_id: int):
    for item in menu_items:
        if item.id == item_id:
            return MenuItem.model_validate(item)
    raise HTTPException(status_code=404, detail=f"Menu item with id {item_id} not found")
