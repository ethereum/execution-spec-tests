"""
Refiller pytest plugin that reads test cases from JSON/YAML files and fills them into test
fixtures.
"""

import inspect
import itertools
import json
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Tuple, Type

import pytest
import yaml
from _pytest.fixtures import FixtureRequest
from _pytest.mark import ParameterSet

from ethereum_test_fixtures import BaseFixture
from ethereum_test_forks import Fork, Paris
from ethereum_test_specs import SPEC_TYPES, BaseJSONTest

from ..shared.helpers import labeled_format_parameter_set


def pytest_collect_file(file_path: Path, path, parent) -> pytest.Collector | None:
    """
    Pytest hook that collects test cases from JSON/YAML files and fills them into test
    fixtures.
    """
    if file_path.suffix in (".json", ".yml"):
        return FillerFile.from_parent(parent, path=file_path)
    return None


def get_test_id_from_arg_names_and_values(
    arg_names: List[str], arg_values: List[Any] | Tuple[Any, ...]
) -> str:
    """Get the test id from argument names and values."""
    return "-".join(
        [
            f"{arg_name}={arg_value}"
            for arg_name, arg_value in zip(arg_names, arg_values, strict=True)
        ]
    )


def get_argument_names_and_values_from_parametrize_mark(
    mark: pytest.Mark | pytest.MarkDecorator,
) -> Tuple[List[str], List[ParameterSet]]:
    """Get the argument names and values from a parametrize mark."""
    if mark.name != "parametrize":
        raise Exception("Mark is not a parametrize mark")
    if mark.kwargs:
        raise Exception("Mark has kwargs which is not supported")
    args = mark.args
    if not isinstance(args, tuple):
        raise Exception("Args is not a tuple")
    if len(args) != 2:
        raise Exception("Args does not have 2 elements")
    arg_names = args[0] if isinstance(args[0], list) else args[0].split(",")
    arg_values = []
    for arg_value in args[1]:
        if not isinstance(arg_value, ParameterSet):
            if not isinstance(arg_value, tuple) and not isinstance(arg_value, list):
                arg_value = (arg_value,)
            test_id = get_test_id_from_arg_names_and_values(arg_names, arg_value)
            arg_values.append(ParameterSet(arg_value, [], id=test_id))
        else:
            arg_values.append(arg_value)
    return arg_names, arg_values


def get_all_combinations_from_parametrize_marks(
    parametrize_marks: List[pytest.Mark | pytest.MarkDecorator],
) -> Tuple[List[str], List[ParameterSet]]:
    """Get all combinations of arguments from multiple parametrize marks."""
    assert parametrize_marks, "No parametrize marks found"
    list_of_values: List[List[ParameterSet]] = []
    all_argument_names = []
    for mark in parametrize_marks:
        arg_names, arg_values = get_argument_names_and_values_from_parametrize_mark(mark)
        list_of_values.append(arg_values)
        all_argument_names.extend(arg_names)
    all_value_combinations: List[ParameterSet] = []
    # use itertools to get all combinations
    for combination in itertools.product(*list_of_values):
        all_value_combinations.append(
            ParameterSet(
                values=[param.values for param in combination],
                marks=[],
                id="-".join([param.id or "" for param in combination]),
            )
        )

    return all_argument_names, all_value_combinations


class FillerFile(pytest.File):
    """
    Filler file that reads test cases from JSON/YAML files and fills them into test
    fixtures.
    """

    def collect(self: "FillerFile") -> Generator["FillerTestItem", None, None]:
        """Collect test cases from JSON/YAML files and fill them into test fixtures."""
        with open(self.path, "r") as file:
            loaded_file = json.load(file) if self.path.suffix == ".json" else yaml.safe_load(file)
            for key in loaded_file:
                filler = BaseJSONTest.model_validate(loaded_file[key])
                call_obj = filler.fill_function()

                signature = inspect.signature(call_obj)
                spec_parameter_name = ""

                fixture_formats: List[ParameterSet] = []
                for test_type in SPEC_TYPES:
                    if test_type.pytest_parameter_name() in signature.parameters:
                        assert spec_parameter_name == "", "Multiple spec parameters found"
                        spec_parameter_name = test_type.pytest_parameter_name()
                        for format_with_or_without_label in test_type.supported_fixture_formats:
                            fixture_formats.append(
                                labeled_format_parameter_set(format_with_or_without_label)
                            )

                # TODO: For each fork
                forks: List[Fork] = [Paris]

                for fixture_format in fixture_formats:
                    for fork in forks:
                        call_kwargs: Dict[str, Any] = {}
                        call_fixture_resolved_kwargs = [
                            spec_parameter_name,
                        ]
                        marks: List[pytest.Mark | pytest.MarkDecorator] = []
                        for mark in fixture_format.marks:
                            if mark.name == "parametrize":
                                continue
                            marks.append(mark)
                        test_id = f"fork_{fork.name()}-{fixture_format.id}"
                        if "fork" in signature.parameters:
                            call_kwargs["fork"] = fork
                        if "pre" in signature.parameters:
                            call_fixture_resolved_kwargs.append("pre")
                        parametrize_marks: List[pytest.Mark | pytest.MarkDecorator] = []
                        if hasattr(call_obj, "pytestmark"):
                            for mark in call_obj.pytestmark:
                                if mark.name == "parametrize":
                                    parametrize_marks.append(mark)

                        if parametrize_marks:
                            parameter_names, parameter_set_list = (
                                get_all_combinations_from_parametrize_marks(parametrize_marks)
                            )
                            for parameter_set in parameter_set_list:
                                # Copy and extend the call_kwargs with the parameter set
                                case_marks = marks[:]
                                for mark in parameter_set.marks:
                                    if mark.name == "parametrize":
                                        continue
                                    case_marks.append(mark)
                                case_call_kwargs = call_kwargs.copy()
                                case_call_kwargs.update(
                                    dict(zip(parameter_names, parameter_set.values, strict=True))
                                )
                                yield FillerTestItem.from_parent(
                                    self,
                                    call_obj=call_obj,
                                    call_kwargs=case_call_kwargs,
                                    call_fixture_resolved_kwargs=call_fixture_resolved_kwargs,
                                    name=f"{key}[{test_id}-{parameter_set.id}]",
                                    fork=fork,
                                    fixture_format=fixture_format
                                    if isinstance(fixture_format, type)
                                    else fixture_format.values[0],
                                    marks=case_marks,
                                )
                        else:
                            yield FillerTestItem.from_parent(
                                self,
                                call_obj=call_obj,
                                call_kwargs=call_kwargs,
                                call_fixture_resolved_kwargs=call_fixture_resolved_kwargs,
                                name=f"{key}[{test_id}]",
                                fork=fork,
                                fixture_format=fixture_format
                                if isinstance(fixture_format, type)
                                else fixture_format.values[0],
                                marks=marks,
                            )


class FillerTestItem(pytest.Item):
    """
    Filler test item that reads test cases from JSON/YAML files and fills them into test
    fixtures.
    """

    originalname: str
    call_obj: Callable
    call_kwargs: Dict[str, Any]
    call_fixture_resolved_kwargs: List[str]
    github_url: str = ""
    fork: Fork
    fixture_format: Type[BaseFixture]

    def __init__(
        self,
        *args,
        originalname: str = "",
        call_obj: Callable,
        call_kwargs: Dict[str, Any],
        call_fixture_resolved_kwargs: List[str],
        fork: Fork,
        fixture_format: Type[BaseFixture],
        marks: List[pytest.Mark],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.originalname = originalname
        self.call_obj = call_obj
        self.call_kwargs = call_kwargs
        self.call_fixture_resolved_kwargs = call_fixture_resolved_kwargs
        self.fork = fork
        self.fixture_format = fixture_format
        for marker in marks:
            self.add_marker(marker)  # type: ignore

    def setup(self):
        """Resolve and apply fixtures before test execution."""
        self._fixtureinfo = self.session._fixturemanager.getfixtureinfo(
            self,
            None,
            None,
            funcargs=False,
        )
        request = FixtureRequest(self, _ispytest=True)
        for fixture_resolved_kwarg in self.call_fixture_resolved_kwargs:
            self.call_kwargs[fixture_resolved_kwarg] = request.getfixturevalue(
                fixture_resolved_kwarg
            )

    def runtest(self):
        """Execute the test logic."""
        self.call_obj(**self.call_kwargs)

    def reportinfo(self):
        return self.fspath, 0, f"Legacy filler test: {self.name}"
