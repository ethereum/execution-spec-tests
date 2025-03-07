"""
Refiller pytest plugin that reads test cases from JSON/YAML files and fills them into test
fixtures.
"""

from pathlib import Path

import pytest


def pytest_addoption(parser: pytest.Parser):
    """Add command-line options to pytest."""
    refiller_group = parser.getgroup("refiller", "Arguments defining refiller behavior")
    refiller_group.addoption(
        "--json-filler-source",
        action="store",
        dest="json_filler_source",
        default="./tests/",
        type=Path,
        help=(
            "Path to directory containing JSON/YAML filler files."
            " Default: `ethereum-spec-evm-resolver`."
        ),
    )


def pytest_generate_tests(metafunc: pytest.Metafunc):
    """
    Pytest hook used to dynamically generate test cases for each fixture format a given
    test spec supports.
    """
    for test_type in SPEC_TYPES:
        if test_type.pytest_parameter_name() in metafunc.fixturenames:
            metafunc.parametrize(
                [test_type.pytest_parameter_name()],
                [
                    labeled_format_parameter_set(format_with_or_without_label)
                    for format_with_or_without_label in test_type.supported_fixture_formats
                ],
                scope="function",
                indirect=True,
            )
