# Testing Guidelines

This document defines how the Barista Coffee Point menu API is tested. It is the standard that every change must meet before it is merged. The CI pipeline is described in [CI.md](CI.md).

## 1. Purpose

Tests must prove that:

- every public endpoint returns the documented status codes, response shapes, and error format;
- the menu data in `menu.json` is valid and loads without error;
- caching (ETag / `Cache-Control`), CORS, and error handling behave as specified;
- regressions are caught automatically on every push and pull request.

## 2. Scope

| In scope | Out of scope |
|---|---|
| All routes in `main.py`: `/`, `/health`, `/menu`, `/menu/{item_id}` | Pydantic/FastAPI/Starlette internals |
| Models in `models.py` | Performance or load testing (not yet required) |
| Data loading in `data.py` and the content of `menu.json` | Browser or kiosk UI (separate project) |
| Middleware: logging, ETag caching, CORS | |
| Exception handlers: HTTP errors and validation errors | |

## 3. Tooling

| Tool | Purpose | Declared in |
|---|---|---|
| `pytest` | Test runner | `requirements-dev.txt` |
| `httpx` | HTTP client used by FastAPI's test client | `requirements-dev.txt` |
| `pytest-cov` | Coverage measurement | `requirements-dev.txt` (add when adopted) |
| `ruff` | Linting and formatting | `requirements-dev.txt` (add when adopted) |

Every test tool must be pinned to an exact version in `requirements-dev.txt`. Do not add test dependencies to `requirements.txt`.

## 4. Test layout

```
baristamenu/
├── main.py
├── models.py
├── data.py
├── menu.json
├── tests/
│   ├── conftest.py          # shared fixtures (client, sample menu)
│   ├── test_health.py       # /, /health
│   ├── test_menu_list.py    # GET /menu and its filters
│   ├── test_menu_item.py    # GET /menu/{item_id}
│   ├── test_errors.py       # error envelope for 404 and 422
│   ├── test_caching.py      # ETag, Cache-Control, 304 responses
│   ├── test_cors.py         # CORS_ALLOWED_ORIGINS behaviour
│   ├── test_models.py       # Pydantic model validation
│   ├── test_menu_data.py    # menu.json integrity
│   └── test_repo_files.py   # requirements files are UTF-8 without BOM
└── docs/
    └── TESTING_GUIDELINES.md
```

- All tests live in the `tests/` directory. The root-level `test_hello.py` must be moved into `tests/` (or deleted if it has no value).
- Test files are named `test_<area>.py`. Test functions are named `test_<behaviour>_<condition>`, for example `test_get_menu_returns_404_for_unknown_category`.

## 5. Test layers

### 5.1 Unit tests
- Cover pure logic: model validation, data integrity, and helper functions.
- Must not start the app, call the network, or touch the file system beyond reading `menu.json`.
- Run in milliseconds.

### 5.2 API tests
- Use FastAPI's `TestClient` (provided through `httpx`) to call the real app in-process.
- Assert on the status code, headers, and JSON body for every test.
- Each endpoint has its own test module (see section 4).

### 5.3 Contract checks
- The OpenAPI schema (`/openapi.json`) must be generated without error. A test must load it and confirm that the four documented paths exist.

## 6. Required coverage per endpoint

### `GET /`
- Returns `200` and `{"message": "Welcome to Barista Coffee Point Menu API"}`.

### `GET /health`
- Returns `200` and `{"status": "ok"}`.

### `GET /menu`
- With no parameters: `200`, `status` is `"success"`, `count` equals the length of `items`, and `count` equals the number of items in `menu.json`.
- `category=coffee`, `category=snacks`, `category=combos`: only items of that category are returned.
- `category` with a valid value but no matching items: `404` with the error envelope (see section 7). Use a monkeypatched menu to test this, because the real data has items in every category.
- `category=invalid`: `422` with the error envelope.
- `available_only=true`: no returned item has `available: false`.
- `available_only=false` (default): unavailable items are included.
- `category` and `available_only` combined: both filters apply.
- `available_only=notabool`: `422`.

### `GET /menu/{item_id}`
- Existing id: `200` and the item matches the record in `menu.json`.
- Unknown id: `404` with message `"Menu item with id <id> not found"`.
- Non-integer id (for example `abc`): `422`.
- Negative or zero id: `404` (no record exists).

## 7. Error response contract

Every error must use this shape:

```json
{"status": "error", "message": "<text>"}
```

- `422` responses must also include an `errors` list.
- Tests must check both the status code and the `status` and `message` fields.
- Internal stack traces, file paths, or Python exception names must never appear in a response body.

## 8. Caching contract

Responses from `GET /menu*` with status `200` must include:

- `ETag` as a quoted SHA-256 hex digest of the body;
- `Cache-Control: max-age=60`.

Tests must confirm:

- the same request returns the same `ETag`;
- a request with `If-None-Match` equal to the current `ETag` returns `304` with an empty body and the same `ETag` and `Cache-Control` headers;
- a request with a stale `If-None-Match` returns `200` with the full body;
- non-`/menu` routes (for example `/health`) do not receive an `ETag` header;
- error responses (`404`, `422`) do not receive an `ETag` header.

## 9. CORS contract

- `CORS_ALLOWED_ORIGINS` is read when `main.py` is imported. Tests that change it must reload the module (or the test must set the variable before import) so the change takes effect.
- With the variable unset: no `Access-Control-Allow-Origin` header is returned for any origin.
- With `CORS_ALLOWED_ORIGINS=https://kiosk.example.com`: that origin receives the header; another origin does not.
- Only `GET` is allowed. A preflight request for `POST` must not be approved.

## 10. Data integrity (`menu.json`)

A test in `test_menu_data.py` must confirm that:

- the file parses and every entry validates as `MenuItem`;
- `id` values are unique;
- `category` is one of `coffee`, `snacks`, `combos`;
- `price` is greater than or equal to zero;
- `name` is not empty.

If any rule fails, the test must name the offending record.

## 11. Pydantic model rules

- `MenuItem` rejects a missing field, a wrong type, and an unknown `category`.
- `price` is `Decimal`. Tests must assert the JSON representation the API returns, and it must stay the same across releases. Pydantic v2 serialises `Decimal` as a JSON string by default.
- `MenuResponse.status` defaults to `"success"`.

## 12. Test isolation rules

- **No real network calls.** Tests must not reach external services.
- **No shared mutable state.** Tests must not modify `main.menu_items` or the `menu.json` file. To test different data, replace the list with `monkeypatch.setattr(main, "menu_items", [...])`. The monkeypatch fixture restores the original value after each test.
- **Environment variables** must be set with `monkeypatch.setenv` and removed after the test.
- **Any order.** Each test must pass when run alone and when run in any order.
- **No sleeps or wall-clock assumptions.**

## 13. Fixtures (`tests/conftest.py`)

- `client`: a `TestClient` for the app. Scope: `function`.
- `sample_menu`: a small, known list of `MenuItem` objects covering all three categories and both `available` values. Use it when a test needs data that does not depend on `menu.json`.
- Fixtures must not hide the expected values. A test that asserts a count must show the expected number in the test body.

## 14. Coverage and quality gates

| Gate | Requirement | Enforced by |
|---|---|---|
| Test pass | 100% of tests pass | CI (`pytest`) |
| Line coverage | At least 90% for `main.py`, `models.py`, and `data.py` | `pytest --cov --cov-fail-under=90` |
| Lint | `ruff check .` reports no errors | CI (to be added) |
| Format | `ruff format --check .` passes | CI (to be added) |

- Coverage is a floor, not a goal. Tests must assert real outcomes, not just execute lines.
- A bug fix must come with a test that fails before the fix and passes after it.

## 15. Running the tests

From the project root, with the virtual environment active:

```bash
pip install -r requirements-dev.txt
pytest                                   # run all tests
pytest tests/test_menu_list.py -v        # run one module
pytest --cov=. --cov-report=term-missing # with coverage
ruff check . && ruff format --check .    # lint and format
```

## 16. CI requirements

- The workflow in `.github/workflows/ci.yml` runs on every `push` and `pull_request`.
- The pipeline must run Python 3.12 (see [CI.md](CI.md)).
- A failing test, a coverage drop below the threshold, or a lint error must fail the build.
- Merges to `main` require a passing build.

## 17. Definition of done

A change is ready for review only when:

1. every new or changed endpoint has tests covering the cases in section 6;
2. the error and caching contracts (sections 7 and 8) still hold;
3. `pytest` passes locally and in CI;
4. coverage meets the gate in section 14;
5. no test depends on the order it runs in or on the network.

## 18. Known gaps to close

These items do not meet this guideline yet:

- `test_hello.py` sits at the project root instead of in `tests/`.
- `CORS_ALLOWED_ORIGINS` is read at import time, which makes it hard to test. Consider reading it inside a function or app factory.
- Menu data is loaded into a module-level global, so tests must use `monkeypatch`. A FastAPI dependency (for example `get_menu_items`) would make the data easier to override.
- Coverage tooling and linting are not yet in `requirements-dev.txt` or CI.
- The CI pipeline runs `pytest` only; it does not run lint or coverage checks.
