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


class MyFunction(pytest.Function):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def runtest(self):
        self.func(self)


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
        with open(self.path, "r") as file:
            loaded_file = json.load(file) if self.path.suffix == ".json" else yaml.safe_load(file)
            for key in loaded_file:
                filler = BaseJSONTest.model_validate(loaded_file[key])
                test_func = filler.fill_function()
                item = pytest.Function.from_parent(self, name=f"{key}[]", callobj=test_func)
                item.fixturenames = test_func.__code__.co_varnames
                collected_items.append(item)
        return collected_items


class FillerItem(pytest.Item):
    """Single test case from a JSON/YAML file that is filled into a test fixture."""

    json_test: BaseJSONTest
    test_case: str
    fork: Fork

    def __init__(self, *, json_test: BaseJSONTest, test_case: str, fork: Fork, **kwargs):
        """Initialize the test case."""
        super().__init__(**kwargs)
        self.json_test = json_test
        self.test_case = test_case
        self.fork = fork

    def runtest(self):
        """Fill the test case into the test fixture."""
        session = self.parent.session
        fixture_manager = session._fixturemanager
        request: pytest.FixtureRequest = fixture_manager.request(self)
        state_test = request.getfixturevalue("state_test")

        # self.json_test.fill_test_case(self.test_case)
