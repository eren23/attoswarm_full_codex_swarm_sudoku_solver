# Sudoku Feature Plan

## Stack Decision

Use a single Python service:

- Backend: Python 3.11+, FastAPI, Pydantic v2
- Frontend: static `HTML/CSS/JavaScript` served by FastAPI
- Tests: `pytest` for solver and API; one browser smoke test can be added after core behavior is stable

This keeps the feature in one deployable app, avoids a separate Node build step, and is sufficient for a 9x9 interactive Sudoku UI.

## Directory Layout

```text
docs/
  sudoku-feature-plan.md
src/
  app.py                  # FastAPI app and route registration
  api/
    schemas.py            # Request/response models
    routes.py             # /health and /solve endpoints
  solver/
    sudoku.py             # Pure solve() implementation
    validation.py         # Grid shape and Sudoku-rule validation
  web/
    index.html            # Single-page UI
    app.js                # Grid rendering, input handling, API calls
    styles.css            # Responsive layout and cell styling
tests/
  unit/
    test_sudoku_solver.py
    test_validation.py
  api/
    test_health.py
    test_solve.py
  e2e/
    test_sudoku_ui.py     # Deferred until backend + UI are stable
requirements.txt
```

## API Contract

### `GET /health`

- `200 OK`
- Response:

```json
{"status":"ok"}
```

### `POST /solve`

- Request body:

```json
{
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
}
```

- Success response: `200 OK`

```json
{
  "solved": true,
  "grid": [[...9 rows...]],
  "message": "Solved successfully."
}
```

- Valid but unsolvable puzzle: `200 OK`

```json
{
  "solved": false,
  "grid": [[...original grid...]],
  "message": "Puzzle is unsolvable."
}
```

- Invalid payload shape or cell values: `422 Unprocessable Entity` from Pydantic
- Structurally valid grid that already breaks Sudoku rules: `400 Bad Request`

```json
{
  "detail": {
    "code": "INVALID_PUZZLE",
    "message": "Initial clues conflict in row, column, or box."
  }
}
```

## Validation Rules

Backend is the source of truth. Frontend mirrors only the rules needed for immediate user feedback.

- Grid must contain exactly 9 rows.
- Each row must contain exactly 9 cells.
- Each cell must be an integer from `0` to `9`.
- `0` means empty; `1` through `9` are fixed values.
- Initial non-zero values must not duplicate within any row, column, or 3x3 box.
- Frontend inputs allow only empty or digits `1` through `9`; invalid keystrokes are rejected locally.
- Frontend highlights duplicate conflicts before submit, but the API still re-validates every request.

## Test Strategy

Required automated coverage:

- Solver unit tests for solved, solvable, unsolvable, invalid, and already-complete grids
- Validation unit tests for wrong dimensions, out-of-range values, non-integer values, and duplicate clues
- API tests for `/health`, successful solve, unsolvable puzzle, malformed payload, and conflicting starting clues

Execution order:

1. Land solver + validation tests first.
2. Add API tests once schemas and routes exist.
3. Add one end-to-end browser smoke test after the UI is wired to the real API.

## Implementation Notes

- Keep solver functions pure and return new grids instead of mutating request models in place.
- Serve the frontend from the same FastAPI app so local development and deployment use one origin.
- Do not add alternative API shapes or a second frontend stack unless this document is explicitly revised.
