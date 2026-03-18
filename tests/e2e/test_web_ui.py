from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator
import socket
import threading
import time

import httpx
import pytest
import uvicorn

from src.api.main import create_app

try:
    from playwright.sync_api import Page, expect, sync_playwright
except ImportError:  # pragma: no cover - handled with pytest.skip in fixture
    Page = object
    expect = None
    sync_playwright = None


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


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", 0))
        except PermissionError as exc:  # pragma: no cover - environment-specific
            pytest.skip(f"Binding a local test port is not permitted in this environment: {exc}")
        return int(sock.getsockname()[1])


@contextmanager
def _run_live_server() -> Iterator[str]:
    port = _find_free_port()
    config = uvicorn.Config(
        create_app(testing=True),
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 10

    while time.monotonic() < deadline:
        if server.started:
            try:
                response = httpx.get(f"{base_url}/health", timeout=0.5)
                if response.status_code == 200:
                    break
            except httpx.HTTPError:
                pass
        time.sleep(0.1)
    else:
        server.should_exit = True
        thread.join(timeout=5)
        raise RuntimeError("Timed out waiting for the FastAPI server to start.")

    try:
        yield base_url
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.fixture(scope="module")
def live_server_url() -> Iterator[str]:
    with _run_live_server() as base_url:
        yield base_url


@pytest.fixture(scope="module")
def page() -> Iterator[Page]:
    if sync_playwright is None:
        pytest.skip("Playwright is not installed.")

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:  # pragma: no cover - environment-specific
            pytest.skip(f"Chromium is unavailable in this environment: {exc}")

        context = browser.new_context()
        page = context.new_page()

        try:
            yield page
        finally:
            context.close()
            browser.close()


def test_web_ui_solves_a_representative_puzzle(live_server_url: str, page: Page) -> None:
    page.goto(live_server_url, wait_until="networkidle")

    expect(page.get_by_role("heading", name="Solve a 9x9 puzzle in one pass")).to_be_visible()

    for row_index, row in enumerate(VALID_PUZZLE, start=1):
        for col_index, value in enumerate(row, start=1):
            if value == 0:
                continue

            page.locator(f"#cell-r{row_index}c{col_index}").fill(str(value))

    page.get_by_role("button", name="Solve").click()

    expect(page.locator("[data-status-message]")).to_have_text("Solved successfully.")
    grid_classes = page.locator("[data-sudoku-grid]").get_attribute("class") or ""
    assert "is-solved" in grid_classes.split()

    for row_index, row in enumerate(VALID_PUZZLE_SOLUTION, start=1):
        for col_index, expected_value in enumerate(row, start=1):
            cell = page.locator(f"#cell-r{row_index}c{col_index}")
            assert cell.input_value() == str(expected_value)

            if VALID_PUZZLE[row_index - 1][col_index - 1] == 0:
                assert cell.get_attribute("data-state") == "solved"
