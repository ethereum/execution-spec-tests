"""test `CALLDATASIZE` opcode."""

import pytest

from ethereum_test_forks import Byzantium, Fork
from ethereum_test_tools import Account, Alloc, StateTestFiller, Transaction
from ethereum_test_tools import Macros as Om
from ethereum_test_tools.vm.opcode import Opcodes as Op


@pytest.mark.parametrize(
    "args_size",
    [0, 2, 16, 33, 257],
)
def test_calldataload(
    state_test: StateTestFiller,
    fork: Fork,
    args_size: int,
    pre: Alloc,
):
    """
    Test `CALLDATASIZE` opcode.

    Based on https://github.com/ethereum/tests/blob/81862e4848585a438d64f911a19b3825f0f4cd95/src/GeneralStateTestsFiller/VMTests/vmTests/calldatasizeFiller.yml
    """
    address = pre.deploy_contract(Op.SSTORE(key=0x0, value=Op.CALLDATASIZE))

    to = pre.deploy_contract(
        code=(
            Om.MSTORE(b"\x01" * args_size, 0x0)
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
        value=0x1,
    )
    post = {address: Account(storage={0x00: args_size})}
    state_test(pre=pre, post=post, tx=tx)
