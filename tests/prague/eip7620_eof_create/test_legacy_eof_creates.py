"""
Test interactions between CREATE, CREATE2, and EOFCREATE
"""

import pytest

from ethereum_test_tools import Account, Environment, StateTestFiller, TestAddress
from ethereum_test_tools.vm.opcode import Opcodes
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import default_address, simple_transaction, smallest_initcode_subcontainer
from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "52ddbcdddcf72dd72427c319f2beddeb468e1737"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize(
    "legacy_code_factory",
    [
        lambda size: Op.CREATE(0, 0, size),
        lambda size: Op.CREATE2(0, 0, size, 0),
    ],
    ids=["CREATE", "CREATE2"],
)
def test_cross_version_creates_fail(
    state_test: StateTestFiller,
    legacy_code_factory: Opcodes,
):
    """
    Verifies that CREATE and CREATE2 cannot create EOF contracts
    """
    env = Environment()
    eof_container_size = len(smallest_initcode_subcontainer)
    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(
            code=Op.JUMP(eof_container_size + 3)  # PUSH1, xx, JUMP
            + bytes(smallest_initcode_subcontainer)
            + Op.JUMPDEST
            + Op.CODECOPY(0, 3, eof_container_size)
            + Op.SSTORE(0, legacy_code_factory(eof_container_size))
            + Op.SSTORE(1, 1)
            + Op.STOP
        ),
    }
    # Storage in 0 should be empty as the create/create2 should fail,
    # and 1 in 1 to show execution continued and did not halt
    post = {default_address: Account(storage={1: 1})}

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


@pytest.mark.parametrize(
    "legacy_code_factory",
    [
        lambda size: Op.CREATE(0, 0, size),
        lambda size: Op.CREATE2(0, 0, size, 0),
    ],
    ids=["CREATE", "CREATE2"],
)
def test_legacy_initcode_eof_contract_fails(
    state_test: StateTestFiller,
    legacy_code_factory: Opcodes,
):
    """
    Verifies that legacy initcode cannot create EOF
    """
    env = Environment()
    eof_container_size = len(smallest_initcode_subcontainer)
    init_code = (
        Op.JUMP(eof_container_size + 3)
        + bytes(smallest_initcode_subcontainer)
        + Op.JUMPDEST
        + Op.CODECOPY(0, 3, eof_container_size)
        + Op.RETURN(0, eof_container_size)
    )
    init_code_size = len(init_code)
    factory_code = (
        Op.JUMP(init_code_size + 3)
        + bytes(init_code)
        + Op.JUMPDEST
        + Op.CODECOPY(0, 3, init_code_size)
        + Op.SSTORE(0, legacy_code_factory(init_code_size))
        + Op.SSTORE(1, 1)
    )

    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(code=factory_code),
    }
    # Storage in 0 should be empty as the final CREATE filed
    # and 1 in 1 to show execution continued and did not halt
    post = {default_address: Account(storage={1: 1})}

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())
