"""
Test execution semantic changes on contracts mid-creation.
"""
import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Bytecode,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .. import EOF_FORK_NAME
from ..eip7620_eof_create.helpers import smallest_runtime_subcontainer

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "137ecc2ae5d9ce23c3d5b77ef3c68851468e7433"

key_legacy_ext_result = 0x01
key_legacy_caller = 0x02

# Parameters for testing EXTCODE* opcodes calling EOF containers mid-creation
ext_code_pytest_params = [
    pytest.param(
        Op.SSTORE(key_legacy_ext_result, Op.EXTCODESIZE(Op.CALLER))
        + Op.SSTORE(key_legacy_caller, Op.CALLER),
        0,
        id="EXTCODESIZE",
    ),
    pytest.param(
        Op.EXTCODECOPY(Op.CALLER, 0, 0, 32)
        + Op.SSTORE(key_legacy_ext_result, Op.MLOAD(0))
        + Op.SSTORE(key_legacy_caller, Op.CALLER),
        0,
        id="EXTCODECOPY",
    ),
    pytest.param(
        Op.SSTORE(key_legacy_ext_result, Op.EXTCODEHASH(Op.CALLER))
        + Op.SSTORE(key_legacy_caller, Op.CALLER),
        0xC5D2460186F7233C927E7DB2DCC703C0E500B653CA82273B7BFAD8045D85A470,
        id="EXTCODEHASH",
    ),
]


@pytest.fixture
def address_legacy_contract(pre: Alloc, legacy_code: Bytecode) -> Address:  # noqa: D103
    return pre.deploy_contract(
        legacy_code,
        storage={
            key_legacy_ext_result: 0xB17D,  # a canary to be overwritten
        },
    )


@pytest.fixture
def init_container(address_legacy_contract: Address) -> Container:  # noqa: D103
    return Container(
        sections=[
            Section.Code(
                code=(Op.EXTCALL(address_legacy_contract, 0, 0, 0) + Op.RETURNCONTRACT[0](0, 0)),
            ),
            Section.Container(container=smallest_runtime_subcontainer),
        ],
    )


@pytest.mark.parametrize(
    "legacy_code,expected_result",
    ext_code_pytest_params,
)
def test_legacy_calls_eof_init_container_sstore(
    state_test: StateTestFiller,
    pre: Alloc,
    address_legacy_contract: Address,
    init_container: Container,
    expected_result: int,
):
    """Test EXTCODE* opcodes calling EOF containers mid-creation"""
    env = Environment()
    salt = 0
    eof_contract_creator_code = Container(
        sections=[
            Section.Code(
                code=Op.SSTORE(0, Op.EOFCREATE[0](0, salt, 0, 0)) + Op.STOP,
            ),
            Section.Container(
                container=init_container,
            ),
        ],
    )

    address_eof_contract_creator = pre.deploy_contract(eof_contract_creator_code)

    created_contract_address = init_container.eofcreate_address(address_eof_contract_creator, salt)

    tx = Transaction(
        sender=pre.fund_eoa(),
        to=address_eof_contract_creator,
        gas_limit=50_000_000,
    )

    post = {
        address_legacy_contract: Account(
            storage={
                key_legacy_ext_result: expected_result,
                key_legacy_caller: created_contract_address,
            }
        ),
        created_contract_address: Account(
            code=smallest_runtime_subcontainer,
        ),
        address_eof_contract_creator: Account(
            storage={
                0: created_contract_address,
            },
            nonce=2,
        ),
    }

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


@pytest.mark.parametrize(
    "legacy_code,expected_result",
    ext_code_pytest_params,
)
@pytest.mark.with_all_contract_creating_tx_types
def test_legacy_calls_eof_init_tx_container_sstore(
    state_test: StateTestFiller,
    pre: Alloc,
    address_legacy_contract: Address,
    init_container: Container,
    expected_result: int,
    tx_type: int,
):
    """Test EXTCODE* opcodes calling EOF containers mid-creation from a creating transaction"""
    env = Environment()

    tx = Transaction(
        sender=pre.fund_eoa(),
        type=tx_type,
        to=None,
        gas_limit=1_000_000,
        data=init_container,
    )

    created_contract_address = tx.created_contract

    post = {
        address_legacy_contract: Account(
            storage={
                key_legacy_ext_result: expected_result,
                key_legacy_caller: created_contract_address,
            }
        ),
        created_contract_address: Account(
            code=smallest_runtime_subcontainer,
        ),
    }

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )
