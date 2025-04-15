"""
abstract: Tests [EIP-7251: Execution layer triggerable consolidation](https://eips.ethereum.org/EIPS/eip-7251)
    Test execution layer triggered exits [EIP-7251: Execution layer triggerable consolidation](https://eips.ethereum.org/EIPS/eip-7251).

"""  # noqa: E501

from typing import List

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Bytecode,
    Transaction,
)
from ethereum_test_tools import Macros as Om
from ethereum_test_tools import Opcodes as Op
from ethereum_test_types import Requests

from .helpers import (
    ConsolidationRequest,
    ConsolidationRequestTransaction,
)
from .spec import Spec as Spec_EIP7251
from .spec import ref_spec_7251

REFERENCE_SPEC_GIT_PATH: str = ref_spec_7251.git_path
REFERENCE_SPEC_VERSION: str = ref_spec_7251.version

pytestmark: pytest.MarkDecorator = pytest.mark.valid_from("Prague")


def consolidation_list_with_custom_fee(n: int) -> List[ConsolidationRequest]:  # noqa: D103
    return [
        ConsolidationRequest(
            source_pubkey=0x01,
            target_pubkey=0x02,
            fee=Spec_EIP7251.get_fee(10),
        )
        for i in range(n)
    ]


@pytest.mark.parametrize(
    "requests_list",
    [
        pytest.param(
            [],
            id="empty_request_list",
        ),
        pytest.param(
            [
                *consolidation_list_with_custom_fee(1),
            ],
            id="1_consolidation_request",
        ),
        pytest.param(
            [
                *consolidation_list_with_custom_fee(2),
            ],
            id="2_consolidation_requests",
        ),
        pytest.param(
            [
                *consolidation_list_with_custom_fee(3),
            ],
            id="3_consolidation_requests",
        ),
        pytest.param(
            [
                *consolidation_list_with_custom_fee(4),
            ],
            id="4_consolidation_requests",
        ),
        pytest.param(
            [
                *consolidation_list_with_custom_fee(5),
            ],
            id="5_consolidation_requests",
        ),
    ],
)
def test_consolidations_asm_modified(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    requests_list: List[ConsolidationRequest],
):
    """Test how clients were to behave when more than 2 consolidations (here: 4 consolidations) would be allowed per block."""  # noqa: E501
    # Source of code (change value of this line to 4 and re-compile with fjl/geas): https://github.com/ethereum/sys-asm/blob/f1c13e285b6aeef2b19793995e00861bf0f32c9a/src/consolidations/main.eas#L31  # noqa: E501, W291
    modified_code: bytes = b"3373fffffffffffffffffffffffffffffffffffffffe1460d35760115f54807fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff1461019a57600182026001905f5b5f82111560685781019083028483029004916001019190604d565b9093900492505050366060146088573661019a573461019a575f5260205ff35b341061019a57600154600101600155600354806004026004013381556001015f358155600101602035815560010160403590553360601b5f5260605f60143760745fa0600101600355005b6003546002548082038060041160e7575060045b5f5b8181146101295782810160040260040181607402815460601b815260140181600101548152602001816002015481526020019060030154905260010160e9565b910180921461013b5790600255610146565b90505f6002555f6003555b5f54807fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff141561017357505f5b6001546001828201116101885750505f61018e565b01600190035b5f555f6001556074025ff35b5f5ffd"  # noqa: E501
    pre[Spec_EIP7251.CONSOLIDATION_REQUEST_PREDEPLOY_ADDRESS] = Account(
        code=modified_code,
        nonce=1,
        balance=0,
    )

    # given a list of consolidation requests construct a consolidation request transaction
    consolidation_request_transaction = ConsolidationRequestTransaction(requests=requests_list)
    # prepare consolidation senders
    consolidation_request_transaction.update_pre(pre=pre)
    # get transaction list
    txs: List[Transaction] = consolidation_request_transaction.transactions()

    blockchain_test(
        pre=pre,
        blocks=[
            Block(
                txs=txs,
                requests_hash=Requests(*requests_list),
            ),
        ],
        post={},
    )


@pytest.mark.parametrize(
    "requests_list",
    [
        pytest.param(
            [],
            id="empty_request_list",
        ),
        pytest.param(
            [
                *consolidation_list_with_custom_fee(1),
            ],
            id="1_consolidation_request",
        ),
        pytest.param(
            [
                *consolidation_list_with_custom_fee(2),
            ],
            id="2_consolidation_requests",
        ),
        pytest.param(
            [
                *consolidation_list_with_custom_fee(3),
            ],
            id="3_consolidation_requests",
        ),
        pytest.param(
            [
                *consolidation_list_with_custom_fee(4),
            ],
            id="4_consolidation_requests",
        ),
        pytest.param(
            [
                *consolidation_list_with_custom_fee(5),
            ],
            id="5_consolidation_requests",
        ),
    ],
)
def test_consolidations_py_modified(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    requests_list: List[ConsolidationRequest],
):
    """Test how clients were to behave when more than 2 consolidations would be allowed per block."""
    modified_code: Bytecode = Bytecode()
    memory_offset: int = 0
    amount_of_requests: int = 0

    for consolidation_request in requests_list:
        # update memory_offset with the correct value
        consolidation_request_bytes_amount: int = len(bytes(consolidation_request))
        assert consolidation_request_bytes_amount == 116, (
            "Expected consolidation request to be of size 116 but got size "
            f"{consolidation_request_bytes_amount}"
        )
        memory_offset += consolidation_request_bytes_amount

        modified_code += Om.MSTORE(bytes(consolidation_request), memory_offset)
        amount_of_requests += 1

    modified_code += Op.RETURN(0, Op.MSIZE())

    pre[Spec_EIP7251.CONSOLIDATION_REQUEST_PREDEPLOY_ADDRESS] = Account(
        code=modified_code,
        nonce=1,
        balance=0,
    )

    # given a list of consolidation requests construct a consolidation request transaction
    consolidation_request_transaction = ConsolidationRequestTransaction(requests=requests_list)
    # prepare consolidation senders
    consolidation_request_transaction.update_pre(pre=pre)
    # get transaction list
    txs: List[Transaction] = consolidation_request_transaction.transactions()

    blockchain_test(
        pre=pre,
        blocks=[
            Block(
                txs=txs,
                requests_hash=Requests(*requests_list),
            ),
        ],
        post={},
    )
