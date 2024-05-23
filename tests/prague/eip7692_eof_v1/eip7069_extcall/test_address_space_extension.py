"""
Tests the "Address Space Extension" aspect of EXT*CALL
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

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7069.md"
REFERENCE_SPEC_VERSION = "1795943aeacc86131d5ab6bb3d65824b3b1d4cad"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)

ID_EXTCALL = 2
ID_CALL = 3
ID_EXTDELEGATECALL = 4
ID_DELEGATECALL = 5
ID_EXTSTATICCALL = 6
ID_STATICCALL = 7
ID_CALLCODE = 8

BASE_ADDRESS = 100000000
ADDRESS_EXTCALL = Address(BASE_ADDRESS + ID_EXTCALL)
ADDRESS_CALL = Address(BASE_ADDRESS + ID_CALL)
ADDRESS_EXTDELEGATECALL = Address(BASE_ADDRESS + ID_EXTDELEGATECALL)
ADDRESS_DELEGATECALL = Address(BASE_ADDRESS + ID_DELEGATECALL)
ADDRESS_EXTSTATICCALL = Address(BASE_ADDRESS + ID_EXTSTATICCALL)
ADDRESS_STATICCALL = Address(BASE_ADDRESS + ID_STATICCALL)
ADDRESS_CALLCODE = Address(BASE_ADDRESS + ID_CALLCODE)


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
                + Op.SSTORE(ID_EXTCALL, Op.CALL(50000, ADDRESS_EXTCALL, 0, 0, 32, 0, 0))
                + Op.SSTORE(ID_CALL, Op.CALL(50000, ADDRESS_CALL, 0, 0, 32, 0, 0))
                + Op.SSTORE(
                    ID_EXTDELEGATECALL, Op.CALL(50000, ADDRESS_EXTDELEGATECALL, 0, 0, 32, 0, 0)
                )
                + Op.SSTORE(ID_DELEGATECALL, Op.CALL(50000, ADDRESS_DELEGATECALL, 0, 0, 32, 0, 0))
                + Op.SSTORE(
                    ID_EXTSTATICCALL, Op.CALL(50000, ADDRESS_EXTSTATICCALL, 0, 0, 32, 0, 0)
                )
                + Op.SSTORE(ID_STATICCALL, Op.CALL(50000, ADDRESS_STATICCALL, 0, 0, 32, 0, 0))
                + Op.SSTORE(ID_CALLCODE, Op.CALL(50000, ADDRESS_CALLCODE, 0, 0, 32, 0, 0))
                + Op.STOP()
            ),
            nonce=1,
        ),
        ADDRESS_EXTCALL: Account(
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
        ADDRESS_CALL: Account(
            code=Op.SSTORE(0, Op.CALL(Op.GAS, Op.CALLDATALOAD(0), 0, 0, 0, 0, 0))
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            + Op.SSTORE(1, Op.MLOAD(0))
            + Op.STOP,
            nonce=1,
        ),
        ADDRESS_EXTDELEGATECALL: Account(
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
        ADDRESS_DELEGATECALL: Account(
            code=Op.SSTORE(0, Op.DELEGATECALL(Op.GAS, Op.CALLDATALOAD(0), 0, 0, 0, 0))
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            + Op.SSTORE(1, Op.MLOAD(0))
            + Op.STOP,
            nonce=1,
        ),
        ADDRESS_EXTSTATICCALL: Account(
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
        ADDRESS_STATICCALL: Account(
            code=Op.SSTORE(0, Op.STATICCALL(Op.GAS, Op.CALLDATALOAD(0), 0, 0, 0, 0))
            + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE)
            + Op.SSTORE(1, Op.MLOAD(0))
            + Op.STOP,
            nonce=1,
        ),
        ADDRESS_CALLCODE: Account(
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
                ID_CALL: 1,
                ID_DELEGATECALL: 1,
                ID_STATICCALL: 1,
                ID_CALLCODE: 1,
            }
            if ase_address
            else {
                ID_EXTCALL: 1,
                ID_CALL: 1,
                ID_EXTDELEGATECALL: 1,
                ID_DELEGATECALL: 1,
                ID_EXTSTATICCALL: 1,
                ID_STATICCALL: 1,
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
        case "Contract":
            pre[Address(stripped_address)] = Account(
                code=Op.MSTORE(0, Op.ADDRESS) + Op.RETURN(0, 32), balance=0, nonce=0
            )
            # For EOF variants the EXT*CALL reverts, so no storage updates for ASE address
            post[ADDRESS_EXTCALL] = Account(storage={} if ase_address else {1: stripped_address})
            post[ADDRESS_CALL] = Account(storage={0: 1, 1: stripped_address})
            # EXTDELEGATECALL fails when calling legacy, so no stripped address
            post[ADDRESS_EXTDELEGATECALL] = Account(storage={} if ase_address else {0: 1})
            post[ADDRESS_DELEGATECALL] = Account(storage={0: 1, 1: ADDRESS_DELEGATECALL})
            post[ADDRESS_EXTSTATICCALL] = Account(
                storage={} if ase_address else {1: stripped_address}
            )
            post[ADDRESS_STATICCALL] = Account(storage={0: 1, 1: stripped_address})
            post[ADDRESS_CALLCODE] = Account(storage={0: 1, 1: ADDRESS_CALLCODE})
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
