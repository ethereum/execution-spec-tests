"""
A pytest plugin providing common functionality for consuming test fixtures.
"""
import json
import sys
import tarfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal, Mapping, Optional, Union, get_args
from urllib.parse import urlparse

import pytest
import requests

from ethereum_test_tools.common.json import load_dataclass_from_json
from ethereum_test_tools.common.types import Fixture

from ..consume_via_rlp.network_ruleset_hive import ruleset

cached_downloads_directory = Path("./cached_downloads")


def is_url(string: str) -> bool:
    """
    Check if a string is a remote URL.
    """
    result = urlparse(string)
    return all([result.scheme, result.netloc])


def download_and_extract(url: str, base_directory: Path) -> Path:
    """
    Download the URL and extract it locally if it hasn't already been downloaded.
    """
    parsed_url = urlparse(url)
    # Extract filename and version from URL
    filename = Path(parsed_url.path).name
    version = Path(parsed_url.path).parts[-2]

    # Create unique directory path for this version
    extract_to = base_directory / version / filename.removesuffix(".tar.gz")

    if extract_to.exists():
        return extract_to

    extract_to.mkdir(parents=True, exist_ok=False)

    # Download and extract the archive
    response = requests.get(url)
    response.raise_for_status()

    archive_path = extract_to / filename
    with open(archive_path, "wb") as file:
        file.write(response.content)

    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=extract_to)

    return extract_to


def pytest_addoption(parser):  # noqa: D103
    consume_group = parser.getgroup(
        "consume", "Arguments related to consuming fixtures via a client"
    )
    consume_group.addoption(
        "--input",
        action="store",
        dest="fixture_directory",
        default="fixtures",
        help="A URL or local directory specifying the JSON test fixtures. Default: './fixtures'.",
    )


def generate_test_cases(fixtures_directory):  # noqa: D103
    test_cases = []

    if fixtures_directory == "stdin":
        test_cases.extend(create_test_cases_from_json("stdin"))
    else:
        fixtures_directory = Path(fixtures_directory)
        for json_file in fixtures_directory.glob("**/*.json"):
            test_cases.extend(create_test_cases_from_json(json_file))

    return test_cases


def pytest_configure(config):  # noqa: D103
    input_source = config.getoption("fixture_directory")
    if input_source != "stdin":
        download_directory = cached_downloads_directory

        if is_url(input_source):
            download_directory.mkdir(parents=True, exist_ok=True)
            input_source = download_and_extract(input_source, download_directory)

        input_source = Path(input_source)
        if not input_source.exists():
            pytest.exit(f"Specified fixture directory '{input_source}' does not exist.")
        if not any(input_source.glob("**/*.json")):
            pytest.exit(
                f"Specified fixture directory '{input_source}' does not contain any JSON files."
            )
        config.option.fixture_directory = input_source
    # We generate the list of test cases here, it need only be done once
    config.test_cases = generate_test_cases(config.option.fixture_directory)


def pytest_report_header(config):  # noqa: D103
    input_source = config.getoption("fixture_directory")
    return f"fixtures: {input_source}"


JsonSource = Union[Path, Literal["stdin"]]
ConsumerTypes = Literal["all", "direct", "rlp", "engine"]


@dataclass
class TestCase:  # noqa: D101
    """
    Define the test case data associated a JSON test fixture in blockchain test
    format.
    """

    @classmethod
    def _marks_default(cls):
        return {consumer_type: [] for consumer_type in get_args(ConsumerTypes)}

    fixture_name: str
    json_file: JsonSource
    json_as_dict: dict
    fixture: Optional[Fixture] = None
    fixture_json: Optional[dict] = field(default_factory=dict)
    marks: Mapping[ConsumerTypes, List[pytest.MarkDecorator]] = field(
        default_factory=lambda: TestCase._marks_default()
    )
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
            self.marks["rlp"].append(pytest.mark.xfail(reason="Missing block header", run=False))
            self.marks["engine"].append(
                pytest.mark.xfail(reason="Missing block header", run=False)
            )
        if self.fixture.fork not in ruleset:
            self.marks["rlp"].append(
                pytest.mark.xfail(reason=f"Unsupported network '{self.fixture.fork}'", run=False)
            )


def create_test_cases_from_json(json_file: JsonSource) -> List[TestCase]:
    """
    Extract blockchain test cases from a JSON file or from stdin.
    """
    test_cases = []

    # TODO: exception handling?
    if json_file == "stdin":
        json_data = json.load(sys.stdin)
    else:
        with open(json_file, "r") as file:
            json_data = json.load(file)

    for fixture_name, fixture_data in json_data.items():
        fixture = None

        marks: List[pytest.MarkDecorator]
        try:
            # TODO: here we validate fixture.blocks, for example, but not nested fields. Can we?
            # Or should we? (it'll be brittle).
            fixture = load_dataclass_from_json(Fixture, fixture_data)
            fixture_json = {fixture_name: fixture_data}
            marks = []
        except Exception as e:
            # TODO: Add logger.error() entry here
            reason = f"Error creating test case {fixture_name} from {json_file}: {e}"
            fixture = None
            fixture_json = None
            marks = [pytest.mark.xfail(reason=reason, run=False)]

        test_case = TestCase(
            json_file=json_file,
            json_as_dict=fixture_data,
            fixture_name=fixture_name,
            fixture=fixture,
            fixture_json=fixture_json,
        )
        test_case.marks["all"].extend(marks)
        test_cases.append(test_case)

    return test_cases


@pytest.fixture(scope="function")
def test_case_fixture(test_case: TestCase) -> Fixture:
    """
    The test fixture as a dictionary. If we failed to parse a test case fixture,
    it's None: We xfail/skip the test.
    """
    assert test_case.fixture is not None
    return test_case.fixture


def pytest_generate_tests(metafunc):
    """
    Generate test cases for every test fixture in all the JSON fixture files
    within the specified fixtures directory, or read from stdin if the directory is 'stdin'.
    """
    test_cases = metafunc.config.test_cases
    if "test_blocktest" in metafunc.function.__name__:
        pytest_params = [
            pytest.param(
                test_case,
                id=test_case.fixture_name,
                marks=test_case.marks["all"] + test_case.marks["direct"],
            )
            for test_case in test_cases
        ]
        metafunc.parametrize("test_case", pytest_params)

    if "test_via_rlp" in metafunc.function.__name__:
        pytest_params = [
            pytest.param(
                test_case,
                id=test_case.fixture_name,
                marks=test_case.marks["all"] + test_case.marks["rlp"],
            )
            for test_case in test_cases
        ]
        metafunc.parametrize("test_case", pytest_params)

    if "test_via_engine" in metafunc.function.__name__:
        pytest_params = [
            pytest.param(
                test_case,
                id=test_case.fixture_name,
                marks=test_case.marks["all"] + test_case.marks["engine"],
            )
            for test_case in test_cases
        ]
        metafunc.parametrize("test_case", pytest_params)

    if "client_type" in metafunc.fixturenames:
        client_ids = [client.name for client in metafunc.config.hive_execution_clients]
        metafunc.parametrize("client_type", metafunc.config.hive_execution_clients, ids=client_ids)
