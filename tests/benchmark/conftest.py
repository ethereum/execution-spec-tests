"""Pytest configuration for benchmark tests."""

from pathlib import Path

import pytest


def pytest_collection_modifyitems(config, items):
    """Add the `benchmark` marker to all tests under `./tests/benchmark`."""
    marker_expr = config.getoption("-m", default="")
    run_benchmarks = marker_expr and (
        "benchmark" in marker_expr and "not benchmark" not in marker_expr
    )

    for item in items:
        if Path(__file__).parent in Path(item.fspath).parents:
            item.add_marker(pytest.mark.benchmark)
            if not run_benchmarks:
                item.add_marker(
                    pytest.mark.skip(
                        reason="Benchmark tests skipped by default. Use -m benchmark to run them."
                    )
                )
