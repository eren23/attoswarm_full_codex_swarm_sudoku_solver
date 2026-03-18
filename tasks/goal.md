# Swarm Goal: Sudoku Solver with Web Frontend

## Overview

Build a Sudoku solving feature with backend solver logic, REST API, and a web frontend. All work must be tested and the final merge must produce a clean, working feature with a merge summary.

---

## Requirements

### 1. Backend Solver (Python)

- **Sudoku solver module** (`src/solver/sudoku.py` or equivalent):
  - Accept a 9×9 grid (0 or empty for blanks)
  - Return solved grid or indicate unsolvable
  - Use constraint propagation / backtracking (classic algorithms)
  - Pure functions, no side effects

- **Solver API** (FastAPI or Flask):
  - `POST /solve` — body: `{"grid": [[...], ...]}`, response: `{"solved": bool, "grid": [[...]], "message": str}`
  - `GET /health` — health check
  - Input validation (9×9, values 0–9)
  - Clear error responses for invalid input

### 2. Frontend (Web UI)

- Single-page web app (HTML/JS or React/Next.js):
  - Renders a 9×9 Sudoku grid
  - User can type numbers (1–9) or clear cells
  - "Solve" button → calls backend API → shows solution
  - "Clear" button → resets grid
  - Basic validation (no duplicate in row/col/box for user input)
  - Responsive layout

### 3. Tests

- Unit tests for solver logic (valid, invalid, empty, already solved)
- API tests (valid request, invalid grid, empty grid)
- Optional: E2E test that loads UI, enters a puzzle, clicks Solve, verifies result

### 4. Deliverables

- Working solver backend with API
- Working frontend that consumes the API
- Test suite that passes
- `requirements.txt` (Python) and dependency file for frontend if applicable
- Brief merge summary documenting what was built and how to run it

---

## Tech Stack (Suggested)

- **Backend**: Python 3.10+, FastAPI, Pydantic
- **Frontend**: Plain HTML/CSS/JS + fetch, or React + Vite
- **Tests**: pytest for backend; Playwright or similar for E2E if added

---

## Success Criteria

1. Given a valid Sudoku puzzle, the solver returns the correct solution.
2. The API accepts and rejects input according to spec.
3. The frontend displays a grid, allows input, and shows the solution from the API.
4. All automated tests pass.
5. A merge summary is produced at completion.
