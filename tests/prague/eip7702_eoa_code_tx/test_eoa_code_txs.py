"""
abstract: Tests use of set-code transactions from [EIP-7702: Set EOA account code for one transaction](https://eips.ethereum.org/EIPS/eip-7702)
    Tests use of set-code transactions from [EIP-7702: Set EOA account code for one transaction](https://eips.ethereum.org/EIPS/eip-7702).
"""  # noqa: E501

import pytest

from ethereum_test_tools import Account, Alloc, AuthorizationTuple, Environment, Initcode
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import StateTestFiller, Storage, Transaction, compute_create_address

from .spec import ref_spec_7702

REFERENCE_SPEC_GIT_PATH = ref_spec_7702.git_path
REFERENCE_SPEC_VERSION = ref_spec_7702.version

pytestmark = pytest.mark.valid_from("Prague")


def test_set_code_to_self_destruct(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test the executing self-destruct opcode in a set-code transaction.
    """
    signer = pre.fund_eoa(0)

    set_code_to_address = pre.deploy_contract(Op.SELFDESTRUCT(Op.ADDRESS))

    sender = pre.fund_eoa(10**18)

    tx = Transaction(
        gas_limit=1_000_000,
        to=sender,
        value=0,
        authorization_tuples=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=signer,
            ),
        ],
        sender=sender,
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={},
    )


@pytest.mark.parametrize(
    "op",
    [
        Op.CREATE,
        Op.CREATE2,
    ],
)
def test_set_code_to_contract_creator(
    state_test: StateTestFiller,
    pre: Alloc,
    op: Op,
):
    """
    Test the executing self-destruct opcode in a set-code transaction.
    """
    storage = Storage()
    signer = pre.fund_eoa(0)

    deployed_code = Op.STOP
    initcode = Initcode(deploy_code=deployed_code)

    deployed_contract_address = compute_create_address(signer)

    set_code = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
        storage.store_next(deployed_contract_address),
        op(value=0, offset=0, size=Op.CALLDATASIZE),
    )
    set_code_to_address = pre.deploy_contract(
        set_code,
    )

    sender = pre.fund_eoa(10**18)

    tx = Transaction(
        gas_limit=1_000_000,
        to=sender,
        value=0,
        data=initcode,
        authorization_tuples=[
            AuthorizationTuple(
                address=set_code_to_address,
                nonce=0,
                signer=signer,
            ),
        ],
        sender=sender,
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            set_code_to_address: Account(storage={}),
            signer: Account(nonce=1, code=b"", storage=storage),
            deployed_contract_address: Account(
                code=deployed_code,
                storage={},
            ),
        },
    )
