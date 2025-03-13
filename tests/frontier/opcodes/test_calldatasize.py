"""test `CALLDATASIZE` opcode."""

import pytest

from ethereum_test_forks import Byzantium, Fork
from ethereum_test_tools import Account, Alloc, Bytecode, StateTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op


@pytest.mark.parametrize(
    "mstore,args_size,code_for_address_a,tx_data,address_a_storage",
    [
        (
            (Op.MSTORE8(offset=0x0, value=0x25) + Op.MSTORE8(offset=0x1, value=0x60)),
            0x2,
            (Op.PUSH1[0x0] + Op.CALLDATALOAD + Op.PUSH1[0x0] + Op.SSTORE),
            b"\x00",
            Account(
                storage={0x00: 0x2560000000000000000000000000000000000000000000000000000000000000}
            ),
        ),
        (
            (
                Op.MSTORE(
                    offset=0x0,
                    value=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                )
                + Op.MSTORE8(offset=0x20, value=0x23)
            ),
            0x21,
            (Op.PUSH1[0x1] + Op.CALLDATALOAD + Op.PUSH1[0x0] + Op.SSTORE + Op.STOP),
            b"\x01",
            Account(
                storage={0x00: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF23}
            ),
        ),
        (
            (
                Op.MSTORE(
                    offset=0x0,
                    value=0x123456789ABCDEF0000000000000000000000000000000000000000000000000,
                )
                + Op.MSTORE8(offset=0x20, value=0x0)
                + Op.MSTORE8(offset=0x21, value=0x24)
            ),
            0x22,
            (Op.PUSH1[0x5] + Op.CALLDATALOAD + Op.PUSH1[0x0] + Op.SSTORE + Op.STOP),
            b"\x02",
            Account(
                storage={0x00: 0xBCDEF00000000000000000000000000000000000000000000000000024000000}
            ),
        ),
    ],
    ids=[
        "data1_2",
        "data1_11",
        "data1_21",
        "data1_31",
        "data1_101",
        "data2_2",
        "data2_11",
        "data2_21",
        "data2_31",
        "data2_101",
        "data3_2",
        "data3_11",
        "data3_21",
        "data3_31",
        "data3_101",
        "data4_2",
        "data4_11",
        "data4_21",
        "data4_31",
        "data4_101",
    ],
)
def test_calldataload(
    state_test: StateTestFiller,
    fork: Fork,
    tx_data: bytes,
    pre: Alloc,
    address_a_storage: Account,
):
    """
    Test `CALLDATASIZE` opcode.

    https://github.com/ethereum/tests/blob/81862e4848585a438d64f911a19b3825f0f4cd95/src/GeneralStateTestsFiller/VMTests/vmTests/calldatasizeFiller.yml
    """
    address = pre.deploy_contract(Op.SSTORE(key=0x0, value=Op.CALLDATASIZE))

    to = pre.deploy_contract(
        code=(
            Op.MSTORE(offset=0x0, value=Op.SHA3(offset=0x0, size=Op.CALLDATALOAD(offset=0x24)))
            + Op.CALL(
                gas=Op.SUB(Op.GAS(), 0x100),
                address=address,
                value=0x0,
                args_offset=0x0,
                args_size=Op.CALLDATALOAD(offset=0x4),
                ret_offset=0x0,
                ret_size=0x0,
            )
        )
    )

    tx = Transaction(
        data=tx_data,
        gas_limit=100_000,
        gas_price=0x0A,
        protected=fork >= Byzantium,
        sender=pre.fund_eoa(),
        to=to,
        value=0x01,
    )
    post = {address: address_a_storage}
    state_test(pre=pre, post=post, tx=tx)
