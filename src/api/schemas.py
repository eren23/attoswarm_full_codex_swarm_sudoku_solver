"""Pydantic models for the Sudoku solve API."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _validate_sudoku_grid(value: Any) -> list[list[int]]:
    """Validate a strict 9x9 Sudoku grid with cell values from 0 to 9."""
    if not isinstance(value, list):
        raise ValueError("grid must be a list of 9 rows.")

    row_count = len(value)
    if row_count != 9:
        raise ValueError(f"grid must contain exactly 9 rows; received {row_count}.")

    validated_grid: list[list[int]] = []
    for row_index, row in enumerate(value, start=1):
        if not isinstance(row, list):
            raise ValueError(f"grid row {row_index} must be a list of 9 integers.")

        cell_count = len(row)
        if cell_count != 9:
            raise ValueError(
                f"grid row {row_index} must contain exactly 9 cells; received {cell_count}."
            )

        validated_row: list[int] = []
        for column_index, cell in enumerate(row, start=1):
            if isinstance(cell, bool) or not isinstance(cell, int):
                raise ValueError(
                    f"grid cell ({row_index}, {column_index}) must be an integer from 0 to 9."
                )

            if not 0 <= cell <= 9:
                raise ValueError(
                    f"grid cell ({row_index}, {column_index}) must be between 0 and 9; "
                    f"received {cell}."
                )

            validated_row.append(cell)

        validated_grid.append(validated_row)

    return validated_grid


SudokuGrid = Annotated[
    list[list[int]],
    BeforeValidator(_validate_sudoku_grid),
    Field(
        description="A 9x9 Sudoku grid. Use 0 for empty cells.",
        examples=[
            [
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
        ],
    ),
]


class SolveRequest(BaseModel):
    """Incoming payload for the solve endpoint."""

    model_config = ConfigDict(extra="forbid")

    grid: SudokuGrid


class SolveResponse(BaseModel):
    """Successful response payload for the solve endpoint."""

    model_config = ConfigDict(extra="forbid")

    solved: bool
    grid: SudokuGrid
    message: str = Field(min_length=1)
