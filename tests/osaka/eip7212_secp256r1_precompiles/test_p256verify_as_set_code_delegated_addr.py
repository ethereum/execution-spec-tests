"""
abstract: Tests P256VERIFY precompile as a set code delegated address
    Tests P256VERIFY precompile of [RIP-7212: Precompile for secp256r1 Curve Support](https://github.com/ethereum/RIPs/blob/master/RIPS/rip-7212.md)
    when used as a set code delegated address.
"""

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    AuthorizationTuple,
    Environment,
    StateTestFiller,
    Storage,
    Transaction,
    call_return_code,
)
from ethereum_test_tools import Opcodes as Op

from .spec import Spec, ref_spec_7212

REFERENCE_SPEC_GIT_PATH = ref_spec_7212.git_path
REFERENCE_SPEC_VERSION = ref_spec_7212.version

pytestmark = pytest.mark.valid_from("Osaka")

auth_account_start_balance = 0


@pytest.mark.with_all_call_opcodes
@pytest.mark.with_all_precompiles
@pytest.mark.eip_checklist("new_precompile/test/call_contexts/set_code")
def test_p256verify_as_set_code_delegated_addr(
    state_test: StateTestFiller,
    pre: Alloc,
    precompile: int,
    call_opcode: Op,
):
    """
    Test setting the code of an account to pre-compile address and executing all call
    opcodes.
    """
    auth_signer = pre.fund_eoa(auth_account_start_balance)

    value = 1 if call_opcode in {Op.CALL, Op.CALLCODE} else 0
    caller_code_storage = Storage()
    caller_code = (
        Op.SSTORE(
            caller_code_storage.store_next(call_return_code(opcode=call_opcode, success=True)),
            call_opcode(address=auth_signer, value=value, gas=0),
        )
        + Op.SSTORE(caller_code_storage.store_next(0), Op.RETURNDATASIZE)
        + Op.STOP
    )
    caller_code_address = pre.deploy_contract(caller_code, balance=value)

    tx = Transaction(
        sender=pre.fund_eoa(),
        gas_limit=500_000,
        to=caller_code_address,
        authorization_list=[
            AuthorizationTuple(
                address=Address(precompile),
                nonce=0,
                signer=auth_signer,
            ),
        ],
    )

    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post={
            auth_signer: Account(
                nonce=1,
                code=Spec.delegation_designation(Address(precompile)),
            ),
            caller_code_address: Account(
                storage=caller_code_storage,
            ),
        },
    )
