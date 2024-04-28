"""
A collection of contracts used in 7620 EOF tests
"""
from ethereum_test_tools import Address
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import Transaction
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION

smallest_runtime_subcontainer = Container(
    name="Runtime Subcontainer",
    sections=[
        Section.Code(
            code=Op.STOP, code_inputs=0, code_outputs=NON_RETURNING_SECTION, max_stack_height=0
        )
    ],
)

smallest_initcode_subcontainer = Container(
    name="Initcode Subcontainer",
    sections=[
        Section.Code(
            code=Op.RETURNCONTRACT[0](0, 0),
            code_inputs=0,
            code_outputs=NON_RETURNING_SECTION,
            max_stack_height=2,
        ),
        Section.Container(container=smallest_runtime_subcontainer),
    ],
)


def fixed_address(index: int) -> Address:
    """
    Returns an determinstic address for testing
    Parameters
    ----------
    index - how foar off of the initial to create the address

    Returns
    -------
    An address, unique per index and human friendly for testing

    """
    return Address(0x7E570000 + index)


default_address = fixed_address(0)


def simple_transaction(
    target: Address = default_address, payload: bytes = b"", gas_limit: int = 10_000_000
):
    """
    Creates a simple transaction
    Parameters
    ----------
    target the target address, defaults to 0x100
    payload the payload, defauls to empty

    Returns
    -------
    a transaction instance that can be passed into state_tests
    """
    return Transaction(
        nonce=1, to=target, gas_limit=gas_limit, gas_price=10, protected=False, data=payload
    )
