# CI Workflow Overview

This project uses GitHub Actions to automatically validate the codebase whenever changes are pushed or a pull request is created.

## Workflow file

The workflow is defined in `.github/workflows/ci.yml`.

## Why this workflow exists

The purpose of CI (Continuous Integration) is to make sure the project still works in a clean environment before code is merged. It helps catch broken code, missing dependencies, failing tests, and configuration issues early.

## Trigger conditions

The workflow runs on:

- `push`: whenever code is pushed to the repository
- `pull_request`: whenever a pull request is opened, updated, or synchronized

This ensures that all new changes are checked automatically.

## Job structure

The workflow contains a single job named `test`:

- `runs-on: ubuntu-latest`

This means the code is executed on a fresh GitHub-hosted Ubuntu Linux machine, which gives a standard and reproducible test environment.

## Steps in the workflow

### 1. Checkout repository

```yaml
- uses: actions/checkout@v4
```

This step downloads the repository contents into the runner so the workflow can access the source code.

### 2. Set up Python

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: pip
```

This installs Python 3.12 on the runner and configures pip caching.

Why it matters:

- ensures the app is tested with the expected Python version
- reduces dependency installation time by caching downloaded packages

### 3. Install project dependencies

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements-dev.txt
```

This does two things:

1. upgrades `pip` to the latest available version
2. installs the project packages from `requirements.txt` and the test tools from `requirements-dev.txt` (`pytest`, `httpx`, `pytest-cov`, `ruff`), which includes `requirements.txt` itself

All tools are pinned to exact versions in `requirements-dev.txt`, so every run uses the same tool versions.

This is essential because the project cannot run its tests or lint checks unless its dependencies are available.

### 4. Lint and format check

```yaml
- name: Lint
  run: ruff check .

- name: Format check
  run: ruff format --check .
```

This enforces the lint and format rules in [TESTING_GUIDELINES.md](TESTING_GUIDELINES.md) (section 14). The workflow fails if `ruff` reports any error or if any file is not formatted.

### 5. Run the test suite with coverage gate

```yaml
- name: Run tests with coverage
  run: pytest --cov=main --cov=models --cov=data --cov-report=term-missing --cov-fail-under=90
```

This runs the test suite in the `tests/` folder and measures line coverage of `main.py`, `models.py`, and `data.py` only. Coverage of the test files and of virtual environments is excluded.

The workflow fails if:

- any test fails, or
- total line coverage is below 90%.

The `--cov-report=term-missing` option lists the uncovered line numbers in the job log, so the gap can be fixed without guessing.

If any step fails, the workflow fails and GitHub Actions reports the job as unsuccessful.

## Merge gate

A passing CI run is required before a change can reach `main`. This is enforced by a branch protection rule on `main` in GitHub repository settings, not by the workflow file:

- require a pull request before merging;
- require the `test` status check to pass before merging;
- require the branch to be up to date with `main` before merging.

Repository administrators must confirm that this rule is set. The workflow cannot enforce it on its own.

## End-to-end behavior

When the workflow runs, it follows this sequence:

1. fetch the repository code
2. install Python 3.12
3. install dependencies from `requirements-dev.txt` (which includes `requirements.txt`)
4. run `ruff check .` and `ruff format --check .`
5. run `pytest` with the coverage gate (90% minimum)
6. mark the workflow as passed or failed

## Why this is useful

This workflow provides:

- automatic validation on every change
- a consistent environment for testing
- early bug detection before merge
- protection against broken or untested code

## Notes for this project

This CI setup assumes:

- Python 3.12 is the intended runtime
- a `requirements.txt` file exists with the project dependencies
- a `requirements-dev.txt` file exists with the test and lint tools (`pytest`, `httpx`, `pytest-cov` with its `coverage` dependency, and `ruff`), all pinned to exact versions
- tests live in the `tests/` folder and are runnable with `pytest`
- the coverage gate and lint checks follow [TESTING_GUIDELINES.md](TESTING_GUIDELINES.md)

If any of those assumptions change, the workflow and this document should be updated together.

## Current test suite

The workflow runs the 62 tests in `tests/` (see [TESTING_GUIDELINES.md](TESTING_GUIDELINES.md)). `pytest.ini` sets `testpaths = tests` and `pythonpath = .`, so a plain `pytest` from the repository root finds the tests and the application modules. At the time of writing, line coverage of `main.py`, `models.py` and `data.py` is 100%, against a 90% gate.

The same commands can be run locally:

```bash
pip install -r requirements-dev.txt
ruff check . && ruff format --check .
pytest --cov=main --cov=models --cov=data --cov-report=term-missing --cov-fail-under=90
```

## Remaining manual step

- [ ] Confirm the branch protection rule on `main` in GitHub settings (see "Merge gate"). The workflow file cannot set this.

## Summary

This CI workflow is a standard Python project setup that ensures code quality by automatically checking out the repository, installing Python and dependencies, linting and format-checking the code, and running the test suite with a coverage gate. Together with the branch protection rule on `main`, it is a safeguard against regressions and broken builds.
