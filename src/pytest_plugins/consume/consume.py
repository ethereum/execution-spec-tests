"""
A pytest plugin providing common functionality for consuming test fixtures.

Features:
- Downloads and caches test fixtures from various sources (local, URL, release).
- Manages test case generation from fixture files.
- Provides xdist load balancing for large pre-allocation groups (enginex simulator).
"""

import logging
import re
import sys
import tarfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import platformdirs
import pytest
import requests
import rich

from cli.gen_index import generate_fixtures_index
from ethereum_test_fixtures import BaseFixture
from ethereum_test_fixtures.consume import IndexFile, TestCases
from ethereum_test_forks import get_forks, get_relative_fork_markers, get_transition_forks
from ethereum_test_tools.utility.versioning import get_current_commit_hash_or_tag

from .releases import ReleaseTag, get_release_page_url, get_release_url, is_release_url, is_url

logger = logging.getLogger(__name__)

CACHED_DOWNLOADS_DIRECTORY = (
    Path(platformdirs.user_cache_dir("ethereum-execution-spec-tests")) / "cached_downloads"
)


class XDistGroupMapper:
    """
    Maps test cases to xdist groups, splitting large pre-allocation groups into sub-groups.

    This class helps improve load balancing when using pytest-xdist with --dist=loadgroup
    by breaking up large pre-allocation groups (e.g., 1000+ tests) into smaller virtual
    sub-groups while maintaining the constraint that tests from the same pre-allocation
    group must run on the same worker.
    """

    def __init__(self, max_group_size: int = 100):
        """Initialize the mapper with a maximum group size."""
        self.max_group_size = max_group_size
        self.group_sizes: Dict[str, int] = {}
        self.test_to_subgroup: Dict[str, int] = {}
        self._built = False

    def build_mapping(self, test_cases: TestCases) -> None:
        """
        Build the mapping of test cases to sub-groups.

        This analyzes all test cases and determines which pre-allocation groups
        need to be split into sub-groups based on the max_group_size.
        """
        if self._built:
            return

        # Count tests per pre-allocation group
        for test_case in test_cases:
            if hasattr(test_case, "pre_hash") and test_case.pre_hash:
                pre_hash = test_case.pre_hash
                self.group_sizes[pre_hash] = self.group_sizes.get(pre_hash, 0) + 1

        # Assign sub-groups for large groups
        group_counters: Dict[str, int] = {}
        for test_case in test_cases:
            if hasattr(test_case, "pre_hash") and test_case.pre_hash:
                pre_hash = test_case.pre_hash
                group_size = self.group_sizes[pre_hash]

                if group_size <= self.max_group_size:
                    # Small group, no sub-group needed
                    self.test_to_subgroup[test_case.id] = 0
                else:
                    # Large group, assign to sub-group using round-robin
                    counter = group_counters.get(pre_hash, 0)
                    sub_group = counter // self.max_group_size
                    self.test_to_subgroup[test_case.id] = sub_group
                    group_counters[pre_hash] = counter + 1

        self._built = True

        # Log summary of large groups
        large_groups = [
            (pre_hash, size)
            for pre_hash, size in self.group_sizes.items()
            if size > self.max_group_size
        ]
        if large_groups:
            logger.info(
                f"Found {len(large_groups)} pre-allocation groups larger than "
                f"{self.max_group_size} tests that will be split for better load balancing"
            )

    def get_xdist_group_name(self, test_case) -> str:
        """
        Get the xdist group name for a test case.

        For small groups, returns the pre_hash as-is.
        For large groups, returns "{pre_hash}:{sub_group_index}".
        """
        if not hasattr(test_case, "pre_hash") or not test_case.pre_hash:
            # No pre_hash, use test ID as fallback
            return test_case.id

        pre_hash = test_case.pre_hash
        group_size = self.group_sizes.get(pre_hash, 0)

        if group_size <= self.max_group_size:
            # Small group, use pre_hash as-is
            return pre_hash

        # Large group, include sub-group index
        sub_group = self.test_to_subgroup.get(test_case.id, 0)
        return f"{pre_hash}:{sub_group}"

    def get_split_statistics(self) -> Dict[str, Dict[str, int]]:
        """
        Get statistics about how groups were split.

        Returns a dict with information about each pre-allocation group
        and how many sub-groups it was split into.
        """
        stats = {}
        for pre_hash, size in self.group_sizes.items():
            if size > self.max_group_size:
                num_subgroups = (size + self.max_group_size - 1) // self.max_group_size
                stats[pre_hash] = {
                    "total_tests": size,
                    "num_subgroups": num_subgroups,
                    "average_tests_per_subgroup": size // num_subgroups,
                }
        return stats


def default_input() -> str:
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


class FixtureDownloader:
    """Handles downloading and extracting fixture archives."""

    def __init__(self, url: str, destination_folder: Path):  # noqa: D107
        self.url = url
        self.destination_folder = destination_folder
        self.parsed_url = urlparse(url)
        self.archive_name = self.strip_archive_extension(Path(self.parsed_url.path).name)

    def download_and_extract(self) -> Tuple[bool, Path]:
        """Download the URL and extract it locally if it hasn't already been downloaded."""
        if self.destination_folder.exists():
            return True, self.detect_extracted_directory()

        return False, self.fetch_and_extract()

    @staticmethod
    def strip_archive_extension(filename: str) -> str:
        """Remove .tar.gz or .tgz extensions from filename."""
        return filename.removesuffix(".tar.gz").removesuffix(".tgz")

    @staticmethod
    def get_cache_path(url: str, cache_folder: Path) -> Path:
        """Get the appropriate cache path for a given URL."""
        parsed_url = urlparse(url)
        archive_name = FixtureDownloader.strip_archive_extension(Path(parsed_url.path).name)

        if is_release_url(url):
            version = Path(parsed_url.path).parts[-2]
            parts = parsed_url.path.strip("/").split("/")
            org_repo = (
                f"{parts[0]}/{parts[1]}"
                if parsed_url.netloc == "github.com" and len(parts) >= 2
                else "other"
            )
            return cache_folder / org_repo / version / archive_name
        return cache_folder / "other" / archive_name

    def fetch_and_extract(self) -> Path:
        """Download and extract an archive from the given URL."""
        self.destination_folder.mkdir(parents=True, exist_ok=True)
        response = requests.get(self.url)
        response.raise_for_status()

        with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as tar:
            tar.extractall(path=self.destination_folder)

        return self.detect_extracted_directory()

    def detect_extracted_directory(self) -> Path:
        """
        Detect a single top-level dir within the extracted archive, otherwise return
        destination_folder.
        """  # noqa: D200
        extracted_dirs = [
            d for d in self.destination_folder.iterdir() if d.is_dir() and d.name != ".meta"
        ]
        return extracted_dirs[0] if len(extracted_dirs) == 1 else self.destination_folder


@dataclass
class FixturesSource:
    """Represents the source of test fixtures."""

    input_option: str
    path: Path
    url: str = ""
    release_page: str = ""
    is_local: bool = True
    is_stdin: bool = False
    was_cached: bool = False
    extract_to_local_path: bool = False

    @classmethod
    def from_input(
        cls,
        input_source: str,
        cache_folder: Optional[Path] = None,
        extract_to: Optional[Path] = None,
    ) -> "FixturesSource":
        """Determine the fixture source type and return an instance."""
        if cache_folder is None:
            cache_folder = CACHED_DOWNLOADS_DIRECTORY
        if input_source == "stdin":
            return cls(input_option=input_source, path=Path(), is_local=False, is_stdin=True)
        if is_release_url(input_source):
            return cls.from_release_url(input_source, cache_folder, extract_to)
        if is_url(input_source):
            return cls.from_url(input_source, cache_folder, extract_to)
        if ReleaseTag.is_release_string(input_source):
            return cls.from_release_spec(input_source, cache_folder, extract_to)
        return cls.validate_local_path(Path(input_source))

    @classmethod
    def from_release_url(
        cls, url: str, cache_folder: Optional[Path] = None, extract_to: Optional[Path] = None
    ) -> "FixturesSource":
        """Create a fixture source from a supported github repo release URL."""
        if cache_folder is None:
            cache_folder = CACHED_DOWNLOADS_DIRECTORY

        destination_folder = extract_to or FixtureDownloader.get_cache_path(url, cache_folder)
        downloader = FixtureDownloader(url, destination_folder)

        # Skip cache check for extract_to (always download fresh)
        if extract_to is not None:
            was_cached = False
            path = downloader.fetch_and_extract()
        else:
            was_cached, path = downloader.download_and_extract()

        return cls(
            input_option=url,
            path=path,
            url=url,
            release_page="",
            is_local=False,
            was_cached=was_cached,
            extract_to_local_path=extract_to is not None,
        )

    @classmethod
    def from_url(
        cls, url: str, cache_folder: Optional[Path] = None, extract_to: Optional[Path] = None
    ) -> "FixturesSource":
        """Create a fixture source from a direct URL."""
        if cache_folder is None:
            cache_folder = CACHED_DOWNLOADS_DIRECTORY

        destination_folder = extract_to or FixtureDownloader.get_cache_path(url, cache_folder)
        downloader = FixtureDownloader(url, destination_folder)

        # Skip cache check for extract_to (always download fresh)
        if extract_to is not None:
            was_cached = False
            path = downloader.fetch_and_extract()
        else:
            was_cached, path = downloader.download_and_extract()

        return cls(
            input_option=url,
            path=path,
            url=url,
            release_page="",
            is_local=False,
            was_cached=was_cached,
            extract_to_local_path=extract_to is not None,
        )

    @classmethod
    def from_release_spec(
        cls, spec: str, cache_folder: Optional[Path] = None, extract_to: Optional[Path] = None
    ) -> "FixturesSource":
        """Create a fixture source from a release spec (e.g., develop@latest)."""
        if cache_folder is None:
            cache_folder = CACHED_DOWNLOADS_DIRECTORY
        url = get_release_url(spec)
        release_page = get_release_page_url(url)

        destination_folder = extract_to or FixtureDownloader.get_cache_path(url, cache_folder)
        downloader = FixtureDownloader(url, destination_folder)

        # Skip cache check for extract_to (always download fresh)
        if extract_to is not None:
            was_cached = False
            path = downloader.fetch_and_extract()
        else:
            was_cached, path = downloader.download_and_extract()

        return cls(
            input_option=spec,
            path=path,
            url=url,
            release_page=release_page,
            is_local=False,
            was_cached=was_cached,
            extract_to_local_path=extract_to is not None,
        )

    @staticmethod
    def validate_local_path(path: Path) -> "FixturesSource":
        """Validate that a local fixture path exists and contains JSON files."""
        if not path.exists():
            pytest.exit(f"Specified fixture directory '{path}' does not exist.")
        if not any(path.glob("**/*.json")):
            pytest.exit(f"Specified fixture directory '{path}' does not contain any JSON files.")
        return FixturesSource(input_option=str(path), path=path)


class SimLimitBehavior:
    """Represents options derived from the `--sim.limit` argument."""

    def __init__(self, pattern: str, collectonly: bool = False):  # noqa: D107
        self.pattern = pattern
        self.collectonly = collectonly

    @staticmethod
    def _escape_id(pattern: str) -> str:
        """
        Escape regex char in the pattern; prepend and append '.*' (for `fill` IDs).

        The `pattern` is prefixed and suffixed with a wildcard match to allow `fill`
        test case IDs to be specified, otherwise the full `consume` test ID must be
        specified.
        """
        return f".*{re.escape(pattern)}.*"

    @classmethod
    def from_string(cls, pattern: str) -> "SimLimitBehavior":
        """
        Parse the `--sim.limit` argument and return a `SimLimitBehavior` instance.

        If `pattern`:
        - Is "collectonly", enable collection mode without filtering.
        - Starts with "collectonly:", enable collection mode and use the rest as a regex pattern.
        - Starts with "id:", treat the rest as a literal test ID and escape special regex chars.
        - Starts with "collectonly:id:", enable collection mode with a literal test ID.
        """
        if pattern == "collectonly":
            return cls(pattern=".*", collectonly=True)

        if pattern.startswith("collectonly:id:"):
            literal_id = pattern.removeprefix("collectonly:id:")
            if not literal_id:
                raise ValueError("Empty literal ID provided.")
            return cls(pattern=cls._escape_id(literal_id), collectonly=True)

        if pattern.startswith("collectonly:"):
            return cls(pattern=pattern.removeprefix("collectonly:"), collectonly=True)

        if pattern.startswith("id:"):
            literal_id = pattern.removeprefix("id:")
            if not literal_id:
                raise ValueError("Empty literal ID provided.")
            return cls(pattern=cls._escape_id(literal_id))

        return cls(pattern=pattern)


def pytest_addoption(parser):  # noqa: D103
    consume_group = parser.getgroup(
        "consume", "Arguments related to consuming fixtures via a client"
    )
    consume_group.addoption(
        "--input",
        action="store",
        dest="fixtures_source",
        default=None,
        help=(
            "Specify the JSON test fixtures source. Can be a local directory, a URL pointing to a "
            " fixtures.tar.gz archive, a release name and version in the form of `NAME@v1.2.3` "
            "(`stable` and `develop` are valid release names, and `latest` is a valid version), "
            "or the special keyword 'stdin'. "
            f"Defaults to the following local directory: '{default_input()}'."
        ),
    )
    consume_group.addoption(
        "--cache-folder",
        action="store",
        dest="fixture_cache_folder",
        default=CACHED_DOWNLOADS_DIRECTORY,
        help=(
            "Specify the path where the downloaded fixtures are cached. "
            f"Defaults to the following directory: '{CACHED_DOWNLOADS_DIRECTORY}'."
        ),
    )
    consume_group.addoption(
        "--extract-to",
        action="store",
        dest="extract_to_folder",
        default=None,
        help=(
            "Extract downloaded fixtures to the specified directory. Only valid with 'cache' "
            "command. When used, fixtures are extracted directly to this path instead of the "
            "user's execution-spec-tests cache directory."
        ),
    )
    if "cache" in sys.argv:
        return
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
        "--sim.limit",
        action="store",
        dest="sim_limit",
        type=SimLimitBehavior.from_string,
        default=SimLimitBehavior(".*"),
        help=(
            "Filter tests by either a regex pattern or a literal test case ID. To match a "
            "test case by its exact ID, prefix the ID with `id:`. The string following `id:` "
            "will be automatically escaped so that all special regex characters are treated as "
            "literals. Without the `id:` prefix, the argument is interpreted as a Python regex "
            "pattern. To see which test cases are matched, without executing them, prefix with "
            '`collectonly:`, e.g. `--sim.limit "collectonly:.*eip4788.*fork_Prague.*"`. '
            "To list all available test case IDs, set the value to `collectonly`."
        ),
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
    # Validate --extract-to usage
    if config.option.extract_to_folder is not None and "cache" not in sys.argv:
        pytest.exit("The --extract-to flag is only valid with the 'cache' command.")

    if config.option.fixtures_source is None:
        # NOTE: Setting the default value here is necessary for correct stdin/piping behavior.
        config.fixtures_source = FixturesSource(
            input_option=default_input(), path=Path(default_input())
        )
    else:
        # NOTE: Setting `type=FixturesSource.from_input` in pytest_addoption() causes the option to
        # be evaluated twice which breaks the result of `was_cached`; the work-around is to call it
        # manually here.
        config.fixtures_source = FixturesSource.from_input(
            config.option.fixtures_source,
            Path(config.option.fixture_cache_folder),
            Path(config.option.extract_to_folder)
            if config.option.extract_to_folder is not None
            else None,
        )
    config.fixture_source_flags = ["--input", config.fixtures_source.input_option]

    if "cache" in sys.argv and not config.fixtures_source:
        pytest.exit("The --input flag is required when using the cache command.")

    if "cache" in sys.argv:
        reason = ""
        if config.fixtures_source.extract_to_local_path:
            reason += "Fixtures downloaded and extracted to specified directory."
        elif config.fixtures_source.was_cached:
            reason += "Fixtures already cached."
        elif not config.fixtures_source.is_local:
            reason += "Fixtures downloaded and cached."
        reason += f"\nPath: {config.fixtures_source.path}"
        reason += f"\nInput: {config.fixtures_source.url or config.fixtures_source.path}"
        if config.fixtures_source.release_page:
            reason += f"\nRelease page: {config.fixtures_source.release_page}"
        pytest.exit(
            returncode=0,
            reason=reason,
        )

    if config.fixtures_source.is_stdin:
        config.test_cases = TestCases.from_stream(sys.stdin)
        return
    index_file = config.fixtures_source.path / ".meta" / "index.json"
    index_file.parent.mkdir(parents=True, exist_ok=True)
    if not index_file.exists():
        rich.print(f"Generating index file [bold cyan]{index_file}[/]...")
        generate_fixtures_index(
            config.fixtures_source.path,
            quiet_mode=False,
            force_flag=False,
            disable_infer_format=False,
        )

    index = IndexFile.model_validate_json(index_file.read_text())
    config.test_cases = index.test_cases

    # Create XDistGroupMapper for enginex simulator if enginex options are present
    try:
        max_group_size = config.getoption("--enginex-max-group-size", None)
        if max_group_size is not None:
            config.xdist_group_mapper = XDistGroupMapper(max_group_size)
            config.xdist_group_mapper.build_mapping(config.test_cases)

            split_stats = config.xdist_group_mapper.get_split_statistics()
            if split_stats and config.option.verbose >= 1:
                rich.print("[bold yellow]Pre-allocation group splitting for load balancing:[/]")
                for pre_hash, stats in split_stats.items():
                    rich.print(
                        f"  Group {pre_hash[:8]}: {stats['total_tests']} tests → "
                        f"{stats['num_subgroups']} sub-groups "
                        f"(~{stats['average_tests_per_subgroup']} tests each)"
                    )
                rich.print(f"  Max group size: {max_group_size}")
        else:
            config.xdist_group_mapper = None
    except ValueError:
        config.xdist_group_mapper = None

    for fixture_format in BaseFixture.formats.values():
        config.addinivalue_line(
            "markers",
            f"{fixture_format.format_name}: Tests in `{fixture_format.format_name}` format ",
        )

    # All forked defined within EEST
    all_forks = {  # type: ignore
        fork for fork in set(get_forks()) | get_transition_forks() if not fork.ignore()
    }
    # Append all forks within the index file (compatibility with `ethereum/tests`)
    all_forks.update(getattr(index, "forks", []))
    for fork in all_forks:
        config.addinivalue_line("markers", f"{fork}: Tests for the {fork} fork")

    if config.option.sim_limit:
        if config.option.dest_regex != ".*":
            pytest.exit(
                "Both the --sim.limit (via env var?) and the --regex flags are set. "
                "Please only set one of them."
            )
        config.option.dest_regex = config.option.sim_limit.pattern
        if config.option.sim_limit.collectonly:
            config.option.collectonly = True
            config.option.verbose = -1  # equivalent to -q; only print test ids

    if config.option.collectonly or config.option.markers:
        return
    if not config.getoption("disable_html") and config.getoption("htmlpath") is None:
        # generate an html report by default, unless explicitly disabled
        config.option.htmlpath = Path(default_html_report_file_path())


def pytest_html_report_title(report):
    """Set the HTML report title (pytest-html plugin)."""
    report.title = "Consume Test Report"


def pytest_report_header(config):
    """Add the consume version and fixtures source to the report header."""
    source = config.fixtures_source
    lines = [
        f"consume ref: {get_current_commit_hash_or_tag()}",
        f"fixtures: {source.path}",
    ]
    if not source.is_local and not source.is_stdin:
        lines.append(f"fixtures url: {source.url}")
        lines.append(f"fixtures release: {source.release_page}")
    return lines


@pytest.fixture(scope="session")
def fixture_source_flags(request) -> List[str]:
    """Return the input flags used to specify the JSON test fixtures source."""
    return request.config.fixture_source_flags


@pytest.fixture(scope="session")
def fixtures_source(request) -> FixturesSource:  # noqa: D103
    return request.config.fixtures_source


def pytest_generate_tests(metafunc):
    """
    Generate test cases for every test fixture in all the JSON fixture files
    within the specified fixtures directory, or read from stdin if the directory is 'stdin'.

    This function only applies to the test_blockchain_via_engine test function
    to avoid conflicts with other consume simulators.
    """
    if "cache" in sys.argv:
        return

    # Only apply to functions that have a 'test_case' parameter (consume test functions)
    if "test_case" not in metafunc.fixturenames:
        return

    test_cases = metafunc.config.test_cases
    xdist_group_mapper = getattr(metafunc.config, "xdist_group_mapper", None)
    param_list = []

    # Check if this is an enginex simulator (has enginex-specific enhancements)
    is_enginex_function = (
        hasattr(metafunc.config, "_supported_fixture_formats")
        and "blockchain_test_engine_x" in metafunc.config._supported_fixture_formats
    )
    for test_case in test_cases:
        # Check if _supported_fixture_formats is set, if not allow all formats
        supported_formats = getattr(metafunc.config, "_supported_fixture_formats", None)
        if supported_formats and test_case.format.format_name not in supported_formats:
            continue

        fork_markers = get_relative_fork_markers(test_case.fork, strict_mode=False)

        # Basic test ID and markers (used by all consume tests)
        test_id = test_case.id
        markers = [getattr(pytest.mark, m) for m in fork_markers] + [
            getattr(pytest.mark, test_case.format.format_name)
        ]

        # Apply enginex-specific enhancements only for enginex functions
        if is_enginex_function:
            # Determine xdist group name for enginex load balancing
            if xdist_group_mapper and hasattr(test_case, "pre_hash") and test_case.pre_hash:
                # Use the mapper to get potentially split group name
                xdist_group_name = xdist_group_mapper.get_xdist_group_name(test_case)
            elif hasattr(test_case, "pre_hash") and test_case.pre_hash:
                # No mapper or not enginex, use pre_hash directly
                xdist_group_name = test_case.pre_hash
            else:
                # No pre_hash, use test ID
                xdist_group_name = test_case.id

            # Create enhanced test ID showing the xdist group name for easier identification
            if hasattr(test_case, "pre_hash") and test_case.pre_hash:
                # Show first 8 chars of xdist group name (includes sub-group if split)
                group_display = (
                    xdist_group_name[:8] if len(xdist_group_name) > 8 else xdist_group_name
                )
                # If it's a split group (contains ':'), show that clearly
                if ":" in xdist_group_name:
                    # Extract sub-group number for display
                    pre_hash_part, sub_group = xdist_group_name.split(":", 1)
                    group_display = f"{pre_hash_part[:8]}:{sub_group}"
                test_id = f"{test_case.id}[{group_display}]"

            # Add xdist group marker for load balancing
            markers.append(pytest.mark.xdist_group(name=xdist_group_name))

        param = pytest.param(test_case, id=test_id, marks=markers)
        param_list.append(param)

    metafunc.parametrize("test_case", param_list)

    if "client_type" in metafunc.fixturenames:
        metafunc.parametrize(
            "client_type",
            metafunc.config.hive_execution_clients,
            ids=[client.name for client in metafunc.config.hive_execution_clients],
        )
