(() => {
  const BOARD_SIZE = 9;
  const DEFAULT_STATUS = "Enter a puzzle and choose Solve to request a solution.";
  const READY_STATUS = "No duplicate conflicts detected. Choose Solve to request a solution.";
  const CONFLICT_STATUS = "Duplicate digit detected in a row, column, or 3x3 box.";
  const SOLVING_STATUS = "Solving puzzle...";
  const NETWORK_ERROR_STATUS = "Unable to reach the solve service. Try again.";

  const form = document.querySelector("[data-sudoku-form]");
  const gridElement = document.querySelector("[data-sudoku-grid]");
  const statusElement = document.querySelector("[data-status-message]");
  const solveButton = document.querySelector('[data-action="solve"]');
  const clearButton = document.querySelector('[data-action="clear"]');
  const cells = Array.from(document.querySelectorAll("[data-cell]"));

  if (!form || !gridElement || !statusElement || !solveButton || !clearButton || cells.length === 0) {
    return;
  }

  const rows = Array.from({ length: BOARD_SIZE }, () => []);
  const columns = Array.from({ length: BOARD_SIZE }, () => []);
  const boxes = Array.from({ length: BOARD_SIZE }, () => []);
  const cellsByPosition = new Map();

  cells.forEach((cell) => {
    const row = Number(cell.dataset.row);
    const col = Number(cell.dataset.col);
    const box = Number(cell.dataset.box);

    rows[row].push(cell);
    columns[col].push(cell);
    boxes[box].push(cell);
    cellsByPosition.set(`${row}:${col}`, cell);
  });

  function setStatus(message, tone = "default") {
    statusElement.textContent = message;
    statusElement.classList.remove("is-error", "is-success", "is-solved");
    statusElement.removeAttribute("aria-invalid");

    if (tone === "error") {
      statusElement.classList.add("is-error");
      statusElement.setAttribute("aria-invalid", "true");
      return;
    }

    if (tone === "solved") {
      statusElement.classList.add("is-success", "is-solved");
      return;
    }

    if (tone === "success") {
      statusElement.classList.add("is-success");
    }
  }

  function sanitizeCellValue(value) {
    const match = String(value).match(/[1-9]/);
    return match ? match[0] : "";
  }

  function getCellCoordinates(cell) {
    return {
      row: Number(cell.dataset.row),
      col: Number(cell.dataset.col),
    };
  }

  function getCellAt(row, col) {
    return cellsByPosition.get(`${row}:${col}`) ?? null;
  }

  function setCellInvalid(cell, invalid) {
    cell.classList.toggle("is-error", invalid);
    cell.classList.toggle("is-invalid", invalid);

    if (invalid) {
      cell.setAttribute("aria-invalid", "true");
      return;
    }

    cell.removeAttribute("aria-invalid");
  }

  function clearSolutionState() {
    gridElement.classList.remove("is-solved");

    cells.forEach((cell) => {
      cell.classList.remove("is-given", "is-solved");
      cell.removeAttribute("data-state");
    });
  }

  function clearValidationState() {
    gridElement.classList.remove("is-error");

    cells.forEach((cell) => {
      setCellInvalid(cell, false);
    });
  }

  function resetBoardState() {
    clearSolutionState();
    clearValidationState();
    setStatus(DEFAULT_STATUS);
  }

  function readGrid() {
    const grid = Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(0));

    cells.forEach((cell) => {
      const { row, col } = getCellCoordinates(cell);
      grid[row][col] = cell.value === "" ? 0 : Number(cell.value);
    });

    return grid;
  }

  function boardHasValues() {
    return cells.some((cell) => cell.value !== "");
  }

  function collectDuplicateConflicts() {
    const conflictedCells = new Set();

    function collectFromUnit(unit) {
      const digits = new Map();

      unit.forEach((cell) => {
        if (cell.value === "") {
          return;
        }

        const matches = digits.get(cell.value) ?? [];
        matches.push(cell);
        digits.set(cell.value, matches);
      });

      digits.forEach((matchingCells) => {
        if (matchingCells.length < 2) {
          return;
        }

        matchingCells.forEach((cell) => conflictedCells.add(cell));
      });
    }

    rows.forEach(collectFromUnit);
    columns.forEach(collectFromUnit);
    boxes.forEach(collectFromUnit);

    return conflictedCells;
  }

  function refreshValidationState({ updateStatus = true } = {}) {
    clearValidationState();

    const conflictedCells = collectDuplicateConflicts();
    const hasConflicts = conflictedCells.size > 0;

    conflictedCells.forEach((cell) => {
      setCellInvalid(cell, true);
    });

    gridElement.classList.toggle("is-error", hasConflicts);

    if (!updateStatus) {
      return hasConflicts;
    }

    if (hasConflicts) {
      setStatus(CONFLICT_STATUS, "error");
      return hasConflicts;
    }

    if (boardHasValues()) {
      setStatus(READY_STATUS);
      return hasConflicts;
    }

    setStatus(DEFAULT_STATUS);
    return hasConflicts;
  }

  function renderGrid(grid, originalGrid = null) {
    clearSolutionState();
    clearValidationState();

    for (let row = 0; row < BOARD_SIZE; row += 1) {
      for (let col = 0; col < BOARD_SIZE; col += 1) {
        const cell = getCellAt(row, col);

        if (!cell) {
          continue;
        }

        const value = grid[row][col];
        cell.value = value === 0 ? "" : String(value);

        if (!originalGrid || value === 0) {
          continue;
        }

        if (originalGrid[row][col] !== 0) {
          cell.classList.add("is-given");
          continue;
        }

        cell.classList.add("is-solved");
        cell.dataset.state = "solved";
      }
    }
  }

  function extractErrorMessage(payload) {
    if (!payload || typeof payload !== "object") {
      return null;
    }

    if (typeof payload.message === "string" && payload.message.trim() !== "") {
      return payload.message;
    }

    if (
      payload.detail &&
      typeof payload.detail === "object" &&
      typeof payload.detail.message === "string" &&
      payload.detail.message.trim() !== ""
    ) {
      return payload.detail.message;
    }

    if (typeof payload.detail === "string" && payload.detail.trim() !== "") {
      return payload.detail;
    }

    if (Array.isArray(payload.detail) && payload.detail.length > 0) {
      return "Puzzle request is invalid.";
    }

    return null;
  }

  function setBusy(busy) {
    solveButton.disabled = busy;
    clearButton.disabled = busy;

    cells.forEach((cell) => {
      cell.disabled = busy;
    });
  }

  function moveFocus(rowOffset, colOffset, cell) {
    const { row, col } = getCellCoordinates(cell);
    const nextRow = row + rowOffset;
    const nextCol = col + colOffset;

    if (nextRow < 0 || nextRow >= BOARD_SIZE || nextCol < 0 || nextCol >= BOARD_SIZE) {
      return;
    }

    const nextCell = getCellAt(nextRow, nextCol);

    if (!nextCell) {
      return;
    }

    nextCell.focus();
    nextCell.select();
  }

  async function solvePuzzle() {
    clearSolutionState();

    const hasConflicts = refreshValidationState();
    if (hasConflicts) {
      return;
    }

    const grid = readGrid();

    setBusy(true);
    setStatus(SOLVING_STATUS);

    try {
      const response = await fetch("/solve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ grid }),
      });

      let payload = null;
      try {
        payload = await response.json();
      } catch (error) {
        payload = null;
      }

      if (!response.ok) {
        const errorMessage = extractErrorMessage(payload) ?? "Unable to solve the puzzle.";
        refreshValidationState({ updateStatus: false });
        setStatus(errorMessage, "error");
        return;
      }

      if (!payload || !Array.isArray(payload.grid) || typeof payload.message !== "string") {
        setStatus("Solve service returned an unexpected response.", "error");
        return;
      }

      renderGrid(payload.grid, grid);

      if (payload.solved) {
        gridElement.classList.add("is-solved");
        setStatus(payload.message, "solved");
        return;
      }

      setStatus(payload.message, "error");
    } catch (error) {
      setStatus(NETWORK_ERROR_STATUS, "error");
    } finally {
      setBusy(false);
    }
  }

  gridElement.addEventListener("keydown", (event) => {
    const cell = event.target.closest("[data-cell]");
    if (!cell || event.ctrlKey || event.metaKey || event.altKey) {
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      moveFocus(-1, 0, cell);
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveFocus(1, 0, cell);
      return;
    }

    if (event.key === "ArrowLeft") {
      event.preventDefault();
      moveFocus(0, -1, cell);
      return;
    }

    if (event.key === "ArrowRight") {
      event.preventDefault();
      moveFocus(0, 1, cell);
      return;
    }

    const isAllowedControlKey = [
      "Backspace",
      "Delete",
      "Tab",
      "Enter",
      "Escape",
      "Home",
      "End",
    ].includes(event.key);

    if (isAllowedControlKey || /^[1-9]$/.test(event.key)) {
      return;
    }

    if (event.key.length === 1) {
      event.preventDefault();
    }
  });

  gridElement.addEventListener("focusin", (event) => {
    const cell = event.target.closest("[data-cell]");
    if (cell) {
      cell.select();
    }
  });

  gridElement.addEventListener("input", (event) => {
    const cell = event.target.closest("[data-cell]");
    if (!cell) {
      return;
    }

    const sanitizedValue = sanitizeCellValue(cell.value);
    if (cell.value !== sanitizedValue) {
      cell.value = sanitizedValue;
    }

    clearSolutionState();
    refreshValidationState();
  });

  gridElement.addEventListener("paste", (event) => {
    const cell = event.target.closest("[data-cell]");
    if (!cell) {
      return;
    }

    event.preventDefault();

    const pastedText = event.clipboardData ? event.clipboardData.getData("text") : "";
    cell.value = sanitizeCellValue(pastedText);
    clearSolutionState();
    refreshValidationState();
  });

  solveButton.addEventListener("click", () => {
    void solvePuzzle();
  });

  form.addEventListener("reset", () => {
    window.requestAnimationFrame(() => {
      resetBoardState();
      const firstCell = getCellAt(0, 0);
      if (firstCell) {
        firstCell.focus();
      }
    });
  });

  refreshValidationState();
})();
