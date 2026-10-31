import hashlib
import logging
import os
import time
from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from data import menu_items
from models import Category, MenuItem, MenuResponse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("barista_menu")

CACHE_CONTROL = "max-age=60"

app = FastAPI(
    title="Barista Coffee Point menu API",
    description="Read only menu API for Kiosk displays and mobile app",
)

# Comma-separated origins, set via the CORS_ALLOWED_ORIGINS env var.
# Empty by default, so no cross-origin browser access until origins are configured.
allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s %s %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.middleware("http")
async def cache_menu_responses(request: Request, call_next):
    response = await call_next(request)
    if (
        request.method != "GET"
        or response.status_code != 200
        or not request.url.path.startswith("/menu")
    ):
        return response

    body = b"".join([chunk async for chunk in response.body_iterator])
    etag = f'"{hashlib.sha256(body).hexdigest()}"'
    if request.headers.get("if-none-match") == etag:
        return Response(
            status_code=304, headers={"ETag": etag, "Cache-Control": CACHE_CONTROL}
        )

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = CACHE_CONTROL
    return Response(
        content=body,
        status_code=200,
        headers=dict(response.headers),
        media_type=response.media_type,
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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/menu", response_model=MenuResponse)
def get_menu(
    category: Annotated[
        Category | None, Query(description="Filter by coffee, snacks or combos")
    ] = None,
    available_only: Annotated[
        bool, Query(description="Hide items that are sold out")
    ] = False,
):
    items = menu_items
    if category:
        items = [item for item in items if item.category == category]
        if not items:
            raise HTTPException(
                status_code=404, detail=f"No item found in category: {category}"
            )
    if available_only:
        items = [item for item in items if item.available]

    items = [MenuItem.model_validate(item) for item in items]
    return MenuResponse(count=len(items), items=items)


@app.get("/menu/{item_id}", response_model=MenuItem)
def get_item(item_id: int):
    for item in menu_items:
        if item.id == item_id:
            return MenuItem.model_validate(item)
    raise HTTPException(
        status_code=404, detail=f"Menu item with id {item_id} not found"
    )
