"""
Refiller pytest plugin that reads test cases from JSON/YAML files and fills them into test
fixtures.
"""

import json
from pathlib import Path
from typing import Iterable, Union

import pytest
import yaml
from _pytest.python import PyCollector

from ethereum_test_specs import BaseJSONTest


def pytest_addoption(parser: pytest.Parser):
    """Add command-line options to pytest."""
    refiller_group = parser.getgroup("refiller", "Arguments defining refiller behavior")
    refiller_group.addoption(
        "--json-filler-source",
        action="store",
        dest="json_filler_source",
        default="./tests/",
        type=Path,
        help=(
            "Path to directory containing JSON/YAML filler files."
            " Default: `ethereum-spec-evm-resolver`."
        ),
    )


def pytest_collect_file(file_path: Path, path, parent) -> pytest.Collector | None:
    """
    Pytest hook that collects test cases from JSON/YAML files and fills them into test
    fixtures.
    """
    if file_path.suffix in (".json", ".yml"):
        return FillerFile.from_parent(parent, path=file_path)
    return None


class FillerFile(pytest.File):
    """
    Pytest file class that reads test cases from JSON/YAML files and fills them into test
    fixtures.
    """

    def collect(self):
        """Load the test vectors using known filler formats."""
        with open(self.path, "r") as file:
            loaded_file = json.load(file) if self.path.suffix == ".json" else yaml.safe_load(file)
            for key in loaded_file:
                filler = BaseJSONTest.model_validate(loaded_file[key])
                yield filler.fill_function()
                # PyCollector._genfunctions(filler.fill_function())
                # yield pytest.Function.from_parent(
                #     parent=self,
                #     name=key,
                #     callobj=filler.fill_function(),
                # )
                """ for test_case in filler.get_test_cases():
                    yield FillerItem.from_parent(
                        self,
                        json_test=filler,
                        name=f"{key}_{test_case}",
                        test_case=test_case,
                        path=self.path,
                    ) """


""" 
class FillerItem(pytest.Item):
    ""Single test case from a JSON/YAML file that is filled into a test fixture.""

    json_test: BaseJSONTest
    test_case: str

    def __init__(self, *, json_test: BaseJSONTest, test_case: str, **kwargs):
        ""Initialize the test case.""
        super().__init__(**kwargs)
        self.json_test = json_test
        self.test_case = test_case

    def runtest(self):
        ""Fill the test case into the test fixture.""
        self.json_test.fill_test_case(self.test_case)
 """
