# Merge Summary

This branch delivers a complete Sudoku solving feature as one FastAPI application that serves both the backend API and the browser UI.

## Built

- Added a pure 9x9 Sudoku solver with conflict detection, candidate propagation, and backtracking search
- Added `GET /health` and `POST /solve` endpoints with strict Pydantic validation
- Returned clear API outcomes for solved puzzles, unsolvable puzzles, malformed payloads, and conflicting starting clues
- Added a responsive single-page frontend with a 9x9 grid, duplicate highlighting, solve and clear actions, keyboard navigation, paste sanitization, and solved-cell styling
- Added automated coverage for solver logic, API behavior, and a Playwright smoke test of the real web flow

## Runbook

- Install Python dependencies with `python -m pip install -r requirements.txt` inside a Python 3.10+ virtualenv
- Start the app with `uvicorn src.api.main:app --reload`
- Open `http://127.0.0.1:8000/` for the frontend
- Run tests with `python -m pytest -q`
- Install Playwright Chromium with `python -m playwright install chromium` before running `tests/e2e/test_web_ui.py`

## Handoff Notes

- The frontend is served by FastAPI from `frontend/`; there is no separate Node-based frontend process
- In this sandbox, dependency installation and test execution could not be fully verified because outbound package downloads were blocked and the available `python3` binary was version 3.9.6 while the code requires Python 3.10+
