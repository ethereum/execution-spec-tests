"""
A pytest plugin that is used to mark the validity of fields used within tests.
For example, for the case the case where the `to` address within a transaction is `nil`.
"""

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Register the plugin's custom markers and process command-line options.

    Custom marker registration:
    https://docs.pytest.org/en/7.1.x/how-to/writing_plugins.html#registering-custom-markers
    """
    config.addinivalue_line(
        "markers",
        "force_invalid_fields: a test that uses specific invalid fields.",
    )
