"""
A hive simulator that feeds test fixtures to clients as RLP-encoded blocks
upon start-up.

Implemented using the pytest framework as a pytest plugin.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Tuple

import pytest

from ethereum_test_tools.common.types import Fixture, load_dataclass_from_json

from .network_ruleset_hive import ruleset


@pytest.fixture(scope="session")
def test_suite_name() -> str:
    """
    The name of the hive test suite used in this simulator.
    """
    return "EEST Consume Blocks via RLP"


@pytest.fixture(scope="session")
def test_suite_description() -> str:
    """
    The description of the hive test suite used in this simulator.
    """
    return "Execute blockchain tests by providing RLP-encoded blocks to a client upon start-up."


@dataclass
class TestCase:  # noqa: D101
    """
    Define the test case data associated a JSON test fixture in blockchain test
    format.
    """

    fixture_name: str
    json_file_path: Path
    json_as_dict: dict
    fixture: Optional[Fixture] = None
    marks: List[pytest.MarkDecorator] = field(default_factory=list)
    __test__ = False  # stop pytest from collecting this dataclass as a test

    def __post_init__(self):
        """
        Sanity check the loaded test-case and add pytest marks.

        Marks can be applied based on any issues detected with the fixture. In
        the future, we can apply marks that were written into the json fixture
        file from `fill`.
        """
        if any(mark is pytest.mark.xfail for mark in self.marks):
            return  # no point continuing
        if not all("blockHeader" in block for block in self.fixture.blocks):
            print("Skipping fixture with missing block header", self.fixture_name)
            self.marks.append(pytest.mark.xfail(reason="Missing block header", run=False))
        if self.fixture.fork not in ruleset:
            self.marks.append(
                pytest.mark.xfail(reason=f"Unsupported network '{self.fixture.fork}'", run=False)
            )


def create_test_cases_from_json(json_file_path: Path) -> Tuple[List[Any], List[str]]:
    """
    Extract blockchain test cases from a JSON fixture file.
    """
    test_cases = []
    test_case_ids = []
    # TODO: Consider try-except block here
    with open(json_file_path, "r") as file:
        json_data = json.load(file)

    for fixture_name, fixture_data in json_data.items():
        fixture = None
        marks = []

        try:
            # TODO: here we validate fixture.blocks, for example, but not nested fields. Can we?
            # Or should we? (it'll be brittle).
            fixture = load_dataclass_from_json(Fixture, fixture_data)
        except Exception as e:
            reason = f"Error creating test case {fixture_name} from {json_file_path}: {e}"
            # TODO: Add logger.error() entry here
            marks.append(pytest.mark.xfail(reason=reason, run=False))

        test_case = TestCase(
            json_file_path=json_file_path,
            json_as_dict=fixture_data,
            fixture_name=fixture_name,
            fixture=fixture,
            marks=marks,
        )
        test_cases.append(pytest.param(test_case, marks=test_case.marks))

        if "::.py" in fixture_name:  # new format; fixture name if fill pytest node id
            test_case_ids.append(str(fixture_name))
        else:  # old format, pre v1.0.7
            test_case_ids.append(f"{json_file_path.name}_{str(fixture_name)}")

    return test_cases, test_case_ids


def pytest_generate_tests(metafunc):
    """
    Generate test cases for every test fixture in all the JSON fixture files
    within the specified fixtures directory.
    """
    fixtures_directory = metafunc.config.getoption("fixture_directory")
    test_cases: List[TestCase] = []
    test_case_ids: List[str] = []
    for json_file in fixtures_directory.glob("**/*.json"):
        cases, ids = create_test_cases_from_json(json_file)
        test_cases.extend(cases)
        test_case_ids.extend(ids)
    metafunc.parametrize("test_case", test_cases, ids=test_case_ids)
    if "client_type" in metafunc.fixturenames:
        client_ids = [client.name for client in metafunc.config.hive_execution_clients]
        metafunc.parametrize("client_type", metafunc.config.hive_execution_clients, ids=client_ids)
