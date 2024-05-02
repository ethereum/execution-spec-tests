"""
EOF V1 Code Validation tests
"""
import pytest

from ethereum_test_tools import EOFTestFiller
from ethereum_test_tools.eof.v1 import Container

from .contracts import INVALID, VALID, container_name
from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6206.md"
REFERENCE_SPEC_VERSION = "a1775816657df4093787fb9fe83c2f7cc17ecf47"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize(
    "container",
    VALID,
    ids=container_name,
)
def test_jumpf_code_validation_valid(
    eof_test: EOFTestFiller,
    container: Container,
):
    """
    Test creating various types of valid EOF V1 contracts using legacy
    initcode and a contract creating transaction.
    """
    assert (
        container.validity_error is None
    ), f"Valid container with validity error: {container.validity_error}"
    eof_test(
        data=container,
    )


@pytest.mark.parametrize(
    "container",
    INVALID,
    ids=container_name,
)
def test_jumpf_code_validation_invalid(
    eof_test: EOFTestFiller,
    container: Container,
):
    """
    Test creating various types of valid EOF V1 contracts using legacy
    initcode and a contract creating transaction.
    """
    assert container.validity_error is not None, "Invalid container without validity error"
    eof_test(
        data=container,
        expect_exception=container.validity_error,
    )
