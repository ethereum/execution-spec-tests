"""
Main module for ethereum test fuzzing tools.
"""

import random
from typing import Annotated, Any, Callable, get_args, get_origin


def type_fuzzer_generator(annotation: Any) -> Callable | None:
    """
    Returns a callable that generates a single fuzzed value for the given annotation.
    """
    if get_origin(annotation) is Annotated:
        # Parameter type should be annotated with a fuzz generator
        args = get_args(annotation)[1:]
        # TODO: Create a fuzz generator type and match each argument until found
        return args[0]
    if annotation == int:
        return lambda: random.randint(0, 2**256)
    return None
