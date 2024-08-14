"""
Pytest utility functions used to write Ethereum tests.
"""

from typing import Any, Dict, List

import pytest

PARAMETRIZE_KWARG_NAMES = ["indirect", "ids", "scope"]
PARAM_KWARG_NAMES = ["id", "marks"]


def named_parametrize(*, cases: List[Dict[str, Any]], **argument_defaults: Any):
    """
    `pytest.mark.parametrize` replacement that allows to specify parameter names with default
    values for each parameter.

    Example usage:
    ```
    @named_parametrize(
        parameter_1=0,  # Default value for parameter_1 is zero
        parameter_2='default',  # Default value for parameter_2 is 'default' string
        cases=[
            dict(parameter_1=1, id='test_1'),
            dict(parameter_2='custom', id='test_2'),
        ],
    )
    def test(parameter_1, parameter_2):
        ...
    ```

    The above test will be run with two sets of parameters:
    - `parameter_1=1, parameter_2='default'`
    - `parameter_1=0, parameter_2='custom'`
    """
    parametrize_kwargs = {
        k: argument_defaults.pop(k) for k in PARAMETRIZE_KWARG_NAMES if k in argument_defaults
    }
    param_cases: List[Any] = []
    for args in cases:
        # Remove keyword arguments that are part of the `pytest.param` signature
        param_kwargs = {k: args.pop(k) for k in PARAM_KWARG_NAMES if k in args}
        # Merge default arguments with the test case arguments
        args = {**argument_defaults, **args}
        param_cases.append(pytest.param(*args.values(), **param_kwargs))

    return pytest.mark.parametrize(list(argument_defaults), param_cases, **parametrize_kwargs)
