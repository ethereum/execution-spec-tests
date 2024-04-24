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

ID_EOF_BALANCE = 0
ID_BALANCE = 1
ID_EXTCALL = 2
ID_CALL = 3
ID_EXTDELEGATE = 4
ID_DELEGATECALL = 5
ID_EXTSTATIC = 6
ID_STATICALL = 7
ID_CALLCODE = 8

BASE_ADDR = 100000000
ADDR_EOF_BALANCE = Address(BASE_ADDR + ID_EOF_BALANCE)
ADDR_BALANCE = Address(BASE_ADDR + ID_BALANCE)
ADDR_EXTCALL = Address(BASE_ADDR + ID_EXTCALL)
ADDR_CALL = Address(BASE_ADDR + ID_CALL)
ADDR_EXTDELEGATE = Address(BASE_ADDR + ID_EXTDELEGATE)
ADDR_DELEGATECALL = Address(BASE_ADDR + ID_DELEGATECALL)
ADDR_EXTSTATIC = Address(BASE_ADDR + ID_EXTSTATIC)
ADDR_STATICALL = Address(BASE_ADDR + ID_STATICALL)
ADDR_CALLCODE = Address(BASE_ADDR + ID_CALLCODE)


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
                + Op.SSTORE(ID_EOF_BALANCE, Op.CALL(50000, ADDR_EOF_BALANCE, 0, 0, 32, 0, 0))
                + Op.SSTORE(ID_BALANCE, Op.CALL(50000, ADDR_BALANCE, 0, 0, 32, 0, 0))
                + Op.SSTORE(ID_EXTCALL, Op.CALL(50000, ADDR_EXTCALL, 0, 0, 32, 0, 0))
                + Op.SSTORE(ID_CALL, Op.CALL(50000, ADDR_CALL, 0, 0, 32, 0, 0))
                + Op.SSTORE(ID_EXTDELEGATE, Op.CALL(50000, ADDR_EXTDELEGATE, 0, 0, 32, 0, 0))
                + Op.SSTORE(ID_DELEGATECALL, Op.CALL(50000, ADDR_DELEGATECALL, 0, 0, 32, 0, 0))
                + Op.SSTORE(ID_EXTSTATIC, Op.CALL(50000, ADDR_EXTSTATIC, 0, 0, 32, 0, 0))
                + Op.SSTORE(ID_STATICALL, Op.CALL(50000, ADDR_STATICALL, 0, 0, 32, 0, 0))
                + Op.SSTORE(ID_CALLCODE, Op.CALL(50000, ADDR_CALLCODE, 0, 0, 32, 0, 0))
                + Op.STOP()
            ),
            nonce=1,
        ),
        ADDR_EOF_BALANCE: Account(
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
        ADDR_BALANCE: Account(
            code=Op.SSTORE(0, Op.BALANCE(Op.CALLDATALOAD(0))) + Op.STOP,
            nonce=1,
        ),
        ADDR_EXTCALL: Account(
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
        ADDR_CALL: Account(
            code=Op.SSTORE(0, Op.CALL(Op.GAS, Op.CALLDATALOAD(0), 0, 0, 0, 0, 0))
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            + Op.SSTORE(1, Op.MLOAD(0))
            + Op.STOP,
            nonce=1,
        ),
        ADDR_EXTDELEGATE: Account(
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
        ADDR_DELEGATECALL: Account(
            code=Op.SSTORE(0, Op.DELEGATECALL(Op.GAS, Op.CALLDATALOAD(0), 0, 0, 0, 0))
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            + Op.SSTORE(1, Op.MLOAD(0))
            + Op.STOP,
            nonce=1,
        ),
        ADDR_EXTSTATIC: Account(
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
        ADDR_STATICALL: Account(
            code=Op.SSTORE(0, Op.STATICCALL(Op.GAS, Op.CALLDATALOAD(0), 0, 0, 0, 0))
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            + Op.SSTORE(1, Op.MLOAD(0))
            + Op.STOP,
            nonce=1,
        ),
        ADDR_CALLCODE: Account(
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
            storage={
                ID_BALANCE: 1,
                ID_CALL: 1,
                ID_DELEGATECALL: 1,
                ID_STATICALL: 1,
                ID_CALLCODE: 1,
            }
            if ase_address
            else {
                ID_EOF_BALANCE: 1,
                ID_BALANCE: 1,
                ID_EXTCALL: 1,
                ID_CALL: 1,
                ID_EXTDELEGATE: 1,
                ID_DELEGATECALL: 1,
                ID_EXTSTATIC: 1,
                ID_STATICALL: 1,
                ID_CALLCODE: 1,
            }
        )
    }
    match target_account_type:
        case "empty":
            # add no account
            pass
        case "EOA":
            pre[Address(stripped_address)] = Account(code="", balance=10**18, nonce=9)
            post[ADDR_EOF_BALANCE] = Account(storage={} if ase_address else {0: 10**18})
            post[ADDR_BALANCE] = Account(storage={0: 10**18})
        case "Contract":
            pre[Address(stripped_address)] = Account(
                code=Op.MSTORE(0, Op.ADDRESS) + Op.RETURN(0, 32), balance=0, nonce=0
            )
            # For EOF variants the EXT*CALL reverts, so no storage updates for ASE address
            post[ADDR_EXTCALL] = Account(storage={} if ase_address else {1: stripped_address})
            post[ADDR_CALL] = Account(storage={0: 1, 1: stripped_address})
            # EXTDELEGATECALL fails when calling legacy, so no stripped address
            post[ADDR_EXTDELEGATE] = Account(storage={} if ase_address else {0: 1})
            post[ADDR_DELEGATECALL] = Account(storage={0: 1, 1: ADDR_DELEGATECALL})
            post[ADDR_EXTSTATIC] = Account(storage={} if ase_address else {1: stripped_address})
            post[ADDR_STATICALL] = Account(storage={0: 1, 1: stripped_address})
            post[ADDR_CALLCODE] = Account(storage={0: 1, 1: ADDR_CALLCODE})
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
