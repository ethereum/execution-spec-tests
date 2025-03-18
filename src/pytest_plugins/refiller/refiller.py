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
                funcobj = filler.fill_function()

                definition = FunctionDefinition.from_parent(self, name=key, callobj=funcobj)

                fixtureinfo = definition._fixtureinfo

                # pytest_generate_tests impls call metafunc.parametrize() which fills
                # metafunc._calls, the outcome of the hook.
                metafunc = pytest.Metafunc(
                    definition=definition,
                    fixtureinfo=fixtureinfo,
                    config=self.config,
                )

                self.ihook.pytest_generate_tests.call_extra([], dict(metafunc=metafunc))

                if not metafunc._calls:
                    yield pytest.Function.from_parent(self, name=key, fixtureinfo=fixtureinfo)
                else:
                    # Add funcargs() as fixturedefs to fixtureinfo.arg2fixturedefs.
                    fm = self.session._fixturemanager
                    # fixtures.add_funcarg_pseudo_fixture_def(self, metafunc, fm)

                    # Add_funcarg_pseudo_fixture_def may have shadowed some fixtures
                    # with direct parametrization, so make sure we update what the
                    # function really needs.
                    fixtureinfo.prune_dependency_tree()

                    for callspec in metafunc._calls:
                        subname = f"{key}[{callspec.id}]"
                        yield pytest.Function.from_parent(
                            self,
                            name=subname,
                            callspec=callspec,
                            fixtureinfo=fixtureinfo,
                            keywords={callspec.id: True},
                            originalname=f"{self.path}",
                        )


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
