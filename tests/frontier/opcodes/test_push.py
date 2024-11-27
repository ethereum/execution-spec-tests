"""
A State test for the set of `PUSH*` opcodes.
Ported from: https://github.com/ethereum/tests/blob/4f65a0a7cbecf4442415c226c65e089acaaf6a8b/src/GeneralStateTestsFiller/VMTests/vmTests/pushFiller.yml # noqa: E501
"""

import pytest

from ethereum_test_forks import Frontier, Homestead
from ethereum_test_tools import Account, Alloc, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import StateTestFiller, Transaction


@pytest.mark.parametrize(
    "push_opcode",
    [getattr(Op, f"PUSH{i}") for i in range(1, 33)],  # Dynamically parametrize PUSH opcodes
    ids=lambda op: str(op),
)
@pytest.mark.valid_from("Frontier")
def test_push(state_test: StateTestFiller, fork: str, push_opcode: Op, pre: Alloc):
    """
    The set of `PUSH*` opcodes pushes data onto the stack.

    In this test, we ensure that the set of `PUSH*` opcodes writes
    a portion of an excerpt from the Ethereum yellow paper to
    storage.
    """
    # Input used to test the `PUSH*` opcode.
    ethereum_state_machine = b"Ethereum is as a transaction-based state machine."

    # Determine the size of the data to be pushed by the `PUSH*` opcode,
    # and trim the input to an appropriate excerpt.
    input_size = int(str(push_opcode)[4:])
    excerpt = ethereum_state_machine[0:input_size]

    env = Environment()

    """
     **               Bytecode explanation              **
     +---------------------------------------------------+
     | Bytecode      | Stack        | Storage            |
     |---------------------------------------------------|
     | PUSH* excerpt | excerpt      |                    |
     | PUSH1 0       | 0 excerpt    |                    |
     | SSTORE        |              | [0]: excerpt       |
     +---------------------------------------------------+
    """

    contract_code = push_opcode(excerpt) + Op.PUSH1(0) + Op.SSTORE
    contract = pre.deploy_contract(contract_code)

    tx = Transaction(
        sender=pre.fund_eoa(),
        to=contract,
        gas_limit=500_000,
        protected=False if fork in [Frontier, Homestead] else True,
    )

    post = {}
    post[contract] = Account(storage={0: int.from_bytes(excerpt, byteorder="big")})

    state_test(env=env, pre=pre, post=post, tx=tx)
