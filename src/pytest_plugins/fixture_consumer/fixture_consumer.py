"""
A pytest plugin to execute the blocktest on the specified fixture directory.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Optional

import pytest

from evm_transition_tool import FixtureFormats, TransitionTool


@dataclass
class FixtureData:  # noqa: D101
    fixture_name: str
    fixture_format: FixtureFormats
    json_file_path: Path


def pytest_addoption(parser):  # noqa: D103
    consume_group = parser.getgroup(
        "consume", "Arguments related to consuming fixtures via a client"
    )
    consume_group.addoption(
        "--fixture-directory",
        type=Path,
        action="store",
        default="fixtures",
        help="Specify the fixture directory to execute tests on. Default: 'fixtures'.",
    )
    consume_group.addoption(
        "--multiple-tests-per-file",
        action="store_true",
        dest="do_multiple_tests_per_file",
        default=False,
        help="Execute one test per fixture in each json file within the fixtures directory.",
    )
    consume_group.addoption(
        "--evm-bin",
        action="store",
        dest="evm_bin",
        type=Path,
        default=None,
        help=(
            "Path to an evm executable that provides `blocktest`. Default: First 'evm' entry in "
            "PATH."
        ),
    )
    consume_group.addoption(
        "--traces",
        action="store_true",
        dest="evm_collect_traces",
        default=False,
        help="Collect traces of the execution information from the transition tool.",
    )
    debug_group = parser.getgroup("debug", "Arguments defining debug behavior")
    debug_group.addoption(
        "--evm-dump-dir",
        action="store",
        dest="base_dump_dir",
        type=Path,
        default=None,
        help="Path to dump the transition tool debug output.",
    )


@pytest.fixture(autouse=True, scope="session")
def evm(request) -> Generator[TransitionTool, None, None]:
    """
    Returns the interface to the evm binary that will consume tests.
    """
    evm = TransitionTool.from_binary_path(
        binary_path=request.config.getoption("evm_bin"),
        # TODO: The verify_fixture() method doesn't currently use this option.
        trace=request.config.getoption("evm_collect_traces"),
    )
    yield evm
    evm.shutdown()


@pytest.fixture(scope="function")
def test_dump_dir(request, json_fixture_path: Path, fixture_name: str) -> Optional[Path]:
    """
    The directory to write evm debug output to.
    """
    base_dump_dir = request.config.getoption("base_dump_dir")
    if not base_dump_dir:
        return None
    if request.config.getoption("do_multiple_tests_per_file"):
        if len(fixture_name) > 142:
            # ensure file name is not too long for eCryptFS
            fixture_name = fixture_name[:70] + "..." + fixture_name[-70:]
        return base_dump_dir / json_fixture_path.stem / fixture_name
    return base_dump_dir / json_fixture_path.stem


@pytest.fixture(scope="function")
def json_fixture_path(fixture_data):
    """
    Provide the path to the current JSON fixture file.
    """
    return fixture_data.json_file_path


@pytest.fixture(scope="function")
def fixture_name(fixture_data):
    """
    The name of the current fixture.
    """
    return fixture_data.fixture_name


def pytest_generate_tests(metafunc):
    """
    Generate test cases for every fixture in all JSON fixture files within the
    fixtures directory.
    """
    if "fixture_name" in metafunc.fixturenames:
        fixtures_directory = metafunc.config.getoption("fixture_directory")

        fixture_data = []
        fixture_ids = []
        for json_file in fixtures_directory.glob("**/*.json"):
            with json_file.open() as f:
                data = json.load(f)
                if metafunc.config.getoption("do_multiple_tests_per_file"):
                    for fixture_name in data.keys():
                        fixture_data.append(
                            FixtureData(fixture_name, FixtureFormats.BLOCKCHAIN_TEST, json_file)
                        )
                        fixture_ids.append(f"{json_file.name}_{fixture_name}")
                else:
                    fixture_data.append(
                        FixtureData(json_file.name, FixtureFormats.BLOCKCHAIN_TEST, json_file)
                    )
                    fixture_ids.append(f"{json_file.name}")

        metafunc.parametrize("fixture_data", fixture_data, ids=fixture_ids)
