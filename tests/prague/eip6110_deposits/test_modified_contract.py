"""Test variants of the deposit contract which adheres the log-style as described in EIP-6110."""

import pytest

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

from .helpers import DepositRequest, create_deposit_log_bytes
from .spec import Spec, ref_spec_6110

REFERENCE_SPEC_GIT_PATH = ref_spec_6110.git_path
REFERENCE_SPEC_VERSION = ref_spec_6110.version


@pytest.mark.parametrize(
    "include_deposit_event",
    [
        pytest.param(True),
        pytest.param(False),
    ],
)
def test_extra_logs(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    include_deposit_event: bool,
):
    """Test deposit contract emitting more log event types than the ones in mainnet."""
    # Supplant mainnet contract with a variant that emits a `Transfer`` log
    # If `include_deposit_event` is `True``, it will also emit a `DepositEvent` log`
    deposit_request = DepositRequest(
        pubkey=0x01,
        withdrawal_credentials=0x02,
        amount=120_000_000_000_000_000,
        signature=0x03,
        index=0x0,
    )
    deposit_request_log = create_deposit_log_bytes(
        pubkey_data=bytes(deposit_request.pubkey),
        withdrawal_credentials_data=bytes(deposit_request.withdrawal_credentials),
        # Note: after converting to bytes, it is converted to little-endian by `[::-1]`
        # (This happens on-chain also, but this is done by the solidity contract)
        amount_data=bytes.fromhex("0" + deposit_request.amount.hex()[2:])[::-1],
        signature_data=bytes(deposit_request.signature),
        index_data=bytes(),
    )

    # ERC20 token transfer log (Sepolia)
    # https://sepolia.etherscan.io/tx/0x2d71f3085a796a0539c9cc28acd9073a67cf862260a41475f000dd101279f94f
    # JSON RPC:
    # curl https://sepolia.infura.io/v3/APIKEY \
    # -X POST \
    # -H "Content-Type: application/json" \
    # -d '{"jsonrpc": "2.0", "method": "eth_getLogs",
    # "params": [{"address": "0x7f02C3E3c98b133055B8B348B2Ac625669Ed295D",
    # "blockHash": "0x8062a17fa791f5dbd59ea68891422e3299ca4e80885a89acf3fc706c8bceef53"}],
    # "id": 1}'

    # {"jsonrpc":"2.0","id":1,"result":
    # [{"removed":false,"logIndex":"0x80","transactionIndex":"0x56",
    # "transactionHash":"0x2d71f3085a796a0539c9cc28acd9073a67cf862260a41475f000dd101279f94f",
    # "blockHash":"0x8062a17fa791f5dbd59ea68891422e3299ca4e80885a89acf3fc706c8bceef53",
    # "blockNumber":"0x794fb5",
    # "address":"0x7f02c3e3c98b133055b8b348b2ac625669ed295d",
    # "data":"0x0000000000000000000000000000000000000000000000000000000000000001",
    # "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
    # "0x0000000000000000000000006885e36bfcb68cb383dfe90023a462c03bcb2ae5",
    # "0x00000000000000000000000080b5dc88c98e528bf9cb4b7f0f076ac41da24651"]

    bytecode = Op.LOG3(
        # ERC-20 token transfer log
        # ERC-20 token transfers are LOG3, since the topic, the sender, and receiver
        # are all topics (the sender and receiver are `indexed` in the solidity event)
        0,
        32,
        0xDDF252AD1BE2C89B69C2B068FC378DAA952BA7F163C4A11628F55A4DF523B3EF,
        0x000000000000000000000000AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,
        0x000000000000000000000000BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB,
    )

    requests = Requests()

    if include_deposit_event:
        bytecode += Om.MSTORE(deposit_request_log) + Op.LOG1(
            0,
            len(deposit_request_log),
            Spec.DEPOSIT_EVENT_SIGNATURE_HASH,
        )
        requests = Requests(deposit_request)
    bytecode += Op.STOP

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
                    requests_hash=requests,
                ),
            ),
        ],
        post={},
    )
