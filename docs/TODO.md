# TODO: Barista Coffee Point Menu API

Enhancement backlog for the read-only menu API that serves the Barista Coffee, London kiosk displays and mobile app.

## 1. Bugs (fix first)

- [x] **Category name mismatch.** The `/menu` docstring says "coffee, snack or combo", but the data uses `snacks` and `combos`. `GET /menu?category=snack` returns 404 for a valid category.
  - Pick one set of names (plural, matching the data) and make the docs match.
  - Type the query parameter as `Literal["coffee", "snacks", "combos"]` or an `Enum` so FastAPI validates it and `/docs` lists the valid values.

## 2. Tests

There are no tests and no test dependencies yet.

- [ ] Add `pytest` and `httpx` (required by FastAPI's `TestClient`) to the dev requirements.
- [ ] Create a `tests/` folder with a `conftest.py` that builds the `TestClient`.
- [ ] `GET /` returns the welcome message.
- [ ] `GET /menu` returns all 10 items and `count == 10`.
- [ ] `GET /menu?category=coffee` returns only coffee items, and `count` matches the list length.
- [ ] `GET /menu?category=COFFEE` returns 422 (the category is a case-sensitive `Literal`; uppercase is rejected).
- [ ] `GET /menu?category=unknown` returns 422 (validation error from the `Literal`).
- [ ] `GET /menu/{id}` returns the item.
- [ ] `GET /menu/{id}` with an unknown id returns 404.
- [ ] Data integrity: every id is unique, every category is in the allowed set, and every price is positive. This catches typos in `data.py` before they reach a kiosk.
- [ ] `/openapi.json` includes the `category` parameter.
- [ ] Run the suite with `pytest`.

## 3. Code quality

- [ ] **Money as `Decimal` or integer paise.** `float` is unsafe for currency; totals in a cart would show rounding errors.
- [ ] **Single source of truth for item shape.** `MenuItemData` (TypedDict in `data.py`) duplicates `MenuItem` (Pydantic in `models.py`). Keep `MenuItem` and have `data.py` use it.
- [ ] **Constrain `category`.** It is a free `str` in the model; use a `Literal` or `Enum`.
- [ ] **Clean up `main.py`.**
  - Remove commented-out code (lines 25 and 29).
  - Fix the typo `cateory` in the comment at line 16.
  - Remove the stray comment-style leftovers.
- [ ] **Consistent model building.** `get_menu` builds `MenuItem` objects, but `get_item` returns the raw dict. Use `MenuItem.model_validate` in both.
- [ ] **Availability filter.** `available` is in the data but unused. Add `?available_only=true` (default `false`) so kiosks can hide sold-out items such as Vada Pav.
- [ ] **Consistent error responses.** Use a custom exception handler, or keep `HTTPException` and make every error share one format.

## 4. Operations

- [ ] **HTTP caching.** The menu changes rarely. Send `Cache-Control: max-age=60` and an `ETag` to cut server load and speed up kiosks.
- [ ] **Pin dependencies.** `fastapi` and `uvicorn[standard]` are unpinned in `requirements.txt`. Generate a lock file (`pip freeze`, `uv`, or `pip-tools`) for reproducible builds.
- [ ] **CORS.** If the mobile app runs as a web view or PWA, add `CORSMiddleware` with an explicit origin list.
- [ ] **Health check.** Add `GET /health` for uptime monitors and kiosk status checks.
- [ ] **Logging.** Add basic request logging.
- [ ] **Docker.** Add a small `Dockerfile` (python-slim base, `uvicorn main:app --host 0.0.0.0`).
- [ ] **CI.** Add a GitHub Actions workflow that installs requirements and runs `pytest` on every push and PR.
- [ ] **Check `.gitignore`.** Confirm `venv/` is excluded before committing.

## 5. Documentation

- [ ] Expand `README.md` (currently one sentence) with:
  - Setup: `python -m venv venv`, install requirements, `uvicorn main:app --reload`.
  - Example requests for each endpoint.
  - The `/docs` URL for interactive API docs.
  - How to run the tests.

## 6. Longer term

- [ ] **Move data out of code.** A JSON or YAML file lets the shop change the menu without a code change.
- [ ] **Database and admin.** Later, a SQLite or Postgres table with an authenticated admin endpoint for edits.
- [ ] **Separate write path.** Keep the public API read-only; put any admin writes in a separate, authenticated service.
- [ ] **Richer item data.** Add image URLs and allergen information for kiosk displays.

## Suggested order

1. Fix the category name mismatch.
2. Add tests and the data integrity checks.
3. Clean up the models and `main.py`.
4. Pin dependencies, expand the README, and commit (none of the Python files are committed yet).
5. Add CI, Docker, and caching.
