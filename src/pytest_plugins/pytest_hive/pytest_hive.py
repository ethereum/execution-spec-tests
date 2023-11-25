"""
A pytest plugin providing common functionality for Hive simulators.

Simulators using this plugin must define two pytest fixtures:

1. `test_suite_name`: The name of the test suite.
2. `test_suite_description`: The description of the test suite.

These fixtures are used when creating the hive test suite.
"""
import os

import pytest
from hive.client import ClientRole
from hive.simulation import Simulation


@pytest.fixture(scope="session")
def simulator(request):  # noqa: D103
    return request.config.hive_simulator


@pytest.fixture(scope="session")
def test_suite(request, simulator: Simulation):
    """
    Defines a Hive test suite and cleans up after all tests have run.
    """
    try:
        test_suite_name = request.getfixturevalue("test_suite_name")
        test_suite_description = request.getfixturevalue("test_suite_description")
    except pytest.FixtureLookupError:
        pytest.exit(
            "Error: The 'test_suite_name' and 'test_suite_description' fixtures are not defined "
            "by the hive simulator pytest plugin using this ('test_suite') fixture!"
        )

    suite = simulator.start_suite(name=test_suite_name, description=test_suite_description)
    # TODO: Can we share this fixture across all nodes using xdist? Hive uses different suites.
    yield suite
    suite.end()


def pytest_configure(config):  # noqa: D103
    if config.option.collectonly:
        return
    hive_simulator_url = os.environ.get("HIVE_SIMULATOR")
    if hive_simulator_url is None:
        pytest.exit(
            "The HIVE_SIMULATOR environment variable is not set.\n\n"
            "If running locally, start hive in --dev mode, for example:\n"
            "./hive --dev --client go-ethereum\n\n"
            "and set the HIVE_SIMULATOR to the reported URL. For example, in bash:\n"
            "export HIVE_SIMULATOR=http://127.0.0.1:3000\n"
            "or in fish:\n"
            "set -x HIVE_SIMULATOR http://127.0.0.1:3000"
        )
    # TODO: Try and get these into fixtures; this is only here due to the "dynamic" parametrization
    # of client_type with hive_execution_clients.
    config.hive_simulator_url = hive_simulator_url
    config.hive_simulator = Simulation(url=hive_simulator_url)
    config.hive_execution_clients = config.hive_simulator.client_types(
        role=ClientRole.ExecutionClient
    )


@pytest.hookimpl(trylast=True)
def pytest_report_header(config, start_path):
    """
    Add lines to pytest's console output header.
    """
    if config.option.collectonly:
        return
    return [f"hive simulator: {config.hive_simulator_url}"]
