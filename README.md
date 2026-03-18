# Sudoku Solver

Single-service Sudoku solver built with FastAPI and a static HTML/CSS/JavaScript frontend. The FastAPI app serves both the API and the web UI, so there is no separate Node or frontend build step.

## Requirements

- Python 3.10+ required
- Python 3.11+ recommended

The checked-in source uses Python 3.10 type syntax such as `bool | None`, so `python3.9` is too old for this project.

## Install Dependencies

Create and activate a virtual environment with a Python 3.10+ interpreter:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install the Playwright browser once if you want to run the browser-based end-to-end test:

```bash
python -m playwright install chromium
```

If your machine does not have `python3.11`, replace it with any Python 3.10+ executable available on your system.

## Run The API And Frontend

Start the FastAPI app:

```bash
uvicorn src.api.main:app --reload
```

Then open:

- Frontend: `http://127.0.0.1:8000/`
- Health check: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`

Important: the frontend is served by the same FastAPI process and calls `POST /solve` on the same origin. There is no separate frontend dev server in this repo.

Example API request:

```bash
curl -X POST http://127.0.0.1:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "grid": [
      [5,3,0,0,7,0,0,0,0],
      [6,0,0,1,9,5,0,0,0],
      [0,9,8,0,0,0,0,6,0],
      [8,0,0,0,6,0,0,0,3],
      [4,0,0,8,0,3,0,0,1],
      [7,0,0,0,2,0,0,0,6],
      [0,6,0,0,0,0,2,8,0],
      [0,0,0,4,1,9,0,0,5],
      [0,0,0,0,8,0,0,7,9]
    ]
  }'
```

## Run Tests

Run the full test suite:

```bash
python -m pytest -q
```

Run targeted suites:

```bash
python -m pytest tests/test_sudoku_solver.py -q
python -m pytest tests/test_api.py tests/test_api_solve.py -q
python -m pytest tests/e2e/test_web_ui.py -q
```

Notes:

- The end-to-end test starts a live Uvicorn server and drives Chromium with Playwright.
- The end-to-end test may skip if Chromium is not installed or the environment does not allow binding a local port.

## What Was Built

- A pure Sudoku solver in `src/solver/sudoku.py` using validation, single-candidate propagation, and backtracking
- A FastAPI service in `src/api/main.py` with `GET /health` and `POST /solve`
- Strict request/response validation in `src/api/schemas.py`
- A single-page web UI in `frontend/` with a 9x9 grid, client-side duplicate detection, solve/clear controls, keyboard navigation, and solved-cell highlighting
- Automated tests covering solver behavior, API behavior, and one browser smoke test
