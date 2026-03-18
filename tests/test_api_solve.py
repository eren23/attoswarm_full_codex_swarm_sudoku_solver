from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)

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

UNSOLVABLE_PUZZLE = [
    [5, 1, 6, 8, 4, 9, 7, 3, 2],
    [3, 0, 7, 6, 0, 5, 0, 0, 0],
    [8, 0, 9, 7, 0, 0, 0, 6, 5],
    [1, 3, 5, 0, 6, 0, 9, 0, 7],
    [4, 7, 2, 5, 9, 1, 0, 0, 6],
    [9, 6, 8, 3, 7, 0, 0, 5, 0],
    [2, 5, 3, 1, 8, 6, 0, 7, 4],
    [6, 8, 4, 2, 0, 7, 5, 0, 0],
    [7, 9, 1, 0, 5, 0, 6, 0, 8],
]

CONFLICTING_PUZZLE = [
    [5, 5, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def test_post_solve_returns_solution_for_valid_puzzle():
    response = client.post("/solve", json={"grid": VALID_PUZZLE})

    assert response.status_code == 200

    body = response.json()
    assert body["solved"] is True
    assert body["message"] == "Solved successfully."
    assert body["grid"] != VALID_PUZZLE


def test_post_solve_returns_unsolved_response_for_unsolvable_puzzle():
    response = client.post("/solve", json={"grid": UNSOLVABLE_PUZZLE})

    assert response.status_code == 200
    assert response.json() == {
        "solved": False,
        "grid": UNSOLVABLE_PUZZLE,
        "message": "Puzzle is unsolvable.",
    }


def test_post_solve_rejects_conflicting_starting_clues():
    response = client.post("/solve", json={"grid": CONFLICTING_PUZZLE})

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "INVALID_PUZZLE",
            "message": "Initial clues conflict in row, column, or box.",
        }
    }


def test_post_solve_rejects_invalid_payload_shape():
    response = client.post("/solve", json={"grid": [[0] * 9 for _ in range(8)]})

    assert response.status_code == 422
