"""
Pytest plugin to enable fork range configuration for the test session.
"""

import itertools
import sys
import textwrap
from dataclasses import dataclass, field
from typing import Any, List

import pytest
from pytest import Metafunc

from ethereum_test_forks import (
    Fork,
    ForkAttribute,
    get_deployed_forks,
    get_forks,
    get_transition_forks,
    transition_fork_to,
)
from evm_transition_tool import TransitionTool


def pytest_addoption(parser):
    """
    Adds command-line options to pytest.
    """
    fork_group = parser.getgroup("Forks", "Specify the fork range to generate fixtures for")
    fork_group.addoption(
        "--forks",
        action="store_true",
        dest="show_fork_help",
        default=False,
        help="Display forks supported by the test framework and exit.",
    )
    fork_group.addoption(
        "--fork",
        action="store",
        dest="single_fork",
        default=None,
        help="Only fill tests for the specified fork.",
    )
    fork_group.addoption(
        "--from",
        action="store",
        dest="forks_from",
        default=None,
        help="Fill tests from and including the specified fork.",
    )
    fork_group.addoption(
        "--until",
        action="store",
        dest="forks_until",
        default=None,
        help="Fill tests until and including the specified fork.",
    )


@dataclass(kw_only=True)
class ForkCovariantParameter:
    """
    Value list for a fork covariant parameter in a given fork.
    """

    name: str
    values: List[Any]


@dataclass(kw_only=True)
class ForkParametrizer:
    """
    A parametrizer for a test case that is parametrized by the fork.
    """

    fork: Fork
    mark: pytest.MarkDecorator | None = None
    fork_covariant_parameters: List[ForkCovariantParameter] = field(default_factory=list)

    def get_parameter_names(self) -> List[str]:
        """
        Return the parameter names for the test case.
        """
        parameter_names = ["fork"]
        for p in self.fork_covariant_parameters:
            if "," in p.name:
                parameter_names.extend(p.name.split(","))
            else:
                parameter_names.append(p.name)
        return parameter_names

    def get_parameter_values(self) -> List[Any]:
        """
        Return the parameter values for the test case.
        """
        param_value_combinations = [
            params
            for params in itertools.product(
                [self.fork],
                *[p.values for p in self.fork_covariant_parameters],
            )
        ]
        for i in range(len(param_value_combinations)):
            # if the parameter is a tuple, we need to flatten it
            param_value_combinations[i] = list(
                itertools.chain.from_iterable(
                    [v] if not isinstance(v, tuple) else v for v in param_value_combinations[i]
                )
            )
        return [
            pytest.param(*params, marks=[self.mark] if self.mark else [])
            for params in param_value_combinations
        ]


@dataclass(kw_only=True)
class CovariantDescriptor:
    """
    A descriptor for a parameter that is covariant with the fork:
    the parametrized values change depending on the fork.
    """

    marker_name: str
    description: str
    fork_attribute_name: str
    parameter_name: str

    def check_enabled(self, metafunc: Metafunc) -> bool:
        """
        Check if the marker is enabled for the given test function.
        """
        m = metafunc.definition.iter_markers(self.marker_name)
        return m is not None and len(list(m)) > 0

    def add_values(self, metafunc: Metafunc, fork_parametrizer: ForkParametrizer) -> None:
        """
        Add the values for the covariant parameter to the parametrizer.
        """
        if not self.check_enabled(metafunc=metafunc):
            return
        fork = fork_parametrizer.fork
        get_fork_covariant_values: ForkAttribute = getattr(fork, self.fork_attribute_name)
        values = get_fork_covariant_values(block_number=0, timestamp=0)
        assert isinstance(values, list)
        assert len(values) > 0
        fork_parametrizer.fork_covariant_parameters.append(
            ForkCovariantParameter(name=self.parameter_name, values=values)
        )


fork_covariant_descriptors = [
    CovariantDescriptor(
        marker_name="with_all_tx_types",
        description="marks a test to be parametrized for all tx types at parameter named tx_type"
        " of type int",
        fork_attribute_name="tx_types",
        parameter_name="tx_type",
    ),
    CovariantDescriptor(
        marker_name="with_all_contract_creating_tx_types",
        description="marks a test to be parametrized for all tx types that can create a contract"
        " at parameter named tx_type of type int",
        fork_attribute_name="contract_creating_tx_types",
        parameter_name="tx_type",
    ),
    CovariantDescriptor(
        marker_name="with_all_precompiles",
        description="marks a test to be parametrized for all precompiles at parameter named"
        " precompile of type int",
        fork_attribute_name="precompiles",
        parameter_name="precompile",
    ),
    CovariantDescriptor(
        marker_name="with_all_evm_code_types",
        description="marks a test to be parametrized for all EVM code types at parameter named"
        " `evm_code_type` of type `EVMCodeType`, such as `LEGACY` and `EOF_V1`",
        fork_attribute_name="evm_code_types",
        parameter_name="evm_code_type",
    ),
    CovariantDescriptor(
        marker_name="with_all_call_opcodes",
        description="marks a test to be parametrized for all *CALL opcodes at parameter named"
        " call_opcode, and also the appropriate EVM code type at parameter named evm_code_type",
        fork_attribute_name="call_opcodes",
        parameter_name="call_opcode,evm_code_type",
    ),
]


def get_fork_range(forks: List[Fork], forks_from: Fork, forks_until: Fork) -> List[Fork]:
    """
    Get the fork range from forks_from to forks_until.
    """
    return [
        next_fork for next_fork in forks if next_fork <= forks_until and next_fork >= forks_from
    ]


def get_last_descendant(forks: List[Fork], fork: Fork) -> Fork:
    """
    Get the last descendant of a class in the inheritance hierarchy.
    """
    for next_fork in reversed(forks):
        if next_fork >= fork:
            return next_fork
    return fork


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Register the plugin's custom markers and process command-line options.

    Custom marker registration:
    https://docs.pytest.org/en/7.1.x/how-to/writing_plugins.html#registering-custom-markers
    """
    config.addinivalue_line(
        "markers",
        (
            "valid_at_transition_to(fork): specifies a test case is valid "
            "only at fork transition boundary to the specified fork"
        ),
    )
    config.addinivalue_line(
        "markers",
        "valid_from(fork): specifies from which fork a test case is valid",
    )
    config.addinivalue_line(
        "markers",
        "valid_until(fork): specifies until which fork a test case is valid",
    )

    for d in fork_covariant_descriptors:
        config.addinivalue_line("markers", f"{d.marker_name}: {d.description}")

    config.forks = [fork for fork in get_forks() if not fork.ignore()]
    config.fork_names = [fork.name() for fork in config.forks]

    available_forks_help = textwrap.dedent(
        f"""\
        Available forks:
        {", ".join(config.fork_names)}
        """
    )
    available_forks_help += textwrap.dedent(
        f"""\
        Available transition forks:
        {", ".join([fork.name() for fork in get_transition_forks()])}
        """
    )

    def get_fork_option(config, option_name: str, parameter_name: str) -> Fork | None:
        """Post-process get option to allow for external fork conditions."""
        option = config.getoption(option_name)
        if not option:
            return None
        if option == "Merge":
            option = "Paris"
        for fork in get_forks():
            if option == fork.name():
                return fork
        print(
            f"Error: Unsupported fork provided to {parameter_name}:",
            option,
            "\n",
            file=sys.stderr,
        )
        print(available_forks_help, file=sys.stderr)
        pytest.exit("Invalid command-line options.", returncode=pytest.ExitCode.USAGE_ERROR)

    single_fork = get_fork_option(config, "single_fork", "--fork")
    forks_from = get_fork_option(config, "forks_from", "--from")
    forks_until = get_fork_option(config, "forks_until", "--until")
    show_fork_help = config.getoption("show_fork_help")

    dev_forks_help = textwrap.dedent(
        "To run tests for a fork under active development, it must be "
        "specified explicitly via --forks-until=FORK.\n"
        "Tests are only ran for deployed mainnet forks by default, i.e., "
        f"until {get_deployed_forks()[-1].name()}.\n"
    )
    if show_fork_help:
        print(available_forks_help)
        print(dev_forks_help)
        pytest.exit("After displaying help.", returncode=0)

    if single_fork and (forks_from or forks_until):
        print(
            "Error: --fork cannot be used in combination with --from or --until", file=sys.stderr
        )
        pytest.exit("Invalid command-line options.", returncode=pytest.ExitCode.USAGE_ERROR)

    if single_fork:
        forks_from = single_fork
        forks_until = single_fork
    else:
        if not forks_from:
            forks_from = config.forks[0]
        if not forks_until:
            forks_until = get_last_descendant(get_deployed_forks(), forks_from)

    config.fork_range = get_fork_range(config.forks, forks_from, forks_until)

    if not config.fork_range:
        print(
            f"Error: --from {forks_from.name()} --until {forks_until.name()} "
            "creates an empty fork range.",
            file=sys.stderr,
        )
        pytest.exit(
            "Command-line options produce empty fork range.",
            returncode=pytest.ExitCode.USAGE_ERROR,
        )

    # with --collect-only, we don't have access to these config options
    if config.option.collectonly:
        config.unsupported_forks = []
        return

    evm_bin = config.getoption("evm_bin")
    t8n = TransitionTool.from_binary_path(binary_path=evm_bin)
    config.unsupported_forks = [
        fork for fork in config.fork_range if not t8n.is_fork_supported(fork)
    ]


@pytest.hookimpl(trylast=True)
def pytest_report_header(config, start_path):
    """A pytest hook called to obtain the report header."""
    bold = "\033[1m"
    warning = "\033[93m"
    reset = "\033[39;49m"
    header = [
        (
            bold
            + f"Executing tests for: {', '.join([f.name() for f in config.fork_range])} "
            + reset
        ),
    ]
    if config.getoption("forks_until") is None:
        header += [
            (
                bold + warning + "Only executing tests with stable/deployed forks: "
                "Specify an upcoming fork via --until=fork to "
                "add forks under development." + reset
            )
        ]
    return header


@pytest.fixture(autouse=True)
def fork(request):
    """
    Parametrize test cases by fork.
    """
    pass


def get_validity_marker_args(
    metafunc: Metafunc,
    validity_marker_name: str,
    test_name: str,
) -> Fork | None:
    """Check and return the arguments specified to validity markers.

    Check that the validity markers:

    - `pytest.mark.valid_from`
    - `pytest.mark.valid_until`
    - `pytest.mark.valid_at_transition_to`

    are applied at most once and have been provided with exactly one
    argument which is a valid fork name.

    Args:
        metafunc: Pytest's metafunc object.
        validity_marker_name: Name of the validity marker to validate
            and return.
        test_name: The name of the test being parametrized by
            `pytest_generate_tests`.

    Returns:
        The name of the fork specified to the validity marker.
    """
    validity_markers = [
        marker for marker in metafunc.definition.iter_markers(validity_marker_name)
    ]
    if not validity_markers:
        return None
    if len(validity_markers) > 1:
        pytest.fail(f"'{test_name}': Too many '{validity_marker_name}' markers applied to test. ")
    if len(validity_markers[0].args) == 0:
        pytest.fail(f"'{test_name}': Missing fork argument with '{validity_marker_name}' marker. ")
    if len(validity_markers[0].args) > 1:
        pytest.fail(
            f"'{test_name}': Too many arguments specified to '{validity_marker_name}' marker. "
        )
    fork_name = validity_markers[0].args[0]

    for fork in metafunc.config.forks:  # type: ignore
        if fork.name() == fork_name:
            return fork

    pytest.fail(
        f"'{test_name}' specifies an invalid fork '{fork_name}' to the "
        f"'{validity_marker_name}'. "
        f"List of valid forks: {', '.join(metafunc.config.fork_names)}"  # type: ignore
    )


def pytest_generate_tests(metafunc):
    """
    Pytest hook used to dynamically generate test cases.
    """
    test_name = metafunc.function.__name__
    valid_at_transition_to = get_validity_marker_args(
        metafunc, "valid_at_transition_to", test_name
    )
    valid_from = get_validity_marker_args(metafunc, "valid_from", test_name)
    valid_until = get_validity_marker_args(metafunc, "valid_until", test_name)

    if valid_at_transition_to and valid_from:
        pytest.fail(
            f"'{test_name}': "
            "The markers 'valid_from' and 'valid_at_transition_to' can't be combined. "
        )
    if valid_at_transition_to and valid_until:
        pytest.fail(
            f"'{test_name}': "
            "The markers 'valid_until' and 'valid_at_transition_to' can't be combined. "
        )

    intersection_range = []

    if valid_at_transition_to:
        if valid_at_transition_to in metafunc.config.fork_range:
            intersection_range = transition_fork_to(valid_at_transition_to)

    else:
        if not valid_from:
            valid_from = metafunc.config.forks[0]

        if not valid_until:
            valid_until = get_last_descendant(metafunc.config.fork_range, valid_from)

        test_fork_range = get_fork_range(metafunc.config.forks, valid_from, valid_until)

        if not test_fork_range:
            pytest.fail(
                "The test function's "
                f"'{test_name}' fork validity markers generate "
                "an empty fork range. Please check the arguments to its "
                f"markers:  @pytest.mark.valid_from ({valid_from}) and "
                f"@pytest.mark.valid_until ({valid_until})."
            )

        intersection_range = list(set(metafunc.config.fork_range) & set(test_fork_range))
        intersection_range.sort(key=metafunc.config.fork_range.index)

    if "fork" in metafunc.fixturenames:
        if not intersection_range:
            if metafunc.config.getoption("verbose") >= 2:
                pytest_params = [
                    pytest.param(
                        None,
                        marks=[
                            pytest.mark.skip(
                                reason=(
                                    f"{test_name} is not valid for any any of forks specified on "
                                    "the command-line."
                                )
                            )
                        ],
                    )
                ]
                metafunc.parametrize("fork", pytest_params, scope="function")
        else:
            pytest_params = [
                (
                    ForkParametrizer(
                        fork=fork,
                        mark=pytest.mark.skip(
                            reason=(
                                f"Fork '{fork}' unsupported by "
                                f"'{metafunc.config.getoption('evm_bin')}'."
                            )
                        ),
                    )
                    if fork.name() in metafunc.config.unsupported_forks
                    else ForkParametrizer(fork=fork)
                )
                for fork in intersection_range
            ]
            add_fork_covariant_parameters(metafunc, pytest_params)
            parametrize_fork(metafunc, pytest_params)


def add_fork_covariant_parameters(
    metafunc: Metafunc, fork_parametrizers: List[ForkParametrizer]
) -> None:
    """
    Iterate over the fork covariant descriptors and add their values to the test function.
    """
    for covariant_descriptor in fork_covariant_descriptors:
        for fork_parametrizer in fork_parametrizers:
            covariant_descriptor.add_values(metafunc=metafunc, fork_parametrizer=fork_parametrizer)


def parametrize_fork(metafunc: Metafunc, fork_parametrizers: List[ForkParametrizer]) -> None:
    """
    Add the fork parameters to the test function.
    """
    param_names: List[str] = []
    param_values: List[Any] = []

    for fork_parametrizer in fork_parametrizers:
        if not param_names:
            param_names = fork_parametrizer.get_parameter_names()
        else:
            assert param_names == fork_parametrizer.get_parameter_names()
        param_values.extend(fork_parametrizer.get_parameter_values())
    metafunc.parametrize(param_names, param_values, scope="function")
