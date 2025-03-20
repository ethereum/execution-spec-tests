"""
Refiller pytest plugin that reads test cases from JSON/YAML files and fills them into test
fixtures.
"""

import json
from pathlib import Path

import pytest
import yaml

from ethereum_test_fixtures import StateFixture
from ethereum_test_forks import Berlin, Fork
from ethereum_test_specs import BaseJSONTest


def pytest_collect_file(file_path: Path, path, parent) -> pytest.Collector | None:
    """
    Pytest hook that collects test cases from JSON/YAML files and fills them into test
    fixtures.
    """
    if file_path.suffix in (".json", ".yml"):
        return FillerFile.from_parent(parent, fspath=file_path)
    return None


class FillerFile(pytest.File):
    """
    Pytest file class that reads test cases from JSON/YAML files and fills them into test
    fixtures.
    """

    def collect(self):
        """Load the test vectors using known filler formats."""
        collected_items = []
        config = self.config
        with open(self.path, "r") as file:
            loaded_file = json.load(file) if self.path.suffix == ".json" else yaml.safe_load(file)
            for key in loaded_file:
                filler = BaseJSONTest.model_validate(loaded_file[key])
                test_func = filler.fill_function()
                item = FillerItem.from_parent(
                    self, name=f"{key}[]", config=config, callobj=test_func
                )
                collected_items.append(item)
        return collected_items


class FillerItem(pytest.Item):
    """Single test case from a JSON/YAML file that is filled into a test fixture."""

    json_test: BaseJSONTest
    test_case: str
    fork: Fork

    def __init__(self, *, parent, config, **kwargs):
        """Initialize the test case."""
        super().__init__(**kwargs)
        self.config = config
        self.session = parent.session

    def setup(self):
        """Resolve and apply fixtures before test execution."""
        fm = self.session._fixturemanager  # Access fixture manager
        request = pytest.FixtureRequest(self, _ispytest=True)
        self.funcargs = {}  # Dictionary to store fixture values

        # Request session-scoped fixtures manually
        for fixturedef in fm._arg2fixturedefs.get("session", []):
            fixture = fm.getfixturedefs(fixturedef.scope)
            if fixture:
                self.funcargs[fixturedef] = request.getfixturevalue(fixturedef)

    def runtest(self):
        """Fill the test case into the test fixture."""
        print(f"Running test: {self.name} with fixtures {self.funcargs}")

    def reportinfo(self):
        return self.fspath, 0, f"custom test: {self.name}"
