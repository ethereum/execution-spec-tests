"""
abstract: Tests [EIP-3540: EOF - EVM Object Format v1](https://eips.ethereum.org/EIPS/eip-3540)
    Tests for [EIP-3540: EOF - EVM Object Format v1](https://eips.ethereum.org/EIPS/eip-3540).
"""

from typing import Any

import pytest

from ethereum_test_forks import Shanghai
from ethereum_test_tools import EOFException, EOFTestFiller

EOF_FORK = Shanghai

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "e27f0bce83584d38748e33ef5095dd4593cc721a"


@pytest.mark.parametrize(
    "code,expect_exception",
    [
        pytest.param(
            "0xef00010100040200010004040000000080000160005000",
            None,
            id="valid_code_1",
        ),
    ],
    ids=["empty_code"],
)
@pytest.mark.valid_from(str(EOF_FORK))
def test_basic_eof_test_generation(
    eof_test: EOFTestFiller, code: Any, expect_exception: EOFException | None
) -> None:
    """
    Test basic EOF test generation.
    """
    eof_test(
        data=code,
        expect_exception=expect_exception,
    )
