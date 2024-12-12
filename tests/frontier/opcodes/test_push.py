"""
abstract: Test PUSH
    Test the PUSH opcodes.

"""

import pytest

from ethereum_test_forks import Frontier, Homestead
from ethereum_test_tools import Account, Alloc, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import StateTestFiller, Storage, Transaction


@pytest.mark.parametrize(
    "push_opcode",
    [
        Op.PUSH0,
        Op.PUSH1,
        Op.PUSH2,
        Op.PUSH3,
        Op.PUSH4,
        Op.PUSH5,
        Op.PUSH6,
        Op.PUSH7,
        Op.PUSH8,
        Op.PUSH9,
        Op.PUSH10,
        Op.PUSH11,
        Op.PUSH12,
        Op.PUSH13,
        Op.PUSH14,
        Op.PUSH15,
        Op.PUSH16,
        Op.PUSH17,
        Op.PUSH18,
        Op.PUSH19,
        Op.PUSH20,
        Op.PUSH21,
        Op.PUSH22,
        Op.PUSH23,
        Op.PUSH24,
        Op.PUSH25,
        Op.PUSH26,
        Op.PUSH27,
        Op.PUSH28,
        Op.PUSH29,
        Op.PUSH30,
        Op.PUSH31,
        Op.PUSH32,
    ],
    ids=lambda op: str(op),
)
@pytest.mark.with_all_evm_code_types
def test_push(
    state_test: StateTestFiller,
    fork: str,
    push_opcode: Op,
    pre: Alloc,
):
    """
    Test the PUSH0-PUSH32 opcodes.
    """

    env = Environment()
    sender = pre.fund_eoa()
    post = {}

    # 0x5F is PUSH0, so from the current opcode's int we can derive which iteration we are in
    #    PUSH0  = iteration 0
    #    PUSH1  = iteration 1
    #    ...
    #    PUSH32 = iteration 32
    current_iter = (
        push_opcode.int() - 0x5F
    )  # also equal to the amount of bytes required to store value chosen in current iteration

    account_code = b"".join(
        # first pushX (X changes each iteration) a value, then push1 key=1, then sstore
        [
            bytes([push_opcode.int()]),
            values[current_iter].to_bytes(current_iter, byteorder="big"),
            bytes([Op.PUSH1.int()]),
            bytes([0x01]),
            bytes([Op.SSTORE.int()]),
        ]
    )

    account = pre.deploy_contract(account_code)

    tx = Transaction(
        ty=0x0,
        nonce=0,
        to=account,
        gas_limit=500000,
        gas_price=10,
        protected=False if fork in [Frontier, Homestead] else True,
        data="",
        sender=sender,
    )

    s: Storage.StorageDictType = {1: values[current_iter]}

    post[account] = Account(storage=s)

    state_test(env=env, pre=pre, post=post, tx=tx)


def get_largest_value_that_requires_at_least_x_bytes(bytes_required):
    """Returns the largest value that can be stored with the specified amount of bytes

    Args:
        bytes_required (int): Amount of bytes that are available

    Returns:
        int: Largest  possible value that can be stored with specified amount of bytes
    """
    if bytes_required > 0:
        return (2 ** (8 * bytes_required)) - 1


# in global scope so that it doesn't get re-created every iteration
# generate list of values that require x bytes, x+1 bytes, etc. to store
values = [0] + [get_largest_value_that_requires_at_least_x_bytes(i) for i in range(1, 33)]
