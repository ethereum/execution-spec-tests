"""
Pytest plugin that applies config to all EIP-7692 tests.
"""

import pytest

EIP_7692_VERSION = "3.0.0"


def pytest_collection_modifyitems(config, items):
    """
    Add the required version of the EOF meta EIP to the test cases.
    """
    for item in items:
        mark = getattr(pytest.mark, "requires")
        item.add_marker(mark("EIP-7692", EIP_7692_VERSION))
