"""
Pytest plug-in that allows fuzzed parametrization.
"""

import inspect
import random
from copy import copy
from typing import Annotated, Any, List, get_args, get_origin

import pytest


def pytest_addoption(parser: pytest.Parser):
    """
    Adds command-line options to pytest.
    """
    fuzzer_group = parser.getgroup("fuzzer", "Arguments defining fuzzer behavior")
    fuzzer_group.addoption(
        "--iterations",
        action="store",
        dest="iterations",
        type=int,
        default=1,
        help=("Number of iterations per test to generate"),
    )


@pytest.hookimpl(trylast=True)
def pytest_report_header(config: pytest.Config):
    """Add lines to pytest's console output header"""
    if config.option.collectonly:
        return
    iterations = config.getoption("iterations")
    return [f"{iterations}"]


def pytest_generate_tests(metafunc: pytest.Metafunc):
    """
    Pytest hook used to dynamically generate fuzzed test cases.
    """
    markers = list(metafunc.definition.iter_markers("fuzzable"))
    assert len(markers) <= 1, "Test should contain only one 'fuzzable' marker"

    if len(markers) == 0:
        pytest.skip("non-fuzzable")

    fuzz_arguments = markers[0].args

    pytest_params: List[Any] = []

    # Remove existing parametrize markers that conflict with fuzzing
    i = 0
    while i < len(metafunc.definition.own_markers):
        own_marker = metafunc.definition.own_markers[i]
        if own_marker.name == "parametrize":
            if type(own_marker.args[0]) is str:
                parametrize_args = own_marker.args[0].split(",")
            else:
                parametrize_args = copy(own_marker.args[0])
            if any(fuzz_argument in parametrize_args for fuzz_argument in fuzz_arguments):
                for fuzz_argument in fuzz_arguments:
                    if fuzz_argument in parametrize_args:
                        parametrize_args.remove(fuzz_argument)
                assert (
                    len(parametrize_args) == 0
                ), "`pytest.mark.parametrize` mixes fuzzable and non-fuzzable arguments"
                del metafunc.definition.own_markers[i]
        i += 1

    iterations = metafunc.config.getoption("iterations")

    fuzz_generators = []
    parameters = inspect.signature(metafunc.function).parameters
    for fuzz_argument in fuzz_arguments:
        assert (
            fuzz_argument in parameters
        ), f"fuzz argument not found in function signature {fuzz_argument}"
        annotation = parameters[fuzz_argument].annotation
        if get_origin(annotation) is Annotated:
            # Parameter type should be annotated with a fuzz generator
            args = get_args(annotation)[1:]
            # TODO: Create a fuzz generator type and match each argument until found
            fuzz_generators.append(args[0])
        elif annotation == int:
            fuzz_generators.append(lambda: random.randint(0, 2**256))
        else:
            raise ValueError(
                f"no fuzzer available for type {annotation} for parameter {fuzz_argument}"
            )

    for _ in range(iterations):
        iteration_args = []
        for fuzz_generator in fuzz_generators:
            iteration_args.append(fuzz_generator())
        pytest_params.append(pytest.param(*iteration_args))

    metafunc.parametrize(f"{','.join(fuzz_arguments)}", pytest_params, scope="function")
