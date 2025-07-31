"""
Pytest plugin for skipping tests based on a YAML skip list file.

This plugin allows specifying tests to be skipped via:
1. A YAML file containing node IDs (default: skip_tests.yaml)
2. Command line argument --skip-list-file to specify custom file
3. Command line argument --skip-tests for comma-separated patterns

Follows patterns established by other pytest_plugins in this codebase.
"""

import fnmatch
from pathlib import Path
from typing import List

import pytest
import yaml


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add command-line options for skip list functionality."""
    skip_group = parser.getgroup("skip_list", "Skip tests based on configured patterns")

    skip_group.addoption(
        "--skip-list-file",
        action="store",
        dest="skip_list_file",
        type=Path,
        default="skip_tests.yaml",
        help="Path to YAML file containing test node IDs to skip (default: skip_tests.yaml)",
    )

    skip_group.addoption(
        "--skip-tests",
        action="store",
        dest="skip_tests_cli",
        default="",
        help="Comma-separated list of test node ID patterns to skip",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """Process skip list configuration and store patterns."""
    skip_patterns: set[str] = set()

    # Load from YAML file
    skip_file = config.getoption("skip_list_file")
    if skip_file and Path(skip_file).exists():
        try:
            with open(skip_file, "r") as f:
                skip_data = yaml.safe_load(f) or {}

            # Support both list format and dict format
            if isinstance(skip_data, list):
                skip_patterns.update(skip_data)
            elif isinstance(skip_data, dict) and "skip_tests" in skip_data:
                skip_list = skip_data["skip_tests"]
                if isinstance(skip_list, list):
                    skip_patterns.update(skip_list)

        except (yaml.YAMLError, IOError) as e:
            pytest.exit(f"Error reading skip list file {skip_file}: {e}")

    # Load from command line
    cli_patterns = config.getoption("skip_tests_cli")
    if cli_patterns:
        patterns = [p.strip() for p in cli_patterns.split(",") if p.strip()]
        skip_patterns.update(patterns)

    # Store patterns in config for use by collection hook
    setattr(config, "_skip_list_patterns", skip_patterns)


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]) -> None:
    """Skip items that match patterns in the skip list."""
    skip_patterns: set[str] = getattr(config, "_skip_list_patterns", set())

    if not skip_patterns:
        return

    skipped_items = []

    for item in items:
        node_id = item.nodeid

        # Check if item matches any skip pattern
        should_skip = False
        matched_pattern = None

        for pattern in skip_patterns:
            # Support both exact match and fnmatch patterns
            if node_id == pattern or fnmatch.fnmatch(node_id, pattern):
                should_skip = True
                matched_pattern = pattern
                break

        if should_skip:
            # Add skip marker with reason
            skip_marker = pytest.mark.skip(
                reason=f"Skipped by skip list pattern: {matched_pattern}"
            )
            item.add_marker(skip_marker)
            skipped_items.append((node_id, matched_pattern))
