# Barista Coffee Point Menu API

A read-only menu API for the Barista Coffee, London kiosk displays and mobile app. Clients fetch the latest menu over HTTP without touching a database. The menu lives in `menu.json`, so the shop can change items and prices without a code change.

Built with [FastAPI](https://fastapi.tiangolo.com/) and [Pydantic](https://docs.pydantic.dev/).

## Features

- List the full menu, or filter by category (`coffee`, `snacks`, `combos`).
- Hide sold-out items with `available_only=true`.
- Fetch a single item by id.
- Interactive API docs generated from the code (Swagger UI and ReDoc).
- HTTP caching with `ETag` and `Cache-Control: max-age=60`, so kiosks can send `If-None-Match` and get `304 Not Modified`.
- Consistent JSON error responses.
- Optional CORS for web or PWA clients, configured by environment variable.
- Request logging with method, path, status and duration.
- Health check endpoint for uptime monitors.

Prices are `Decimal` values stored as strings in `menu.json` (for example `"30.00"`), so they never pass through floating point.

## Project structure

```
baristamenu/
├── main.py              # FastAPI app: routes, middleware, error handling
├── models.py            # Pydantic models (MenuItem, MenuResponse, Category)
├── data.py              # Loads and validates menu.json at startup
├── menu.json            # The menu (edit this to change items or prices)
├── requirements.txt     # Runtime dependencies (pinned)
├── requirements-dev.txt # Test and lint tools (pinned, includes requirements.txt)
├── pytest.ini           # Test discovery settings
├── tests/               # Test suite
├── docs/
│   ├── TESTING_GUIDELINES.md
│   ├── CI.md
│   └── TODO.md
└── .github/workflows/ci.yml
```

## Requirements

- Python 3.12 (the version used in CI)
- pip

## Setup

Run these commands from the project root.

**Windows (PowerShell)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To run the tests and linters as well, install the dev requirements instead:

```bash
pip install -r requirements-dev.txt
```

## Running the API

Start the development server with auto-reload:

```bash
uvicorn main:app --reload
```

The API is now available at <http://127.0.0.1:8000>.

For a production-style run without auto-reload, bind to all interfaces:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Interactive API docs

FastAPI generates these pages automatically from the code:

| URL | What it is |
| --- | --- |
| <http://127.0.0.1:8000/docs> | Swagger UI: browse and try every endpoint |
| <http://127.0.0.1:8000/redoc> | ReDoc: a read-only reference view |
| <http://127.0.0.1:8000/openapi.json> | The raw OpenAPI schema |

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Welcome message |
| GET | `/health` | Health check, returns `{"status": "ok"}` |
| GET | `/menu` | List menu items. Optional query params: `category`, `available_only` |
| GET | `/menu/{item_id}` | Get one menu item by id |

Write methods (`POST`, `PUT`, `PATCH`, `DELETE`) on `/menu` return `405 Method Not Allowed`. The API is read-only by design.

### Query parameters for `GET /menu`

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `category` | `coffee` \| `snacks` \| `combos` | none | Return only items in this category. Case-sensitive: `COFFEE` returns `422`. An unknown value returns `422`. |
| `available_only` | boolean | `false` | When `true`, hide sold-out items. |

## Example requests

Examples use `curl`. On Windows PowerShell, use `curl.exe` so it is not aliased to `Invoke-WebRequest`.

**Welcome message**

```bash
curl http://127.0.0.1:8000/
```

```json
{"message": "Welcome to Barista Coffee Point Menu API"}
```

**Health check**

```bash
curl http://127.0.0.1:8000/health
```

```json
{"status": "ok"}
```

**Full menu** (10 items)

```bash
curl http://127.0.0.1:8000/menu
```

```json
{
  "status": "success",
  "count": 10,
  "items": [
    {
      "id": 1,
      "name": "Masala coffee",
      "category": "coffee",
      "price": "30.00",
      "description": "Classic Indian spiced coffee with ginger and cardamom",
      "available": true
    }
  ]
}
```

The response above is shortened to one item. The real response includes all ten.

**Coffee only**

```bash
curl "http://127.0.0.1:8000/menu?category=coffee"
```

**Snacks that are in stock**

```bash
curl "http://127.0.0.1:8000/menu?category=snacks&available_only=true"
```

Vada Pav is sold out, so it is left out of this response.

**One item by id**

```bash
curl http://127.0.0.1:8000/menu/5
```

**Conditional request** (uses the `ETag` from the previous response)

```bash
curl -i -H 'If-None-Match: "<etag-value>"' http://127.0.0.1:8000/menu
```

A matching ETag returns `304 Not Modified` with an empty body.

### Error responses

All errors share one shape:

```json
{"status": "error", "message": "Menu item with id 999 not found"}
```

| Status | When |
| --- | --- |
| `404` | Unknown item id, or a category with no items |
| `422` | Invalid query parameter (for example `category=unknown`) |
| `405` | Write method used on a read-only route |

## Configuration

| Environment variable | Default | Description |
| --- | --- | --- |
| `CORS_ALLOWED_ORIGINS` | empty | Comma-separated list of origins allowed to call the API from a browser, for example `https://kiosk.example.com,https://app.example.com`. When empty, no cross-origin browser access is allowed. |

Example:

```bash
export CORS_ALLOWED_ORIGINS="https://kiosk.example.com"
uvicorn main:app --reload
```

On Windows PowerShell: `$env:CORS_ALLOWED_ORIGINS = "https://kiosk.example.com"`

## Changing the menu

Edit `menu.json`. Each item needs these fields:

| Field | Type | Rules |
| --- | --- | --- |
| `id` | integer | Unique across the file |
| `name` | string | |
| `category` | string | `coffee`, `snacks` or `combos` |
| `price` | string | Decimal, for example `"30.00"`. Must be positive. |
| `description` | string | |
| `available` | boolean | `false` hides the item from `available_only=true` |

The app validates `menu.json` at startup. A typo, such as a bad category, stops the server from starting. The data integrity tests also catch these before they reach a kiosk.

## Running the tests

```bash
pytest
```

To match the CI coverage gate:

```bash
pytest --cov=main --cov=models --cov=data --cov-report=term-missing --cov-fail-under=90
```

## Linting and formatting

```bash
ruff check .
ruff format --check .
```

To fix formatting automatically, run `ruff format .`.

## Continuous integration

GitHub Actions runs lint, format checks and the test suite with the coverage gate on every push and pull request. See [docs/CI.md](docs/CI.md).

## Further documentation

- [docs/TESTING_GUIDELINES.md](docs/TESTING_GUIDELINES.md): testing conventions, lint and format rules
- [docs/CI.md](docs/CI.md): the CI workflow, step by step
- [docs/TODO.md](docs/TODO.md): the enhancement backlog
