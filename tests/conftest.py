"""
Pytest (plugin) definitions local to Cancun tests.
"""
import warnings

import pytest


def pytest_collection_modifyitems(items):
    """
    Modify tests post collection.

    Here we override the default behavior of the `yul` fixture so that
    solc compiles with shanghai instead of cancun (which is unavailable
    in solc 0.8.20).
    """
    for item in items:
        if "Cancun" in item.name and "yul" in item.fixturenames:
            warnings.warn("Compiling Yul source with Shanghai, not Cancun.")
            item.add_marker(pytest.mark.compile_yul_with("Shanghai"))
