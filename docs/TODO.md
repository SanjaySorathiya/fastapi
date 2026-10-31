# TODO: Barista Coffee Point Menu API

Enhancement backlog for the read-only menu API that serves the Barista Coffee, London kiosk displays and mobile app.

## 1. Bugs (fix first)

- [x] **Category name mismatch.** The `/menu` docstring says "coffee, snack or combo", but the data uses `snacks` and `combos`. `GET /menu?category=snack` returns 404 for a valid category.
  - Pick one set of names (plural, matching the data) and make the docs match.
  - Type the query parameter as `Literal["coffee", "snacks", "combos"]` or an `Enum` so FastAPI validates it and `/docs` lists the valid values.

## 2. Tests

The suite follows [TESTING_GUIDELINES.md](TESTING_GUIDELINES.md): 62 tests in `tests/`, 100% line coverage of `main.py`, `models.py` and `data.py`.

- [x] Add `pytest` and `httpx` (required by FastAPI's `TestClient`) to the dev requirements. `pytest-cov` and `ruff` were added too, all pinned.
- [x] Create a `tests/` folder with a `conftest.py` that builds the `TestClient`. `pytest.ini` sets `testpaths` and `pythonpath`.
- [x] `GET /` returns the welcome message.
- [x] `GET /menu` returns all 10 items and `count == 10`.
- [x] `GET /menu?category=coffee` returns only coffee items, and `count` matches the list length.
- [x] `GET /menu?category=COFFEE` returns 422 (the category is a case-sensitive `Literal`; uppercase is rejected).
- [x] `GET /menu?category=unknown` returns 422 (validation error from the `Literal`).
- [x] `GET /menu/{id}` returns the item.
- [x] `GET /menu/{id}` with an unknown id returns 404.
- [x] Data integrity: every id is unique, every category is in the allowed set, and every price is positive. This catches typos in `menu.json` before they reach a kiosk.
- [x] `/openapi.json` includes the `category` parameter.
- [x] Run the suite with `pytest`.
- [x] Also covered: `available_only`, the error envelope, ETag/304 caching, CORS, 405 on write methods, and the Pydantic models.
- [x] Remove the dummy `test_hello.py`.
- [ ] Optional: replace the `httpx` test client with `httpx2`. Starlette prints a deprecation warning during the test run.

## 3. Code quality

- [x] **Money as `Decimal` or integer paise.** `float` is unsafe for currency; totals in a cart would show rounding errors.
- [x] **Single source of truth for item shape.** `MenuItemData` (TypedDict in `data.py`) duplicates `MenuItem` (Pydantic in `models.py`). Keep `MenuItem` and have `data.py` use it.
- [x] **Constrain `category`.** It is a free `str` in the model; use a `Literal` or `Enum`.
- [x] **Clean up `main.py`.**
  - Remove commented-out code (lines 25 and 29).
  - Fix the typo `cateory` in the comment at line 16.
  - Remove the stray comment-style leftovers.
- [x] **Consistent model building.** `get_menu` builds `MenuItem` objects, but `get_item` returns the raw dict. Use `MenuItem.model_validate` in both.
- [x] **Availability filter.** `available` is in the data but unused. Add `?available_only=true` (default `false`) so kiosks can hide sold-out items such as Vada Pav.
- [x] **Consistent error responses.** Use a custom exception handler, or keep `HTTPException` and make every error share one format.

## 4. Operations

- [x] **HTTP caching.** The menu changes rarely. Send `Cache-Control: max-age=60` and an `ETag` to cut server load and speed up kiosks.
  - `/menu` and `/menu/{id}` send an `ETag` (SHA-256 of the body) and `Cache-Control: max-age=60`; a matching `If-None-Match` gets `304`. Errors are not cached.
- [x] **Pin dependencies.** `fastapi` and `uvicorn[standard]` are unpinned in `requirements.txt`. Generate a lock file (`pip freeze`, `uv`, or `pip-tools`) for reproducible builds.
  - `requirements.txt` pins every package (a full `pip freeze`) and is saved as UTF-8.
- [x] **CORS.** If the mobile app runs as a web view or PWA, add `CORSMiddleware` with an explicit origin list.
  - Origins come from the `CORS_ALLOWED_ORIGINS` env var (comma-separated). Empty by default, so no cross-origin access until set.
- [x] **Health check.** Add `GET /health` for uptime monitors and kiosk status checks.
- [x] **Logging.** Add basic request logging.
  - Each request logs method, path, status and duration (`barista_menu` logger).
- [x] **CI.** Add a GitHub Actions workflow that installs requirements and runs `pytest` on every push and PR.
  - `.github/workflows/ci.yml` installs `requirements-dev.txt`, runs `ruff check` and `ruff format --check`, then runs `pytest` with a 90% coverage gate. See [CI.md](CI.md).
  - [ ] Still to do in GitHub settings: add a branch protection rule on `main` that requires the `test` check to pass.
- [x] **Check `.gitignore`.** Confirm `venv/` is excluded before committing.
  - `venv/` and `.venv313/` are both ignored.

## 5. Documentation

- [ ] Expand `README.md` (currently one sentence) with:
  - Setup: `python -m venv venv`, install requirements, `uvicorn main:app --reload`.
  - Example requests for each endpoint.
  - The `/docs` URL for interactive API docs.
  - How to run the tests.

## 6. Longer term

- [x] **Move data out of code.** A JSON or YAML file lets the shop change the menu without a code change.
  - Menu now lives in `menu.json`; `data.py` loads and validates it with `MenuItem` at startup.
  - Prices are stored as strings (`"30.00"`) so they parse to `Decimal` without float rounding.
- [x] **Separate write path.** Keep the public API read-only; put any admin writes in a separate, authenticated service.
  - The API exposes only `GET` routes; `POST`/`PUT`/`PATCH`/`DELETE` on `/menu` return 405. No admin write service is built yet; it stays out of this codebase until needed.

## Suggested order

1. Fix the category name mismatch.
2. Add tests and the data integrity checks.
3. Clean up the models and `main.py`.
4. Pin dependencies, expand the README, and commit (none of the Python files are committed yet).
5. Add CI, Docker, and caching.
