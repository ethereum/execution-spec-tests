"""Pytest configuration for benchmark tests."""

from pathlib import Path

import pytest


def pytest_collection_modifyitems(config, items):
    """Add the `benchmark` marker to all tests under `./tests/benchmark`."""
    marker_expr = config.getoption("-m", default="")
    run_benchmarks = marker_expr and (
        "benchmark" in marker_expr and "not benchmark" not in marker_expr
    )

    items_to_remove = []
    for item in items:
        if Path(__file__).parent in Path(item.fspath).parents:
            item.add_marker(pytest.mark.benchmark)
            if not run_benchmarks:
                items_to_remove.append(item)

    for item in items_to_remove:
        items.remove(item)
