from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import create_app


client = TestClient(create_app(testing=True))

VALID_PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

VALID_PUZZLE_SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

EMPTY_GRID = [[0] * 9 for _ in range(9)]

EMPTY_GRID_SOLUTION = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9],
    [4, 5, 6, 7, 8, 9, 1, 2, 3],
    [7, 8, 9, 1, 2, 3, 4, 5, 6],
    [2, 3, 1, 6, 7, 4, 8, 9, 5],
    [8, 7, 5, 9, 1, 2, 3, 6, 4],
    [6, 9, 4, 5, 3, 8, 2, 1, 7],
    [3, 1, 7, 2, 6, 5, 9, 4, 8],
    [5, 4, 2, 8, 9, 7, 6, 3, 1],
    [9, 6, 8, 3, 4, 1, 5, 7, 2],
]

MALFORMED_GRID = [[0] * 9 for _ in range(8)]

OUT_OF_RANGE_GRID = [[10] + [0] * 8] + [[0] * 9 for _ in range(8)]


def test_get_health_returns_ok_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_solve_returns_solution_for_valid_puzzle():
    response = client.post("/solve", json={"grid": VALID_PUZZLE})

    assert response.status_code == 200
    assert response.json() == {
        "solved": True,
        "grid": VALID_PUZZLE_SOLUTION,
        "message": "Solved successfully.",
    }


def test_post_solve_returns_solution_for_empty_grid():
    response = client.post("/solve", json={"grid": EMPTY_GRID})

    assert response.status_code == 200
    assert response.json() == {
        "solved": True,
        "grid": EMPTY_GRID_SOLUTION,
        "message": "Solved successfully.",
    }


def test_post_solve_rejects_malformed_grid_dimensions():
    response = client.post("/solve", json={"grid": MALFORMED_GRID})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "value_error",
                "loc": ["body", "grid"],
                "msg": "Value error, grid must contain exactly 9 rows; received 8.",
                "input": MALFORMED_GRID,
                "ctx": {"error": {}},
                "url": "https://errors.pydantic.dev/2.12/v/value_error",
            }
        ]
    }


def test_post_solve_rejects_out_of_range_cell_values():
    response = client.post("/solve", json={"grid": OUT_OF_RANGE_GRID})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "value_error",
                "loc": ["body", "grid"],
                "msg": "Value error, grid cell (1, 1) must be between 0 and 9; received 10.",
                "input": OUT_OF_RANGE_GRID,
                "ctx": {"error": {}},
                "url": "https://errors.pydantic.dev/2.12/v/value_error",
            }
        ]
    }
