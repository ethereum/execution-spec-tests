"""
A pytest plugin providing common functionality for consuming test fixtures.
"""
import tarfile
from pathlib import Path
from urllib.parse import urlparse

import pytest
import requests

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


def pytest_configure(config):  # noqa: D103
    input_source = config.getoption("fixture_directory")
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


def pytest_report_header(config):  # noqa: D103
    input_source = config.getoption("fixture_directory")
    return f"fixtures: {input_source}"
