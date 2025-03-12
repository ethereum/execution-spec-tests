"""test `CALLDATALOAD` opcode."""

import pytest

from ethereum_test_forks import Byzantium, Fork
from ethereum_test_tools import Account, Alloc, Bytecode, StateTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op


@pytest.mark.parametrize(
    "mstore,args_size,code_for_200,tx_data,code_address_storage",
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
        "two_bytes",
        "word_n_byte",
        "34_bytes",
    ],
)
def test_calldataload(
    state_test: StateTestFiller,
    mstore: Bytecode,
    args_size: int,
    code_for_200: Bytecode,
    fork: Fork,
    tx_data: bytes,
    pre: Alloc,
    code_address_storage: Account,
):
    """
    Test `CALLDATALOAD` opcode.

    Based on https://github.com/ethereum/tests/blob/ae4791077e8fcf716136e70fe8392f1a1f1495fb/src/GeneralStateTestsFiller/VMTests/vmTests/calldatacopyFiller.ym
    """
    code_200_address = pre.deploy_contract(code_for_200)

    code_1000_address = pre.deploy_contract(
        mstore
        + Op.CALL(
            gas=0xFFFFFF,
            address=code_200_address,
            value=0x0,
            args_offset=0x0,
            args_size=args_size,
            ret_offset=0x0,
            ret_size=0x0,
        )
    )

    to = pre.deploy_contract(
        code=(
            Op.ADD(0x1000, Op.CALLDATALOAD(offset=0x4))
            + Op.CALL(
                gas=0xFFFFFF,
                # address=Op.ADD(0x1000, Op.CALLDATALOAD(offset=0x4)),
                address=code_1000_address,
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
        data=tx_data,
        gas_limit=100_000,
        gas_price=0x0A,
        protected=fork >= Byzantium,
        sender=pre.fund_eoa(),
        to=to,
        value=0x01,
    )
    post = {code_200_address: code_address_storage}
    state_test(pre=pre, post=post, tx=tx)
