"""Pytest configuration for state tests."""

from pathlib import Path

import pytest

DEFAULT_BENCHMARK_FORK = "Prague"


def pytest_generate_tests(metafunc):
    """Add default valid_from marker to state tests without explicit fork specification."""
    state_dir = Path(__file__).parent
    test_file_path = Path(metafunc.definition.fspath)

    if state_dir in test_file_path.parents:
        has_valid_from = any(
            marker.name == "valid_from" for marker in metafunc.definition.iter_markers()
        )
        if not has_valid_from:
            metafunc.definition.add_marker(pytest.mark.valid_from(DEFAULT_BENCHMARK_FORK))


def pytest_collection_modifyitems(config, items):
    """Manage state test markers and filtering."""
    state_dir = Path(__file__).parent
    gen_docs = config.getoption("--gen-docs", default=False)

    if gen_docs:
        _add_state_markers_for_docs(items, state_dir)
        return

    marker_expr = config.getoption("-m", default="")

    items_to_remove = []

    for i, item in enumerate(items):
        item_path = Path(item.fspath)
        is_in_state_dir = state_dir in item_path.parents

        # Add state marker to tests in state directory that don't have it
        if is_in_state_dir and not item.get_closest_marker("state"):
            item.add_marker(pytest.mark.state)

        has_state_marker = item.get_closest_marker("state")

        run_state = marker_expr and ("state" in marker_expr) and ("not state" not in marker_expr)

        # When not running state tests, remove all state tests
        if not run_state and has_state_marker:
            items_to_remove.append(i)

    for i in reversed(items_to_remove):
        items.pop(i)


def _add_state_markers_for_docs(items, state_dir):
    """Add state markers for documentation generation."""
    for item in items:
        item_path = Path(item.fspath)
        if state_dir in item_path.parents and not item.get_closest_marker("state"):
            item.add_marker(pytest.mark.state)
