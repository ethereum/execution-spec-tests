"""test `CALLDATASIZE` opcode."""

import pytest

from ethereum_test_forks import Byzantium, Fork
from ethereum_test_tools import Account, Alloc, StateTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op


@pytest.mark.parametrize(
    "args_size,sha3_len,storage",
    [
        ("0002", "01", 0x02),
        ("0011", "01", 0x11),
        ("0021", "01", 0x21),
        ("0031", "01", 0x31),
        ("0101", "01", 0x101),
        ("0002", "02", 0x02),
        ("0011", "02", 0x11),
        ("0021", "02", 0x21),
        ("0031", "02", 0x31),
        ("0101", "02", 0x101),
        ("0002", "03", 0x02),
        ("0011", "03", 0x11),
        ("0021", "03", 0x21),
        ("0031", "03", 0x31),
        ("0101", "03", 0x101),
        ("0002", "04", 0x02),
        ("0011", "04", 0x11),
        ("0021", "04", 0x21),
        ("0031", "04", 0x31),
        ("0101", "04", 0x101),
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
    args_size: str,
    sha3_len: str,
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
    tx_data = bytes.fromhex("1a8451e6" + "00" * 30 + args_size + "00" * 31 + sha3_len)

    tx = Transaction(
        data=tx_data,
        gas_limit=100_000,
        protected=fork >= Byzantium,
        sender=pre.fund_eoa(),
        to=to,
    )
    post = {address: Account(storage={0x00: storage})}
    state_test(pre=pre, post=post, tx=tx)
