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
    [getattr(Op, f"PUSH{i}") for i in range(0, 33)],
    ids=lambda op: str(op),
)
@pytest.mark.with_all_evm_code_types
def test_push(
    state_test: StateTestFiller,
    fork: str,
    push_opcode: Op,
    pre: Alloc,
    get_number_list,
):
    """
    Test the PUSH0-PUSH32 opcodes.
    """

    env = Environment()
    sender = pre.fund_eoa()
    post = {}

    values = get_number_list

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


@pytest.fixture(scope="module")
def get_number_list():
    """Returns a list consisting of values that take an increasing amount of bytes to be stored"""
    return [0] + [get_largest_value_that_requires_at_least_x_bytes(i) for i in range(1, 33)]
