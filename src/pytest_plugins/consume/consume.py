"""
A pytest plugin providing common functionality for consuming test fixtures.
"""

import sys
import tarfile
from pathlib import Path
from typing import Literal, Union
from urllib.parse import urlparse

import pytest
import requests
import rich

from cli.gen_index import generate_fixtures_index
from ethereum_test_tools.spec.consume.types import TestCases
from evm_transition_tool import FixtureFormats

cached_downloads_directory = Path("./cached_downloads")

JsonSource = Union[Path, Literal["stdin"]]


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
        dest="fixture_source",
        default="fixtures",
        help="A URL or local directory specifying the JSON test fixtures. Default: './fixtures'.",
    )


def pytest_configure(config):  # noqa: D103
    input_source = config.getoption("fixture_source")
    if input_source == "stdin":
        config.test_cases = TestCases.from_stream(sys.stdin)
        return

    if is_url(input_source):
        cached_downloads_directory.mkdir(parents=True, exist_ok=True)
        input_source = download_and_extract(input_source, cached_downloads_directory)
        config.option.fixture_source = input_source

    input_source = Path(input_source)
    if not input_source.exists():
        pytest.exit(f"Specified fixture directory '{input_source}' does not exist.")
    if not any(input_source.glob("**/*.json")):
        pytest.exit(
            f"Specified fixture directory '{input_source}' does not contain any JSON files."
        )

    index_file = input_source / "index.json"
    if not index_file.exists():
        rich.print(f"Generating index file [bold cyan]{index_file}[/]...")
    generate_fixtures_index(
        Path(input_source), quiet_mode=False, force_flag=False, disable_infer_format=False
    )
    config.test_cases = TestCases.from_index_file(Path(input_source) / "index.json")


def pytest_report_header(config):  # noqa: D103
    input_source = config.getoption("fixture_source")
    return f"fixtures: {input_source}"


@pytest.fixture(scope="function")
def fixture_source(request) -> JsonSource:  # noqa: D103
    return request.config.getoption("fixture_source")


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
                id=test_case.id,
                # marks=test_case.marks["all"] + test_case.marks["direct"],
            )
            for test_case in test_cases
            if test_case.format == FixtureFormats.BLOCKCHAIN_TEST
        ]
        metafunc.parametrize("test_case", pytest_params)

    if "test_statetest" in metafunc.function.__name__:
        pytest_params = [
            pytest.param(
                test_case,
                id=test_case.id,
                # marks=test_case.marks["all"] + test_case.marks["direct"],
            )
            for test_case in test_cases
            if test_case.format == FixtureFormats.STATE_TEST
        ]
        metafunc.parametrize("test_case", pytest_params)

    if "test_via_rlp" in metafunc.function.__name__:
        pytest_params = [
            pytest.param(
                test_case,
                id=test_case.id,
                # marks=test_case.marks["all"] + test_case.marks["rlp"],
            )
            for test_case in test_cases
            if test_case.format == FixtureFormats.BLOCKCHAIN_TEST
        ]
        metafunc.parametrize("test_case", pytest_params)

    if "test_via_engine" in metafunc.function.__name__:
        pytest_params = [
            pytest.param(
                test_case,
                id=test_case.id,
                # marks=test_case.marks["all"] + test_case.marks["engine"],
            )
            for test_case in test_cases
        ]
        metafunc.parametrize("test_case", pytest_params)

    if "client_type" in metafunc.fixturenames:
        client_ids = [client.name for client in metafunc.config.hive_execution_clients]
        metafunc.parametrize("client_type", metafunc.config.hive_execution_clients, ids=client_ids)
