"""
Refiller pytest plugin that reads test cases from JSON/YAML files and fills them into test
fixtures.
"""

import json
from pathlib import Path
from typing import Iterable, List, Union

import pytest
import yaml
from _pytest.python import FunctionDefinition

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


class DynamicModule(pytest.Module):
    def istestfunction(obj, *args) -> bool:
        return True


class FillerFile(pytest.File):
    """
    Pytest file class that reads test cases from JSON/YAML files and fills them into test
    fixtures.
    """

    def collect(self):
        """Load the test vectors using known filler formats."""
        dict_values: List[List[Union[pytest.Item, pytest.Collector]]] = []
        with open(self.path, "r") as file:
            loaded_file = json.load(file) if self.path.suffix == ".json" else yaml.safe_load(file)
            values: List[Union[pytest.Item, pytest.Collector]] = []
            module = DynamicModule.from_parent(
                parent=self,
                fspath="/home/marioevz/Development/Eth/execution-spec-tests/src/pytest_plugins/refiller/refiller.py",
            )
            for key in loaded_file:
                filler = BaseJSONTest.model_validate(loaded_file[key])
                funcobj = filler.fill_function()
                setattr(funcobj, "__test__", True)

                ihook = self.ihook
                res = ihook.pytest_pycollect_makeitem(collector=module, name=key, obj=funcobj)

                if res is None:
                    continue
                elif isinstance(res, list):
                    values.extend(res)
                else:
                    values.append(res)

                # pytest_generate_tests impls call metafunc.parametrize() which fills
                # metafunc._calls, the outcome of the hook.

                """ 
                yield pytest.Function.from_parent(
                    parent=self,
                    name=key,
                    callspec=filler.fill_function_callspec(),
                    callobj=funcobj,
                )
                for test_case in filler.get_test_cases():
                    yield FillerItem.from_parent(
                        self,
                        json_test=filler,
                        name=f"{key}_{test_case}",
                        test_case=test_case,
                        path=self.path,
                    ) """
            dict_values.append(values)
        result = []
        for values in reversed(dict_values):
            result.extend(values)
        return result


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
