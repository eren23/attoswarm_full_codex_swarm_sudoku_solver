import pytest

from src.solver.sudoku import is_solved, solve


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

SOLVED_PUZZLE = [
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

UNSOLVABLE_PUZZLE = [
    [5, 3, 1, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def test_solve_returns_expected_solution_for_valid_puzzle():
    puzzle = [row[:] for row in VALID_PUZZLE]

    result = solve(puzzle)

    assert result.solved is True
    assert result.grid == SOLVED_PUZZLE
    assert result.message == "Solved successfully."
    assert puzzle == VALID_PUZZLE


def test_solve_keeps_already_solved_puzzle_solved():
    puzzle = [row[:] for row in SOLVED_PUZZLE]

    result = solve(puzzle)

    assert result.solved is True
    assert result.grid == SOLVED_PUZZLE
    assert result.grid is not puzzle
    assert result.message == "Solved successfully."


def test_solve_finds_a_valid_solution_for_an_empty_grid():
    empty_grid = [[0] * 9 for _ in range(9)]

    result = solve(empty_grid)

    assert result.solved is True
    assert is_solved(result.grid) is True
    assert result.message == "Solved successfully."


def test_solve_reports_unsolvable_puzzle_without_conflicts():
    puzzle = [row[:] for row in UNSOLVABLE_PUZZLE]

    result = solve(puzzle)

    assert result.solved is False
    assert result.grid == UNSOLVABLE_PUZZLE
    assert result.message == "Puzzle is unsolvable."


def test_solve_rejects_invalid_puzzle_shape():
    invalid_grid = [[0] * 9 for _ in range(8)]

    with pytest.raises(ValueError, match="exactly 9 rows"):
        solve(invalid_grid)
