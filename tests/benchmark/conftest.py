"""Pytest configuration for benchmark tests."""

from pathlib import Path

import pytest

DEFAULT_BENCHMARK_FORK = "Prague"


def pytest_generate_tests(metafunc):
    """Add default valid_from marker to benchmark tests without explicit fork specification."""
    benchmark_dir = Path(__file__).parent
    test_file_path = Path(metafunc.definition.fspath)

    if benchmark_dir in test_file_path.parents:
        has_valid_from = any(
            marker.name == "valid_from" for marker in metafunc.definition.iter_markers()
        )
        if not has_valid_from:
            metafunc.definition.add_marker(pytest.mark.valid_from(DEFAULT_BENCHMARK_FORK))


def pytest_collection_modifyitems(config, items):
    """Manage benchmark and bloatnet test markers and filtering."""
    benchmark_dir = Path(__file__).parent
    gen_docs = config.getoption("--gen-docs", default=False)

    if gen_docs:
        _add_benchmark_markers_for_docs(items, benchmark_dir)
        return

    marker_expr = config.getoption("-m", default="")
    run_benchmarks = _should_run_benchmarks(marker_expr, config)
    run_bloatnet = _should_run_bloatnet(marker_expr)

    _process_test_items(items, benchmark_dir, run_benchmarks, run_bloatnet)


def _add_benchmark_markers_for_docs(items, benchmark_dir):
    """Add benchmark markers for documentation generation."""
    for item in items:
        if benchmark_dir in Path(item.fspath).parents:
            if not item.get_closest_marker("benchmark") and not item.get_closest_marker(
                "bloatnet"
            ):
                item.add_marker(pytest.mark.benchmark)


def _should_run_benchmarks(marker_expr, config):
    """Check if benchmark tests should run based on marker expression and config."""
    return (
        marker_expr and ("benchmark" in marker_expr) and ("not benchmark" not in marker_expr)
    ) or config.getoption("--gas-benchmark-values", default=None)


def _should_run_bloatnet(marker_expr):
    """Check if bloatnet tests should run based on marker expression."""
    return marker_expr and ("bloatnet" in marker_expr) and ("not bloatnet" not in marker_expr)


def _process_test_items(items, benchmark_dir, run_benchmarks, run_bloatnet):
    """Process test items to add markers and filter based on selection criteria."""
    items_to_remove = []

    for i, item in enumerate(items):
        is_in_benchmark_dir = benchmark_dir in Path(item.fspath).parents
        is_benchmark_test = is_in_benchmark_dir or item.get_closest_marker("benchmark")
        is_bloatnet_test = item.get_closest_marker("bloatnet")

        # Add appropriate markers
        if (
            is_in_benchmark_dir
            and not item.get_closest_marker("benchmark")
            and not item.get_closest_marker("bloatnet")
        ):
            item.add_marker(pytest.mark.benchmark)

        if is_bloatnet_test and not item.get_closest_marker("bloatnet"):
            item.add_marker(pytest.mark.bloatnet)

        # Determine if item should be removed
        if is_bloatnet_test and not run_bloatnet:
            items_to_remove.append(i)
        elif is_benchmark_test and not run_benchmarks:
            items_to_remove.append(i)
        elif (
            (run_benchmarks or run_bloatnet) and (not is_benchmark_test) and (not is_bloatnet_test)
        ):
            items_to_remove.append(i)

    # Remove items in reverse order to preserve indices
    for i in reversed(items_to_remove):
        items.pop(i)
