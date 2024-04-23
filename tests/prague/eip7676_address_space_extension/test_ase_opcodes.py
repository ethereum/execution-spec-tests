"""
Execution of CALLF, RETF opcodes within EOF V1 containers tests
"""

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Environment,
    StateTestFiller,
    TestAddress,
    Transaction,
)
from ethereum_test_tools.common.conversions import BytesConvertible, to_bytes
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7676.md"
REFERENCE_SPEC_VERSION = (
    "00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
)

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize(
    "target_address",
    (
        b"",
        b"\x10\x00",
        b"\x78" * 20,
        b"\xff" * 20,
        b"\x01" + (b"\x00" * 20),
        b"\x5a" * 28,
        b"\x5a" * 32,
        b"\xff" * 32,
    ),
    ids=["zero", "short", "mid20", "max20", "minAse", "midAse", "fullAse", "maxAse"],
)
@pytest.mark.parametrize("target_account_type", ("empty", "EOA", "Contract"), ids=lambda x: x)
def test_address_space_extension(
    state_test: StateTestFiller,
    target_address: BytesConvertible,
    target_account_type: str,
):
    """
    Test contacts with possibly extended address and fail if address is too large
    """
    env = Environment()

    address_bytes = to_bytes(target_address)
    ase_address = len(address_bytes) > 20
    if ase_address and address_bytes[0] == b"00":
        raise ValueError("Test instrumentation requires target addresses trim leading zeros")

    pre = {
        TestAddress: Account(
            balance=1000000000000000000000,
            nonce=1,
        ),
        Address(0x100): Account(
            code=(
                Op.MSTORE(0, Op.PUSH32(address_bytes))
                + Op.SSTORE(0, Op.CALL(50000, 0x200, 0, 0, 32, 0, 0))
                + Op.SSTORE(1, Op.CALL(50000, 0x300, 0, 0, 32, 0, 0))
                + Op.SSTORE(2, Op.CALL(50000, 0x400, 0, 0, 32, 0, 0))
                + Op.SSTORE(3, Op.CALL(50000, 0x500, 0, 0, 32, 0, 0))
                + Op.SSTORE(4, Op.CALL(50000, 0x201, 0, 0, 32, 0, 0))
                + Op.SSTORE(5, Op.CALL(50000, 0x301, 0, 0, 32, 0, 0))
                + Op.SSTORE(6, Op.CALL(50000, 0x401, 0, 0, 32, 0, 0))
                + Op.SSTORE(7, Op.CALL(50000, 0x501, 0, 0, 32, 0, 0))
                + Op.SSTORE(8, Op.CALL(50000, 0x601, 0, 0, 32, 0, 0))
                + Op.STOP()
            ),
            nonce=1,
        ),
        Address(0x200): Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.BALANCE(Op.CALLDATALOAD(0))) + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=2,
                    )
                ],
            ),
            nonce=1,
        ),
        Address(0x201): Account(
            code=Op.SSTORE(0, Op.BALANCE(Op.CALLDATALOAD(0))) + Op.STOP,
            nonce=1,
        ),
        Address(0x300): Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.EXTCALL(Op.CALLDATALOAD(0), 0, 0, 0))
                        + Op.SSTORE(1, Op.RETURNDATALOAD(0))
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=4,
                    )
                ],
            ),
            nonce=1,
        ),
        Address(0x301): Account(
            code=Op.SSTORE(0, Op.CALL(Op.GAS, Op.CALLDATALOAD(0), 0, 0, 0, 0, 0))
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            + Op.SSTORE(1, Op.MLOAD(0))
            + Op.STOP,
            nonce=1,
        ),
        Address(0x400): Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.EXTDELEGATECALL(Op.CALLDATALOAD(0), 0, 0))
                        + Op.SSTORE(1, Op.RETURNDATALOAD(0))
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=3,
                    )
                ],
            ),
            nonce=1,
        ),
        Address(0x401): Account(
            code=Op.SSTORE(0, Op.DELEGATECALL(Op.GAS, Op.CALLDATALOAD(0), 0, 0, 0, 0))
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            + Op.SSTORE(1, Op.MLOAD(0))
            + Op.STOP,
            nonce=1,
        ),
        Address(0x500): Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.EXTSTATICCALL(Op.CALLDATALOAD(0), 0, 0))
                        + Op.SSTORE(1, Op.RETURNDATALOAD(0))
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=3,
                    )
                ],
            ),
            nonce=1,
        ),
        Address(0x501): Account(
            code=Op.SSTORE(0, Op.STATICCALL(Op.GAS, Op.CALLDATALOAD(0), 0, 0, 0, 0))
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            + Op.SSTORE(1, Op.MLOAD(0))
            + Op.STOP,
            nonce=1,
        ),
        Address(0x601): Account(
            code=Op.SSTORE(0, Op.CALLCODE(Op.GAS, Op.CALLDATALOAD(0), 0, 0, 0, 0, 0))
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            + Op.SSTORE(1, Op.MLOAD(0))
            + Op.STOP,
            nonce=1,
        ),
    }

    stripped_address = address_bytes[-20:] if ase_address else target_address
    post = {
        Address(0x100): Account(
            storage={0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1}
            if not ase_address
            else {4: 1, 5: 1, 6: 1, 7: 1, 8: 1}
        )
    }
    match target_account_type:
        case "empty":
            # add no account
            pass
        case "EOA":
            pre[Address(stripped_address)] = Account(code="", balance=10**18, nonce=9)
            post[Address(0x200)] = Account(storage={} if ase_address else {0: 10**18})
            post[Address(0x201)] = Account(storage={0: 10**18})
        case "Contract":
            pre[Address(stripped_address)] = Account(
                code=Op.MSTORE(0, Op.ADDRESS) + Op.RETURN(0, 32), balance=0, nonce=0
            )
            # For EOF variants the EXT*CALL reverts, so no storage updates for ASE address
            post[Address(0x300)] = Account(storage={} if ase_address else {1: stripped_address})
            post[Address(0x301)] = Account(storage={0: 1, 1: stripped_address})
            # EXTDELEGATECALL fails when calling legacy, so no stripped address
            post[Address(0x400)] = Account(storage={} if ase_address else {0: 1})
            post[Address(0x401)] = Account(storage={0: 1, 1: 0x401})
            post[Address(0x500)] = Account(storage={} if ase_address else {1: stripped_address})
            post[Address(0x501)] = Account(storage={0: 1, 1: stripped_address})
            post[Address(0x601)] = Account(storage={0: 1, 1: 0x601})
        case _:
            raise ValueError("Unknown account type: " + target_account_type)

    tx = Transaction(
        nonce=1,
        to=Address(0x100),
        gas_limit=50000000,
        gas_price=10,
        protected=False,
        data="",
    )

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )
