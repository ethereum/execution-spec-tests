"""Test variants of the deposit contract which adheres the log-style as described in EIP-6110."""

import pytest

from ethereum_test_tools import (Account, Alloc, Block, BlockchainTestFiller,
                                 Header)
from ethereum_test_tools import Macros as Om
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import Requests, Transaction

from .helpers import DepositRequest
from .spec import Spec, ref_spec_6110

REFERENCE_SPEC_GIT_PATH = ref_spec_6110.git_path
REFERENCE_SPEC_VERSION = ref_spec_6110.version


@pytest.mark.parametrize(
    "deposit_event_includes_abi_encoding",
    [
        pytest.param(True),
        pytest.param(False, marks=pytest.mark.skip(reason="Not in spec")),
    ],
)
def test_extra_logs(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    deposit_event_includes_abi_encoding: bool,
):
    """Test deposit contract emitting more log event types than the ones in mainnet."""
    # Supplant mainnet contract with a variant that emits two logs, one of which
    # has a different data length.
    deposit_request = DepositRequest(
        pubkey=0x01,
        withdrawal_credentials=0x02,
        amount=120_000_000_000_000_000,
        signature=0x03,
        index=0x0,
    )
    deposit_request_log = deposit_request.log(
        include_abi_encoding=deposit_event_includes_abi_encoding,
    )

    bytecode = (
        Op.LOG1(
            # ERC-20 token transfer log
            0,
            32,
            0xDDF252AD1BE2C89B69C2B068FC378DAA952BA7F163C4A11628F55A4DF523B3EF,
        )
        + Om.MSTORE(deposit_request_log)
        + Op.LOG1(
            0,
            len(deposit_request_log),
            0x649BBC62D0E31342AFEA4E5CD82D4049E7E1EE912FC0889AA790803BE39038C5,
        )
        + Op.STOP
    )
    assert len(deposit_request_log) == 576

    pre[Spec.DEPOSIT_CONTRACT_ADDRESS] = Account(
        code=bytecode,
        nonce=1,
        balance=0,
    )
    sender = pre.fund_eoa()

    tx = Transaction(
        to=Spec.DEPOSIT_CONTRACT_ADDRESS,
        sender=sender,
        gas_limit=100_000,
    )

    blockchain_test(
        pre=pre,
        blocks=[
            Block(
                txs=[tx],
                header_verify=Header(
                    requests_hash=Requests(deposit_request),
                ),
            ),
        ],
        post={},
    )
