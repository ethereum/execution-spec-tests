"""
Shared pytest fixtures and hooks for EEST generation modes (fill and execute).
"""

import warnings
from typing import List, cast

import pytest

from ethereum_test_forks import (
    Fork,
    get_closest_fork_with_solc_support,
    get_forks_with_solc_support,
)
from ethereum_test_specs import SPEC_TYPES
from ethereum_test_tools import Yul
from pytest_plugins.spec_version_checker.spec_version_checker import EIPSpecTestItem


@pytest.fixture(autouse=True)
def eips():
    """
    A fixture specifying that, by default, no EIPs should be activated for
    tests.

    This fixture (function) may be redefined in test filler modules in order
    to overwrite this default and return a list of integers specifying which
    EIPs should be activated for the tests in scope.
    """
    return []


@pytest.fixture
def yul(fork: Fork, request: pytest.FixtureRequest):
    """
    A fixture that allows contract code to be defined with Yul code.

    This fixture defines a class that wraps the ::ethereum_test_tools.Yul
    class so that upon instantiation within the test case, it provides the
    test case's current fork parameter. The forks is then available for use
    in solc's arguments for the Yul code compilation.

    Test cases can override the default value by specifying a fixed version
    with the @pytest.mark.compile_yul_with(FORK) marker.
    """
    solc_target_fork: Fork | None
    marker = request.node.get_closest_marker("compile_yul_with")
    assert hasattr(request.config, "solc_version"), "solc_version not set in pytest config."
    if marker:
        if not marker.args[0]:
            pytest.fail(
                f"{request.node.name}: Expected one argument in 'compile_yul_with' marker."
            )
        for fork in request.config.forks:  # type: ignore
            if fork.name() == marker.args[0]:
                solc_target_fork = fork
                break
        else:
            pytest.fail(f"{request.node.name}: Fork {marker.args[0]} not found in forks list.")
        assert solc_target_fork in get_forks_with_solc_support(request.config.solc_version)
    else:
        solc_target_fork = get_closest_fork_with_solc_support(fork, request.config.solc_version)
        assert solc_target_fork is not None, "No fork supports provided solc version."
        if solc_target_fork != fork and request.config.getoption("verbose") >= 1:
            warnings.warn(f"Compiling Yul for {solc_target_fork.name()}, not {fork.name()}.")

    class YulWrapper(Yul):
        def __new__(cls, *args, **kwargs):
            return super(YulWrapper, cls).__new__(cls, *args, **kwargs, fork=solc_target_fork)

    return YulWrapper


@pytest.fixture(scope="function")
def fixture_description(request: pytest.FixtureRequest) -> str:
    """Fixture to extract and combine docstrings from the test class and the test function."""
    description_unavailable = (
        "No description available - add a docstring to the python test class or function."
    )
    test_class_doc = f"Test class documentation:\n{request.cls.__doc__}" if request.cls else ""
    test_function_doc = (
        f"Test function documentation:\n{request.function.__doc__}"
        if request.function.__doc__
        else ""
    )
    if not test_class_doc and not test_function_doc:
        return description_unavailable
    combined_docstring = f"{test_class_doc}\n\n{test_function_doc}".strip()
    return combined_docstring


def pytest_make_parametrize_id(config: pytest.Config, val: str, argname: str):
    """
    Pytest hook called when generating test ids. We use this to generate
    more readable test ids for the generated tests.
    """
    return f"{argname}_{val}"


SPEC_TYPES_PARAMETERS: List[str] = [s.pytest_parameter_name() for s in SPEC_TYPES]


def pytest_runtest_call(item: pytest.Item):
    """
    Pytest hook called in the context of test execution.
    """
    if isinstance(item, EIPSpecTestItem):
        return

    class InvalidFiller(Exception):
        def __init__(self, message):
            super().__init__(message)

    item = cast(pytest.Function, item)  # help mypy infer type

    if "state_test" in item.fixturenames and "blockchain_test" in item.fixturenames:
        raise InvalidFiller(
            "A filler should only implement either a state test or " "a blockchain test; not both."
        )

    # Check that the test defines either test type as parameter.
    if not any([i for i in item.funcargs if i in SPEC_TYPES_PARAMETERS]):
        pytest.fail(
            "Test must define either one of the following parameters to "
            + "properly generate a test: "
            + ", ".join(SPEC_TYPES_PARAMETERS)
        )
