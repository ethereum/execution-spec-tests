"""Configuration for filter_fixtures tests."""


def pytest_addoption(parser):
    """Add custom command-line options for testing."""
    parser.addoption(
        "--fixtures-dir",
        action="store",
        default=None,
        help="Path to fixtures directory to test against (default: uses test_fixtures)",
    )
    parser.addoption(
        "--before-fixtures-dir",
        action="store",
        default=None,
        help="Path to before-filtering fixtures directory for comparison tests",
    )
    parser.addoption(
        "--after-fixtures-dir",
        action="store",
        default=None,
        help="Path to after-filtering fixtures directory for comparison tests",
    )
