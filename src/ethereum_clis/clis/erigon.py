"""Erigon execution client transition tool."""

from ethereum_test_exceptions import ExceptionMapper


class ErigonExceptionMapper(ExceptionMapper):
    """Erigon exception mapper."""

    mapping_substring = {}
    mapping_regex = {}
