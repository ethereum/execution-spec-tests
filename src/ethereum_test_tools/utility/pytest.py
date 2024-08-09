"""
Pytest utility functions used to write Ethereum tests.
"""

from typing import Any

import pytest


def named_pytest_param(**argument_defaults: Any):
    """
    Returns a tuple of argument names and a parametrize function that generates
    `pytest.param` objects with the given argument names and default values.

    The default values can be overridden by passing them as keyword arguments to the
    `param` function.

    Arguments to this function are the default values for the parameters.

    The return value is a tuple of two elements:
    - A list of argument names.
    - The `pytest.param` generator function.

    Example usage:
    ```
    argument_names, param = named_pytest_param(
        parameter_1=0,
        parameter_2='default',
    )

    @pytest.mark.parametrize(
        argument_names,
        [
            param(parameter_1=1, id='test_1'),
            param(parameter_2='custom', id='test_2'),
        ],
    )
    def test(parameter_1, parameter_2):
        ...
    ```

    The above test will be run with two sets of parameters:
    - `parameter_1=1, parameter_2='default'`
    - `parameter_1=0, parameter_2='custom'`
    """

    def param(*, id: str, marks=(), **kwargs: Any):
        """
        Pytest parameter generator for gas tests.
        """
        args_list = [kwargs.get(name, argument_defaults[name]) for name in argument_defaults]
        return pytest.param(*args_list, id=id, marks=marks)

    return list(argument_defaults.keys()), param
