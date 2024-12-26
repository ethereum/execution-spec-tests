"""A pytest plugin providing common functionality for consuming test fixtures."""

import os
import sys
import tarfile
from io import BytesIO
from pathlib import Path
from typing import List, Literal, Union
from urllib.parse import urlparse

import platformdirs
import pytest
import requests
import rich

from cli.gen_index import generate_fixtures_index
from ethereum_test_fixtures.consume import TestCases
from ethereum_test_tools.utility.versioning import get_current_commit_hash_or_tag

from .releases import get_release_url

CACHED_DOWNLOADS_DIRECTORY = (
    Path(platformdirs.user_cache_dir("ethereum-execution-spec-tests")) / "cached_downloads"
)

JsonSource = Union[Path, Literal["stdin"]]


def default_input_directory() -> str:
    """
    Directory (default) to consume generated test fixtures from. Defined as a
    function to allow for easier testing.
    """
    return "./fixtures"


def default_html_report_file_path() -> str:
    """
    Filepath (default) to store the generated HTML test report. Defined as a
    function to allow for easier testing.
    """
    return ".meta/report_consume.html"


def is_url(string: str) -> bool:
    """Check if a string is a remote URL."""
    result = urlparse(string)
    return all([result.scheme, result.netloc])


def download_and_extract(url: str, base_directory: Path) -> Path:
    """Download the URL and extract it locally if it hasn't already been downloaded."""
    parsed_url = urlparse(url)
    filename = Path(parsed_url.path).name
    version = Path(parsed_url.path).parts[-2]
    extract_to = base_directory / version / filename.removesuffix(".tar.gz")

    if extract_to.exists():
        # skip download if the archive has already been downloaded
        return extract_to / "fixtures"

    extract_to.mkdir(parents=True, exist_ok=False)
    response = requests.get(url)
    response.raise_for_status()

    with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as tar:  # noqa: SC200
        tar.extractall(path=extract_to)

    return extract_to / "fixtures"


def pytest_addoption(parser):  # noqa: D103
    consume_group = parser.getgroup(
        "consume", "Arguments related to consuming fixtures via a client"
    )
    consume_group.addoption(
        "--input",
        action="store",
        dest="fixture_source",
        default=None,
        help=(
            "Specify the JSON test fixtures source. Can be a local directory, a URL pointing to a "
            " fixtures.tar.gz archive, or one of the special keywords: 'stdin', "
            "'latest-stable', 'latest-develop'. "
            f"Defaults to the following local directory: '{default_input_directory()}'."
        ),
    )
    consume_group.addoption(
        "--release",
        action="store",
        dest="fixture_release",
        default=None,
        help=(
            "Specify the name and, optionally, the version of the release to use as JSON test"
            " fixtures source."
            "If a specific version is not provided (e.g. RELEASE_NAME@v1.2.3), the latest release"
            " will be used."
            "Release names `stable` and `develop` are supported, as well as devnet-named releases."
        ),
    )
    consume_group.addoption(
        "--fork",
        action="store",
        dest="single_fork",
        default=None,
        help="Only consume tests for the specified fork.",
    )
    consume_group.addoption(
        "--no-html",
        action="store_true",
        dest="disable_html",
        default=False,
        help=(
            "Don't generate an HTML test report (in the output directory). "
            "The --html flag can be used to specify a different path."
        ),
    )
    consume_group.addoption(
        "--cache-folder",
        action="store",
        dest="fixture_cache_folder",
        default=CACHED_DOWNLOADS_DIRECTORY,
        help=(
            "Specify the path where the downloaded fixtures should be cached. "
            f"Defaults to the following directory: '{CACHED_DOWNLOADS_DIRECTORY}'."
        ),
    )
    consume_group.addoption(
        "--cache-only",
        action="store_true",
        dest="cache_only",
        default=False,
        help=("Do not run any tests, only cache the fixtures. "),
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):  # noqa: D103
    """
    Pytest hook called after command line options have been parsed and before
    test collection begins.

    `@pytest.hookimpl(tryfirst=True)` is applied to ensure that this hook is
    called before the pytest-html plugin's pytest_configure to ensure that
    it uses the modified `htmlpath` option.
    """
    input_source = config.getoption("fixture_source")
    release_source = config.getoption("fixture_release")
    cached_downloads_directory = Path(config.getoption("fixture_cache_folder"))

    if input_source is not None and input_source == "stdin":
        config.fixture_source_flags = ["--input=stdin"]
        config.test_cases = TestCases.from_stream(sys.stdin)
        config.input_source = "stdin"
        return

    if release_source is not None:
        config.fixture_source_flags = ["--release", release_source]
        input_source = get_release_url(release_source)
    elif input_source is not None:
        config.fixture_source_flags = ["--input", input_source]
    else:
        config.fixture_source_flags = []
        input_source = default_input_directory()

    if is_url(input_source):
        cached_downloads_directory.mkdir(parents=True, exist_ok=True)
        input_source = download_and_extract(input_source, cached_downloads_directory)

    input_source = Path(input_source)
    config.input_source = input_source
    if not input_source.exists():
        pytest.exit(f"Specified fixture directory '{input_source}' does not exist.")
    if not any(input_source.glob("**/*.json")):
        pytest.exit(
            f"Specified fixture directory '{input_source}' does not contain any JSON files."
        )

    index_file = input_source / ".meta" / "index.json"
    index_file.parent.mkdir(parents=True, exist_ok=True)
    if not index_file.exists():
        rich.print(f"Generating index file [bold cyan]{index_file}[/]...")
        generate_fixtures_index(
            input_source, quiet_mode=False, force_flag=False, disable_infer_format=False
        )
    config.test_cases = TestCases.from_index_file(index_file)

    if config.option.collectonly:
        return
    if not config.getoption("disable_html") and config.getoption("htmlpath") is None:
        # generate an html report by default, unless explicitly disabled
        config.option.htmlpath = os.path.join(input_source, default_html_report_file_path())


def pytest_html_report_title(report):
    """Set the HTML report title (pytest-html plugin)."""
    report.title = "Consume Test Report"


def pytest_report_header(config):  # noqa: D103
    consume_version = f"consume commit: {get_current_commit_hash_or_tag()}"
    input_source = f"fixtures: {config.input_source}"
    return [consume_version, input_source]


@pytest.fixture(scope="session")
def fixture_source_flags(request) -> List[str]:
    """
    Returns the input flags used to specify the JSON test fixtures source.
    """
    return request.config.fixture_source_flags


@pytest.fixture(scope="session")
def fixture_source(request) -> JsonSource:  # noqa: D103
    return request.config.input_source


def pytest_generate_tests(metafunc):
    """
    Generate test cases for every test fixture in all the JSON fixture files
    within the specified fixtures directory, or read from stdin if the directory is 'stdin'.
    """
    if metafunc.config.getoption("cache_only"):
        return

    fork = metafunc.config.getoption("single_fork")
    metafunc.parametrize(
        "test_case",
        (
            pytest.param(test_case, id=test_case.id)
            for test_case in metafunc.config.test_cases
            if test_case.format in metafunc.function.fixture_format
            and (not fork or test_case.fork == fork)
        ),
    )

    if "client_type" in metafunc.fixturenames:
        client_ids = [client.name for client in metafunc.config.hive_execution_clients]
        metafunc.parametrize("client_type", metafunc.config.hive_execution_clients, ids=client_ids)


def pytest_collection_modifyitems(session, config, items):
    """Modify collected item names to remove the test runner function from the name."""
    for item in items:
        original_name = item.originalname
        remove = f"{original_name}["
        if item.name.startswith(remove):
            item.name = item.name[len(remove) : -1]
