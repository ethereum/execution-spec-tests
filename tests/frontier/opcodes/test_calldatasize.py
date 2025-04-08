"""test `CALLDATASIZE` opcode."""

import pytest

from ethereum_test_forks import Byzantium, Fork
from ethereum_test_tools import Account, Alloc, StateTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op


@pytest.mark.parametrize(
    "args_size,sha3_len,storage",
    [
        (0x0002, 0x01, 0x02),
        (0x0011, 0x01, 0x11),
        (0x0021, 0x01, 0x21),
        (0x0031, 0x01, 0x31),
        (0x0101, 0x01, 0x101),
        (0x0002, 0x02, 0x02),
        (0x0011, 0x02, 0x11),
        (0x0021, 0x02, 0x21),
        (0x0031, 0x02, 0x31),
        (0x0101, 0x02, 0x101),
        (0x0002, 0x03, 0x02),
        (0x0011, 0x03, 0x11),
        (0x0021, 0x03, 0x21),
        (0x0031, 0x03, 0x31),
        (0x0101, 0x03, 0x101),
        (0x0002, 0x04, 0x02),
        (0x0011, 0x04, 0x11),
        (0x0021, 0x04, 0x21),
        (0x0031, 0x04, 0x31),
        (0x0101, 0x04, 0x101),
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
    args_size: int,
    sha3_len: int,
    pre: Alloc,
    storage: Account,
):
    """
    Test `CALLDATASIZE` opcode.

    Based on https://github.com/ethereum/tests/blob/81862e4848585a438d64f911a19b3825f0f4cd95/src/GeneralStateTestsFiller/VMTests/vmTests/calldatasizeFiller.yml
    """
    address = pre.deploy_contract(Op.SSTORE(key=0x0, value=Op.CALLDATASIZE))

    to = pre.deploy_contract(
        code=(
            Op.MSTORE(offset=0x0, value=Op.SHA3(offset=0x0, size=sha3_len))
            + Op.CALL(
                gas=Op.SUB(Op.GAS(), 0x100),
                address=address,
                value=0x0,
                args_offset=0x0,
                args_size=args_size,
                ret_offset=0x0,
                ret_size=0x0,
            )
        )
    )

    tx = Transaction(
        gas_limit=100_000,
        protected=fork >= Byzantium,
        sender=pre.fund_eoa(),
        to=to,
    )
    post = {address: Account(storage={0x00: storage})}
    state_test(pre=pre, post=post, tx=tx)
