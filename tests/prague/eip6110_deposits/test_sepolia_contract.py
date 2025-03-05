"""Test sepolia variant logs contract."""

from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Header,
    Requests,
    Transaction,
)
from ethereum_test_tools import Macros as Om
from ethereum_test_tools import Opcodes as Op

from .helpers import DepositRequest
from .spec import Spec, ref_spec_6110

REFERENCE_SPEC_GIT_PATH = ref_spec_6110.git_path
REFERENCE_SPEC_VERSION = ref_spec_6110.version


def test_sepolia_extraneous_log(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
):
    """Test sepolia variant logs contract."""
    # Supplant mainnet contract with the Sepolia variant, which emits two logs, one of which
    # has a different data length.
    deposit_request = DepositRequest(
        pubkey=0x01,
        withdrawal_credentials=0x02,
        amount=120_000_000_000_000_000,
        signature=0x03,
        index=0x0,
    )

    bytecode = (
        Op.LOG1(
            # ERC-20 token transfer log
            0,
            32,
            0xDDF252AD1BE2C89B69C2B068FC378DAA952BA7F163C4A11628F55A4DF523B3EF,
        )
        + Om.MSTORE(deposit_request.log)
        + Op.LOG1(
            0,
            len(deposit_request.log),
            0x649BBC62D0E31342AFEA4E5CD82D4049E7E1EE912FC0889AA790803BE39038C5,
        )
        + Op.STOP
    )
    assert len(deposit_request.log) == 576

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
