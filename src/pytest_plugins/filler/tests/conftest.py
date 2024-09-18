"""
Local pytest configuration for filler tests.
"""

import os
import sysconfig

import pytest


def pytest_runtest_setup(item):
    """Hook to skip tests if running with pytest-xdist in parallel."""
    marker = item.get_closest_marker(name="run_in_serial")
    if marker is not None:
        if os.getenv("PYTEST_XDIST_WORKER_COUNT") not in [None, "1"]:
            pytest.skip("Skipping test because pytest-xdist is running with more than one worker.")


@pytest.fixture(autouse=True)
def monkeypatch_path_for_entry_points(monkeypatch):
    """
    Monkeypatch the PATH to add the "bin" directory where entrypoints are installed.

    This would typically be in the venv in which we're running these tests and fill,
    which, with uv, is `./.venv/bin`.

    This is required in order for fill to locate the ethereum-spec-evm-resolver
    "binary" (entrypoint) when being executed using pytester.
    """
    bin_dir = sysconfig.get_path("scripts")
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
