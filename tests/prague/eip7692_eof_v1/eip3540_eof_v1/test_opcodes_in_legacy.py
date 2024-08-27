"""
Tests all EOF-only opcodes in legacy contracts and expects failure.
"""

import pytest

from ethereum_test_base_types import Alloc, Account
from ethereum_test_specs import StateTestFiller
from ethereum_test_tools import Bytecode, EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import AutoSection, Container, Section
from ethereum_test_types import Environment, Transaction
from ethereum_test_vm import Opcodes

from .. import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7692.md"
REFERENCE_SPEC_VERSION = "f0e7661ee0d16e612e0931ec88b4c9f208e9d513"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)

slot_code_executed = b"EXEC"
value_code_executed = b"exec"
value_non_execution_canary = b"brid"


@pytest.mark.parametrize(
    "code",
    [
        pytest.param(Op.PUSH0 + Op.DUPN[0], id="DUPN"),
        pytest.param(Op.PUSH0 + Op.SWAPN[0], id="SWAPN"),
        pytest.param(Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.EXCHANGE[2, 3], id="EXCHANGE"),
        pytest.param(Op.RJUMP[0], id="RJUMP"),
        pytest.param(Op.PUSH0 + Op.RJUMPI[0], id="RJUMPI"),
        pytest.param(Op.PUSH0 + Op.RJUMPV[0, 0], id="RJUMPI"),
        pytest.param(Op.CALLF[1], id="CALLF"),
        pytest.param(Op.RETF, id="RETF"),
        pytest.param(Op.JUMPF, id="JUMPF"),
        pytest.param(Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(2) + Op.EXTCALL, id="EXTCALL"),
        pytest.param(
            Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(2) + Op.EXTDELEGATECALL, id="EXTDELEGATECALL"
        ),
        pytest.param(
            Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(2) + Op.EXTSTATICCALL, id="EXTSTATICCALL"
        ),
        pytest.param(Op.DATALOAD(0), id="DATALOAD"),
        pytest.param(Op.DATALOADN[0], id="DATALOADN"),
        pytest.param(Op.DATASIZE, id="DATASIZE"),
        pytest.param(Op.DATACOPY(0, 0, 32), id="DATACOPY"),
        pytest.param(Op.EOFCREATE[0](0, 0, 0, 0), id="EOFCREATE"),
        pytest.param(Op.RETURNCONTRACT[0], id="RETURNCONTRACT"),
    ],
)
def test_opcodes_in_legacy(state_test: StateTestFiller, pre: Alloc, code: Opcodes):
    """
    Test all EOF only opcodes in legacy contracts and expects failure.
    """
    env = Environment()

    address_test_contract = pre.deploy_contract(
        code=code + Op.SSTORE(slot_code_executed, value_code_executed),
        storage={slot_code_executed: value_non_execution_canary},
    )

    post = {
        # assert the canary is not over-written. If it was written then the EOF opcode was valid
        address_test_contract: Account(storage={slot_code_executed: value_non_execution_canary}),
    }

    sender = pre.fund_eoa()

    tx = Transaction(
        sender=sender,
        to=address_test_contract,
        gas_limit=5_000_000,
        gas_price=10,
        protected=False,
        data="",
    )

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )
