"""test `CALLDATALOAD` opcode."""

import pytest

from ethereum_test_forks import Byzantium, Fork
from ethereum_test_tools import Account, Alloc, StateTestFiller, Transaction
from ethereum_test_tools import Macros as Om
from ethereum_test_tools.vm.opcode import Opcodes as Op


@pytest.mark.parametrize(
    "calldata,calldata_offset,expected_storage",
    [
        (
            b"\x25\x60",
            0x0,
            0x2560000000000000000000000000000000000000000000000000000000000000,
        ),
        (
            b"\xff" * 32 + b"\x23",
            0x1,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF23,
        ),
        (
            bytes.fromhex("123456789ABCDEF00000000000000000000000000000000000000000000000000024"),
            0x5,
            0xBCDEF00000000000000000000000000000000000000000000000000024000000,
        ),
    ],
    ids=[
        "two_bytes",
        "word_n_byte",
        "34_bytes",
    ],
)
def test_calldataload(
    state_test: StateTestFiller,
    calldata: bytes,
    calldata_offset: int,
    fork: Fork,
    pre: Alloc,
    expected_storage: Account,
):
    """
    Test `CALLDATALOAD` opcode.

    Based on https://github.com/ethereum/tests/blob/ae4791077e8fcf716136e70fe8392f1a1f1495fb/src/GeneralStateTestsFiller/VMTests/vmTests/calldatacopyFiller.yml
    """
    address_a = pre.deploy_contract(
        (Op.PUSH1[calldata_offset] + Op.CALLDATALOAD + Op.PUSH1[0x0] + Op.SSTORE + Op.STOP),
    )

    address_b = pre.deploy_contract(
        Om.MSTORE(calldata, 0x0)
        + Op.CALL(
            gas=Op.SUB(Op.GAS(), 0x100),
            address=address_a,
            value=0x0,
            args_offset=0x0,
            args_size=len(calldata),
            ret_offset=0x0,
            ret_size=0x0,
        )
    )

    to = pre.deploy_contract(
        code=(
            Op.ADD(0x1000, Op.CALLDATALOAD(offset=0x4))
            + Op.CALL(
                gas=Op.SUB(Op.GAS(), 0x100),
                address=address_b,
                value=0x0,
                args_offset=0x0,
                args_size=0x0,
                ret_offset=0x0,
                ret_size=0x0,
            )
            + Op.STOP
        ),
    )

    tx = Transaction(
        data=calldata,
        gas_limit=100_000,
        protected=fork >= Byzantium,
        sender=pre.fund_eoa(),
        to=to,
    )
    post = {
        address_a: Account(storage={0x00: expected_storage}),
    }
    state_test(pre=pre, post=post, tx=tx)
