"""Pure Sudoku solving helpers for 9x9 grids."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Sequence


GRID_SIZE = 9
BOX_SIZE = 3
DIGITS = frozenset(range(1, GRID_SIZE + 1))

Grid = list[list[int]]
GridLike = Sequence[Sequence[int]]


@dataclass(frozen=True)
class SolveResult:
    """Outcome of a Sudoku solve attempt."""

    solved: bool
    grid: Grid
    message: str


def solve(grid: GridLike) -> SolveResult:
    """Solve a Sudoku puzzle without mutating the caller's grid."""
    normalized = _normalize_grid(grid)

    if _has_conflicts(normalized):
        raise ValueError("Initial clues conflict in row, column, or box.")

    if _is_complete(normalized):
        return SolveResult(
            solved=True,
            grid=_copy_grid(normalized),
            message="Solved successfully.",
        )

    solved_grid = _search(normalized)
    if solved_grid is None:
        return SolveResult(
            solved=False,
            grid=_copy_grid(normalized),
            message="Puzzle is unsolvable.",
        )

    return SolveResult(
        solved=True,
        grid=solved_grid,
        message="Solved successfully.",
    )


def is_solved(grid: GridLike) -> bool:
    """Return True when the grid is fully filled and respects Sudoku rules."""
    normalized = _normalize_grid(grid)
    return _is_complete(normalized) and not _has_conflicts(normalized)


def has_conflicts(grid: GridLike) -> bool:
    """Return True when any row, column, or 3x3 box contains duplicates."""
    normalized = _normalize_grid(grid)
    return _has_conflicts(normalized)


def _has_conflicts(grid: Grid) -> bool:
    """Internal conflict check for an already normalized grid."""

    for row in grid:
        if _unit_has_duplicates(row):
            return True

    for column_index in range(GRID_SIZE):
        if _unit_has_duplicates(
            grid[row_index][column_index] for row_index in range(GRID_SIZE)
        ):
            return True

    for box_row in range(0, GRID_SIZE, BOX_SIZE):
        for box_col in range(0, GRID_SIZE, BOX_SIZE):
            if _unit_has_duplicates(_iter_box(grid, box_row, box_col)):
                return True

    return False


def get_candidates(grid: GridLike, row: int, col: int) -> set[int]:
    """Return the valid candidates for an empty cell."""
    normalized = _normalize_grid(grid)
    _validate_indices(row, col)
    return _get_candidates(normalized, row, col)


def _get_candidates(grid: Grid, row: int, col: int) -> set[int]:
    if grid[row][col] != 0:
        return set()

    used_values = set(grid[row])
    used_values.update(grid[row_index][col] for row_index in range(GRID_SIZE))
    used_values.update(_iter_box(grid, row - row % BOX_SIZE, col - col % BOX_SIZE))

    return DIGITS.difference(used_values)


def _search(grid: Grid) -> Grid | None:
    propagated = _propagate_singles(grid)
    if propagated is None:
        return None

    if _is_complete(propagated):
        return propagated

    next_cell = _select_unfilled_cell(propagated)
    if next_cell is None:
        return propagated

    row, col, candidates = next_cell
    for value in sorted(candidates):
        branch = _copy_grid(propagated)
        branch[row][col] = value
        solved = _search(branch)
        if solved is not None:
            return solved

    return None


def _propagate_singles(grid: Grid) -> Grid | None:
    working_grid = _copy_grid(grid)

    while True:
        forced_moves: list[tuple[int, int, int]] = []

        for row_index in range(GRID_SIZE):
            for col_index in range(GRID_SIZE):
                if working_grid[row_index][col_index] != 0:
                    continue

                candidates = _get_candidates(working_grid, row_index, col_index)
                if not candidates:
                    return None

                if len(candidates) == 1:
                    forced_moves.append(
                        (row_index, col_index, next(iter(candidates)))
                    )

        if not forced_moves:
            return working_grid

        for row_index, col_index, value in forced_moves:
            working_grid[row_index][col_index] = value


def _select_unfilled_cell(grid: Grid) -> tuple[int, int, set[int]] | None:
    best_choice: tuple[int, int, set[int]] | None = None

    for row_index in range(GRID_SIZE):
        for col_index in range(GRID_SIZE):
            if grid[row_index][col_index] != 0:
                continue

            candidates = _get_candidates(grid, row_index, col_index)
            if not candidates:
                return row_index, col_index, set()

            if best_choice is None or len(candidates) < len(best_choice[2]):
                best_choice = (row_index, col_index, candidates)

    return best_choice


def _normalize_grid(grid: GridLike) -> Grid:
    if len(grid) != GRID_SIZE:
        raise ValueError("Sudoku grid must contain exactly 9 rows.")

    normalized: Grid = []
    for row in grid:
        if len(row) != GRID_SIZE:
            raise ValueError("Sudoku grid rows must contain exactly 9 values.")

        normalized_row: list[int] = []
        for value in row:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("Sudoku cells must be integers from 0 to 9.")
            if value < 0 or value > GRID_SIZE:
                raise ValueError("Sudoku cells must be integers from 0 to 9.")
            normalized_row.append(value)

        normalized.append(normalized_row)

    return normalized


def _copy_grid(grid: GridLike) -> Grid:
    return [list(row) for row in grid]


def _is_complete(grid: GridLike) -> bool:
    return all(value != 0 for row in grid for value in row)


def _unit_has_duplicates(values: Iterable[int]) -> bool:
    seen: set[int] = set()

    for value in values:
        if value == 0:
            continue
        if value in seen:
            return True
        seen.add(value)

    return False


def _iter_box(grid: GridLike, start_row: int, start_col: int):
    for row_index in range(start_row, start_row + BOX_SIZE):
        for col_index in range(start_col, start_col + BOX_SIZE):
            yield grid[row_index][col_index]


def _validate_indices(row: int, col: int) -> None:
    if not 0 <= row < GRID_SIZE or not 0 <= col < GRID_SIZE:
        raise IndexError("Sudoku cell indices must be between 0 and 8.")


__all__ = [
    "BOX_SIZE",
    "DIGITS",
    "GRID_SIZE",
    "Grid",
    "GridLike",
    "SolveResult",
    "get_candidates",
    "has_conflicts",
    "is_solved",
    "solve",
]
