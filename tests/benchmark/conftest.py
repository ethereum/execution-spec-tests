"""Pytest configuration for benchmark tests."""

from pathlib import Path

import pytest


def pytest_collection_modifyitems(config, items):
    """Add the `benchmark` marker to all tests under `./tests/benchmark`."""
    marker_expr = config.getoption("-m", default="")
    gas_benchmark_values = config.getoption("--gas-benchmark-values", default=None)
    run_benchmarks = marker_expr and (
        "benchmark" in marker_expr and "not benchmark" not in marker_expr
    )

    if gas_benchmark_values:
        run_benchmarks = True

    items_for_removal = []
    for i, item in enumerate(items):
        is_benchmark_test = Path(__file__).parent in Path(item.fspath).parents

        if is_benchmark_test:
            benchmark_marker = pytest.mark.benchmark

            if gas_benchmark_values:
                gas_values = [int(v.strip()) for v in gas_benchmark_values.split(",")]
                benchmark_marker = pytest.mark.benchmark(gas_values=gas_values)

            item.add_marker(benchmark_marker)
            if not run_benchmarks:
                items_for_removal.append(i)

        elif run_benchmarks:
            items_for_removal.append(i)

    for i in reversed(items_for_removal):
        items.pop(i)
