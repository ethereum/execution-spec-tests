"""
Plugin to configure test suite scope based on command line options.

This module ensures that when using shared clients, the test suite scope is adjusted
to be session scoped instead of module scoped.
"""

def pytest_configure(config):
    """
    Configure pytest settings based on command line options.
    
    When --use-shared-clients is specified, we need to ensure the test_suite
    fixture is session scoped to avoid scope conflicts.
    """
    if config.getoption("use_shared_clients", False):
        # Override the test_suite_scope to be session when using shared clients
        config.test_suite_scope = "session"