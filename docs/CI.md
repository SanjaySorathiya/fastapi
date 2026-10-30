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
2. installs the project packages from `requirements.txt` and the test tools from `requirements-dev.txt` (`pytest`, `httpx`), which includes `requirements.txt` itself

This is essential because the project cannot run its tests unless its dependencies are available.

### 4. Run the test suite

```yaml
- name: Run tests
  run: pytest
```

This executes the project’s test suite using `pytest`.

If any test fails, the workflow fails and GitHub Actions reports the job as unsuccessful.

## End-to-end behavior

When the workflow runs, it follows this sequence:

1. fetch the repository code
2. install Python 3.12
3. install dependencies from `requirements-dev.txt` (which includes `requirements.txt`)
4. run `pytest`
5. mark the workflow as passed or failed

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
- a `requirements-dev.txt` file exists with the test tools (`pytest`, `httpx`)
- tests are available and runnable with `pytest`

If any of those assumptions change, the workflow should be updated accordingly.

## Summary

This CI workflow is a standard Python project setup that ensures code quality by automatically checking out the repository, installing Python and dependencies, and running the test suite. It is a simple but effective safeguard against regressions and broken builds.
