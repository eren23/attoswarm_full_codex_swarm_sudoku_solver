"""Solve endpoint for Sudoku puzzles."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import SolveRequest, SolveResponse
from src.solver.sudoku import solve


router = APIRouter()


@router.post(
    "/solve",
    response_model=SolveResponse,
    status_code=status.HTTP_200_OK,
    tags=["solve"],
)
async def solve_sudoku(payload: SolveRequest) -> SolveResponse:
    """Solve a validated Sudoku grid and return the API response shape."""

    try:
        result = solve(payload.grid)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PUZZLE",
                "message": str(exc),
            },
        ) from exc

    return SolveResponse(
        solved=result.solved,
        grid=result.grid,
        message=result.message,
    )
