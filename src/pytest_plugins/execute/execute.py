"""
Top-level pytest configuration file providing:
- Command-line options,
- Test-fixtures that can be used by all test cases,
and that modifies pytest hooks in order to fill test specs for all tests and
writes the generated fixtures to file.
"""

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Type

import pytest
from pytest_metadata.plugin import metadata_key  # type: ignore

from ethereum_test_execution import BaseExecute, ExecuteFormats
from ethereum_test_forks import (
    Fork,
    Frontier,
    Paris,
    get_closest_fork_with_solc_support,
    get_forks_with_solc_support,
)
from ethereum_test_rpc import EthRPC
from ethereum_test_tools import SPEC_TYPES, BaseTest, TestInfo, Transaction, Yul
from ethereum_test_tools.code import Solc
from evm_transition_tool import TransitionTool
from pytest_plugins.spec_version_checker.spec_version_checker import EIPSpecTestItem

from .pre_alloc import Alloc


def default_output_directory() -> str:
    """
    The default directory to store the generated test fixtures. Defined as a
    function to allow for easier testing.
    """
    return "./execution_results"


def default_html_report_filename() -> str:
    """
    The default file to store the generated HTML test report. Defined as a
    function to allow for easier testing.
    """
    return "report_execute.html"


def pytest_addoption(parser):
    """
    Adds command-line options to pytest.
    """
    evm_group = parser.getgroup("evm", "Arguments defining evm executable behavior")
    evm_group.addoption(
        "--evm-bin",
        action="store",
        dest="evm_bin",
        type=Path,
        default=None,
        help=(
            "Path to an evm executable that provides `t8n`. Default: First 'evm' entry in PATH."
        ),
    )
    evm_group.addoption(
        "--traces",
        action="store_true",
        dest="evm_collect_traces",
        default=None,
        help="Collect traces of the execution information from the transition tool.",
    )
    evm_group.addoption(
        "--verify-fixtures",
        action="store_true",
        dest="verify_fixtures",
        default=False,
        help=(
            "Verify generated fixture JSON files using geth's evm blocktest command. "
            "By default, the same evm binary as for the t8n tool is used. A different (geth) evm "
            "binary may be specified via --verify-fixtures-bin, this must be specified if filling "
            "with a non-geth t8n tool that does not support blocktest."
        ),
    )
    evm_group.addoption(
        "--verify-fixtures-bin",
        action="store",
        dest="verify_fixtures_bin",
        type=Path,
        default=None,
        help=(
            "Path to an evm executable that provides the `blocktest` command. "
            "Default: The first (geth) 'evm' entry in PATH."
        ),
    )

    solc_group = parser.getgroup("solc", "Arguments defining the solc executable")
    solc_group.addoption(
        "--solc-bin",
        action="store",
        dest="solc_bin",
        default=None,
        help=(
            "Path to a solc executable (for Yul source compilation). "
            "Default: First 'solc' entry in PATH."
        ),
    )

    test_group = parser.getgroup("tests", "Arguments defining filler location and output")
    test_group.addoption(
        "--filler-path",
        action="store",
        dest="filler_path",
        default="./tests/",
        type=Path,
        help="Path to filler directives",
    )
    test_group.addoption(
        "--output",
        action="store",
        dest="output",
        type=Path,
        default=Path(default_output_directory()),
        help=(
            "Directory path to write the execution result. "
            f"Default: '{default_output_directory()}'."
        ),
    )
    test_group.addoption(
        "--no-html",
        action="store_true",
        dest="disable_html",
        default=False,
        help=(
            "Don't generate an HTML test report (in the output directory). "
            "The --html flag can be used to specify a different path."
        ),
    )
    test_group.addoption(
        "--build-name",
        action="store",
        dest="build_name",
        default=None,
        type=str,
        help="Specify a build name for the fixtures.ini file, e.g., 'stable'.",
    )

    debug_group = parser.getgroup("debug", "Arguments defining debug behavior")
    debug_group.addoption(
        "--evm-dump-dir",
        "--t8n-dump-dir",
        action="store",
        dest="base_dump_dir",
        default="",
        help="Path to dump the transition tool debug output.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Pytest hook called after command line options have been parsed and before
    test collection begins.

    Couple of notes:
    1. Register the plugin's custom markers and process command-line options.

        Custom marker registration:
        https://docs.pytest.org/en/7.1.x/how-to/writing_plugins.html#registering-custom-markers

    2. `@pytest.hookimpl(tryfirst=True)` is applied to ensure that this hook is
        called before the pytest-html plugin's pytest_configure to ensure that
        it uses the modified `htmlpath` option.
    """
    for execute_format in ExecuteFormats:
        config.addinivalue_line(
            "markers",
            (f"{execute_format.name.lower()}: {execute_format.description()}"),
        )
    config.addinivalue_line(
        "markers",
        "yul_test: a test case that compiles Yul code.",
    )
    config.addinivalue_line(
        "markers",
        "compile_yul_with(fork): Always compile Yul source using the corresponding evm version.",
    )
    if config.option.collectonly:
        return
    if not config.getoption("disable_html") and config.getoption("htmlpath") is None:
        # generate an html report by default, unless explicitly disabled
        config.option.htmlpath = config.getoption("output") / default_html_report_filename()
    # Instantiate the transition tool here to check that the binary path/trace option is valid.
    # This ensures we only raise an error once, if appropriate, instead of for every test.
    t8n = TransitionTool.from_binary_path(
        binary_path=config.getoption("evm_bin"), trace=config.getoption("evm_collect_traces")
    )
    if (
        isinstance(config.getoption("numprocesses"), int)
        and config.getoption("numprocesses") > 0
        and "Besu" in str(t8n.detect_binary_pattern)
    ):
        pytest.exit(
            "The Besu t8n tool does not work well with the xdist plugin; use -n=0.",
            returncode=pytest.ExitCode.USAGE_ERROR,
        )
    config.solc_version = Solc(config.getoption("solc_bin")).version
    if config.solc_version < Frontier.solc_min_version():
        pytest.exit(
            f"Unsupported solc version: {config.solc_version}. Minimum required version is "
            f"{Frontier.solc_min_version()}",
            returncode=pytest.ExitCode.USAGE_ERROR,
        )

    config.stash[metadata_key]["Tools"] = {
        "t8n": t8n.version(),
        "solc": str(config.solc_version),
    }
    command_line_args = "fill " + " ".join(config.invocation_params.args)
    config.stash[metadata_key]["Command-line args"] = f"<code>{command_line_args}</code>"


@pytest.hookimpl(trylast=True)
def pytest_report_header(config, start_path):
    """Add lines to pytest's console output header"""
    if config.option.collectonly:
        return
    t8n_version = config.stash[metadata_key]["Tools"]["t8n"]
    solc_version = config.stash[metadata_key]["Tools"]["solc"]
    return [(f"{t8n_version}, {solc_version}")]


def pytest_metadata(metadata):
    """
    Add or remove metadata to/from the pytest report.
    """
    metadata.pop("JAVA_HOME", None)


def pytest_html_results_table_header(cells):
    """
    Customize the table headers of the HTML report table.
    """
    cells.insert(3, '<th class="sortable" data-column-type="fixturePath">JSON Fixture File</th>')
    cells.insert(4, '<th class="sortable" data-column-type="evmDumpDir">EVM Dump Dir</th>')
    del cells[-1]  # Remove the "Links" column


def pytest_html_results_table_row(report, cells):
    """
    Customize the table rows of the HTML report table.
    """
    if hasattr(report, "user_properties"):
        user_props = dict(report.user_properties)
        if (
            report.passed
            and "fixture_path_absolute" in user_props
            and "fixture_path_relative" in user_props
        ):
            fixture_path_absolute = user_props["fixture_path_absolute"]
            fixture_path_relative = user_props["fixture_path_relative"]
            fixture_path_link = (
                f'<a href="{fixture_path_absolute}" target="_blank">{fixture_path_relative}</a>'
            )
            cells.insert(3, f"<td>{fixture_path_link}</td>")
        elif report.failed:
            cells.insert(3, "<td>Fixture unavailable</td>")
        if "evm_dump_dir" in user_props:
            if user_props["evm_dump_dir"] is None:
                cells.insert(
                    4, "<td>For t8n debug info use <code>--evm-dump-dir=path --traces</code></td>"
                )
            else:
                evm_dump_dir = user_props.get("evm_dump_dir")
                if evm_dump_dir == "N/A":
                    evm_dump_entry = "N/A"
                else:
                    evm_dump_entry = f'<a href="{evm_dump_dir}" target="_blank">{evm_dump_dir}</a>'
                cells.insert(4, f"<td>{evm_dump_entry}</td>")
    del cells[-1]  # Remove the "Links" column


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    This hook is called when each test is run and a report is being made.

    Make each test's fixture json path available to the test report via
    user_properties.
    """
    outcome = yield
    report = outcome.get_result()

    if call.when == "call":
        if hasattr(item.config, "fixture_path_absolute") and hasattr(
            item.config, "fixture_path_relative"
        ):
            report.user_properties.append(
                ("fixture_path_absolute", item.config.fixture_path_absolute)
            )
            report.user_properties.append(
                ("fixture_path_relative", item.config.fixture_path_relative)
            )
        if hasattr(item.config, "evm_dump_dir") and hasattr(item.config, "execute_format"):
            if item.config.execute_format in [
                "state_test",
                "blockchain_test",
                "blockchain_test_hive",
            ]:
                report.user_properties.append(("evm_dump_dir", item.config.evm_dump_dir))
            else:
                report.user_properties.append(("evm_dump_dir", "N/A"))  # not yet for EOF


def pytest_html_report_title(report):
    """
    Set the HTML report title (pytest-html plugin).
    """
    report.title = "Fill Test Report"


@pytest.fixture(autouse=True, scope="session")
def evm_bin(request) -> Path:
    """
    Returns the configured evm tool binary path used to run t8n.
    """
    return request.config.getoption("evm_bin")


@pytest.fixture(autouse=True, scope="session")
def verify_fixtures_bin(request) -> Path:
    """
    Returns the configured evm tool binary path used to run statetest or
    blocktest.
    """
    return request.config.getoption("verify_fixtures_bin")


@pytest.fixture(autouse=True, scope="session")
def solc_bin(request):
    """
    Returns the configured solc binary path.
    """
    return request.config.getoption("solc_bin")


@pytest.fixture(autouse=True, scope="session")
def t8n(request, evm_bin: Path) -> Generator[TransitionTool, None, None]:
    """
    Returns the configured transition tool.
    """
    t8n = TransitionTool.from_binary_path(
        binary_path=evm_bin, trace=request.config.getoption("evm_collect_traces")
    )
    yield t8n
    t8n.shutdown()


@pytest.fixture(scope="session")
def base_dump_dir(request) -> Optional[Path]:
    """
    The base directory to dump the evm debug output.
    """
    base_dump_dir_str = request.config.getoption("base_dump_dir")
    if base_dump_dir_str:
        return Path(base_dump_dir_str)
    return None


@pytest.fixture(scope="function")
def dump_dir_parameter_level(
    request, base_dump_dir: Optional[Path], filler_path: Path
) -> Optional[Path]:
    """
    The directory to dump evm transition tool debug output on a test parameter
    level.

    Example with --evm-dump-dir=/tmp/evm:
    -> /tmp/evm/shanghai__eip3855_push0__test_push0__test_push0_key_sstore/fork_shanghai/
    """
    evm_dump_dir = node_to_test_info(request.node).get_dump_dir_path(
        base_dump_dir,
        filler_path,
        level="test_parameter",
    )
    # NOTE: Use str for compatibility with pytest-dist
    if evm_dump_dir:
        request.node.config.evm_dump_dir = str(evm_dump_dir)
    else:
        request.node.config.evm_dump_dir = None
    return evm_dump_dir


@dataclass(kw_only=True)
class Collector:
    """
    A class that collects transactions and post-allocations for every test case.
    """

    eth_rpc: EthRPC
    collected_tests: Dict[str, BaseExecute] = field(default_factory=dict)

    def collect(self, test_name: str, execute_format: BaseExecute):
        """
        Collects the transactions and post-allocations for the test case.
        """
        self.collected_tests[test_name] = execute_format


@pytest.fixture(scope="session")
def collector(
    request,
    eth_rpc: EthRPC,
) -> Generator[Collector, None, None]:
    """
    Returns the configured fixture collector instance used for all tests
    in one test module.
    """
    collector = Collector(eth_rpc=eth_rpc)
    yield collector


@pytest.fixture(autouse=True, scope="session")
def filler_path(request) -> Path:
    """
    Returns the directory containing the tests to execute.
    """
    return request.config.getoption("filler_path")


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
def yul(fork: Fork, request):
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
    if marker:
        if not marker.args[0]:
            pytest.fail(
                f"{request.node.name}: Expected one argument in 'compile_yul_with' marker."
            )
        for fork in request.config.forks:
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


SPEC_TYPES_PARAMETERS: List[str] = [s.pytest_parameter_name() for s in SPEC_TYPES]


def node_to_test_info(node) -> TestInfo:
    """
    Returns the test info of the current node item.
    """
    return TestInfo(
        name=node.name,
        id=node.nodeid,
        original_name=node.originalname,
        path=Path(node.path),
    )


@pytest.fixture(scope="function")
def fixture_description(request):
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


def base_test_parametrizer(cls: Type[BaseTest]):
    """
    Generates a pytest.fixture for a given BaseTest subclass.

    Implementation detail: All spec fixtures must be scoped on test function level to avoid
    leakage between tests.
    """

    @pytest.fixture(
        scope="function",
        name=cls.pytest_parameter_name(),
    )
    def base_test_parametrizer_func(
        request: Any,
        fork: Fork,
        pre: Alloc,
        eips: List[int],
        eth_rpc: EthRPC,
        dump_dir_parameter_level,
        collector: Collector,
    ):
        """
        Fixture used to instantiate an auto-fillable BaseTest object from within
        a test function.

        Every test that defines a test filler must explicitly specify its parameter name
        (see `pytest_parameter_name` in each implementation of BaseTest) in its function
        arguments.

        When parametrize, indirect must be used along with the fixture format as value.
        """
        execute_format = request.param
        assert isinstance(execute_format, ExecuteFormats)

        class BaseTestWrapper(cls):  # type: ignore
            def __init__(self, *args, **kwargs):
                kwargs["t8n_dump_dir"] = dump_dir_parameter_level
                if "pre" not in kwargs:
                    kwargs["pre"] = pre
                super(BaseTestWrapper, self).__init__(*args, **kwargs)

                # wait for pre-requisite transactions to be included in blocks
                pre.wait_for_transactions()

                execute = self.execute(fork=fork, execute_format=execute_format, eips=eips)
                execute.execute(eth_rpc)
                collector.collect(request.node.nodeid, execute)

                # Refund all EOAs
                refund_txs = []
                for eoa, seed_address in pre._funded_eoa:
                    remaining_balance = eth_rpc.get_balance(eoa)
                    eoa.nonce = eth_rpc.get_transaction_count(eoa)
                    refund_gas_limit = 21_000
                    refund_gas_price = 10**9
                    tx_cost = refund_gas_limit * refund_gas_price
                    if remaining_balance < tx_cost:
                        continue
                    refund_txs.append(
                        Transaction(
                            sender=eoa,
                            to=seed_address,
                            gas_limit=21_000,
                            gas_price=10**9,
                            value=remaining_balance - tx_cost,
                        ).with_signature_and_sender()
                    )
                eth_rpc.send_wait_transactions(refund_txs)

        return BaseTestWrapper

    return base_test_parametrizer_func


# Dynamically generate a pytest fixture for each test spec type.
for cls in SPEC_TYPES:
    # Fixture needs to be defined in the global scope so pytest can detect it.
    globals()[cls.pytest_parameter_name()] = base_test_parametrizer(cls)


def pytest_generate_tests(metafunc):
    """
    Pytest hook used to dynamically generate test cases for each fixture format a given
    test spec supports.
    """
    for test_type in SPEC_TYPES:
        if test_type.pytest_parameter_name() in metafunc.fixturenames:
            metafunc.parametrize(
                [test_type.pytest_parameter_name()],
                [
                    pytest.param(
                        execute_format,
                        id=execute_format.name.lower(),
                        marks=[getattr(pytest.mark, execute_format.name.lower())],
                    )
                    for execute_format in test_type.supported_execute_formats
                ],
                scope="function",
                indirect=True,
            )


def pytest_collection_modifyitems(config, items):
    """
    Remove pre-Paris tests parametrized to generate hive type fixtures; these
    can't be used in the Hive Pyspec Simulator.

    This can't be handled in this plugins pytest_generate_tests() as the fork
    parametrization occurs in the forks plugin.
    """
    for item in items[:]:  # use a copy of the list, as we'll be modifying it
        if isinstance(item, EIPSpecTestItem):
            continue
        if "fork" not in item.callspec.params or item.callspec.params["fork"] is None:
            items.remove(item)
            continue
        if item.callspec.params["fork"] < Paris:
            # Even though the `state_test` test spec does not produce a hive STATE_TEST, it does
            # produce a BLOCKCHAIN_TEST_HIVE, so we need to remove it here.
            # TODO: Ideally, the logic could be contained in the `FixtureFormat` class, we create
            # a `fork_supported` method that returns True if the fork is supported.
            if ("state_test" in item.callspec.params) and item.callspec.params[
                "state_test"
            ].name.endswith("HIVE"):
                items.remove(item)
            if ("blockchain_test" in item.callspec.params) and item.callspec.params[
                "blockchain_test"
            ].name.endswith("HIVE"):
                items.remove(item)
        if "yul" in item.fixturenames:
            item.add_marker(pytest.mark.yul_test)


def pytest_make_parametrize_id(config, val, argname):
    """
    Pytest hook called when generating test ids. We use this to generate
    more readable test ids for the generated tests.
    """
    return f"{argname}_{val}"


def pytest_runtest_call(item):
    """
    Pytest hook called in the context of test execution.
    """
    if isinstance(item, EIPSpecTestItem):
        return

    class InvalidFiller(Exception):
        def __init__(self, message):
            super().__init__(message)

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
