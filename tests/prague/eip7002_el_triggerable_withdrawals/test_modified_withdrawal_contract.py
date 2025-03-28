"""
abstract: Tests [EIP-7002: Execution layer triggerable withdrawals](https://eips.ethereum.org/EIPS/eip-7002)
    Test execution layer triggered exits [EIP-7002: Execution layer triggerable withdrawals](https://eips.ethereum.org/EIPS/eip-7002).

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
from ethereum_test_tools import Opcodes as Op
from ethereum_test_types import Requests

from .helpers import (
    WithdrawalRequest,
    # WithdrawalRequestBase,
    # WithdrawalRequestContract,
    WithdrawalRequestTransaction,
)
from .spec import Spec as Spec_EIP7002
from .spec import ref_spec_7002

REFERENCE_SPEC_GIT_PATH: str = ref_spec_7002.git_path
REFERENCE_SPEC_VERSION: str = ref_spec_7002.version


def single_withdrawal_with_custom_fee(i: int) -> WithdrawalRequest:  # noqa: D103
    return WithdrawalRequest(
        validator_pubkey=i + 1,
        amount=0,
        fee=Spec_EIP7002.get_fee(0),
    )


@pytest.mark.parametrize(
    "requests_list",
    [
        pytest.param(
            [],
            id="empty_request_list",
        ),
        pytest.param(
            [single_withdrawal_with_custom_fee(0)],
            id="1_withdrawal_request",
        ),
        pytest.param(
            [
                *[
                    single_withdrawal_with_custom_fee(i)
                    for i in range(
                        0,
                        15,
                    )
                ],
            ],
            id="15_withdrawal_requests",
        ),
        pytest.param(
            [
                *[
                    single_withdrawal_with_custom_fee(i)
                    for i in range(
                        0,
                        16,
                    )
                ],
            ],
            id="16_withdrawal_requests",
        ),
        pytest.param(
            [
                *[
                    single_withdrawal_with_custom_fee(i)
                    for i in range(
                        0,
                        17,
                    )
                ],
            ],
            id="17_withdrawal_requests",
        ),
        pytest.param(
            [
                *[
                    single_withdrawal_with_custom_fee(i)
                    for i in range(
                        0,
                        18,
                    )
                ],
            ],
            id="18_withdrawal_requests",
        ),
    ],
)
def test_extra_withdrawals(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    requests_list: List[WithdrawalRequest],
):
    """Test how clients were to behave when more than 16 withdrawals would be allowed per block."""
    modified_code: bytes = b"3373fffffffffffffffffffffffffffffffffffffffe1460cb5760115f54807fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff146101f457600182026001905f5b5f82111560685781019083028483029004916001019190604d565b909390049250505036603814608857366101f457346101f4575f5260205ff35b34106101f457600154600101600155600354806003026004013381556001015f35815560010160203590553360601b5f5260385f601437604c5fa0600101600355005b6003546002548082038060121160df575060125b5f5b8181146101835782810160030260040181604c02815460601b8152601401816001015481526020019060020154807fffffffffffffffffffffffffffffffff00000000000000000000000000000000168252906010019060401c908160381c81600701538160301c81600601538160281c81600501538160201c81600401538160181c81600301538160101c81600201538160081c81600101535360010160e1565b910180921461019557906002556101a0565b90505f6002555f6003555b5f54807fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff14156101cd57505f5b6001546002828201116101e25750505f6101e8565b01600290035b5f555f600155604c025ff35b5f5ffd"  # noqa: E501
    pre[Spec_EIP7002.WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS] = Account(
        code=modified_code,
        nonce=1,
        balance=0,
    )

    # given a list of withdrawal requests construct a withdrawal request transaction
    withdrawal_request_transaction = WithdrawalRequestTransaction(requests=requests_list)
    # prepare withdrawal senders
    withdrawal_request_transaction.update_pre(pre=pre)
    # get transaction list
    txs: List[Transaction] = withdrawal_request_transaction.transactions()

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
            [single_withdrawal_with_custom_fee(0)],
            id="1_withdrawal_request",
        ),
        pytest.param(
            [
                *[
                    single_withdrawal_with_custom_fee(i)
                    for i in range(
                        0,
                        15,
                    )
                ],
            ],
            id="15_withdrawal_requests",
        ),
        pytest.param(
            [
                *[
                    single_withdrawal_with_custom_fee(i)
                    for i in range(
                        0,
                        16,
                    )
                ],
            ],
            id="16_withdrawal_requests",
        ),
        pytest.param(
            [
                *[
                    single_withdrawal_with_custom_fee(i)
                    for i in range(
                        0,
                        17,
                    )
                ],
            ],
            id="17_withdrawal_requests",
        ),
        pytest.param(
            [
                *[
                    single_withdrawal_with_custom_fee(i)
                    for i in range(
                        0,
                        18,
                    )
                ],
            ],
            id="18_withdrawal_requests",
        ),
    ],
)
def test_extra_withdrawals_pseudo_contract(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    requests_list: List[WithdrawalRequest],
):
    """Test how clients were to behave when more than 16 withdrawals would be allowed per block."""
    modified_code: Bytecode = Bytecode()
    memory_offset: int = 0
    amount_of_requests: int = 0

    # Goal: Have contract return a bunch of withdrawal requests
    #   Problem: EVM has no concept of withdrawal request, it just return bytes from memory
    #       Problem: How to get __bytes__ from withdrawal request
    #       Problem: How to know exact size of withdrawal requests byte representation
    #       Problem: If size larger than 32 bytes how to split across multiple MSTOREs?

    # what size does a withdrawal_request bytes representation have?
    #   withdrawal_request.__bytes__:
    #             bytes(self.source_address)            ->          20 bytes
    #           + bytes(self.validator_pubkey)          ->          48 bytes
    #           + self.amount.to_bytes(8, "little")     ->          8 bytes
    #                                                   -> Total:   76 bytes
    for withdrawal_request in requests_list:
        withdrawal_request_chunk_1_3_32bytes: bytes = withdrawal_request.__bytes__()[:32]
        withdrawal_request_chunk_2_3_32bytes: bytes = withdrawal_request.__bytes__()[32:64]
        withdrawal_request_chunk_3_3_12bytes: bytes = withdrawal_request.__bytes__()[64:]

        modified_code += Op.MSTORE(memory_offset, withdrawal_request_chunk_1_3_32bytes)
        memory_offset += 32

        modified_code += Op.MSTORE(memory_offset, withdrawal_request_chunk_2_3_32bytes)
        memory_offset += 32

        modified_code += Op.MSTORE(memory_offset, withdrawal_request_chunk_3_3_12bytes)
        # memory_offset += 32  # MSTORE ALWAYS writes 32 bytes, no need to update memory offset tho

        amount_of_requests += 1

    modified_code += Op.RETURN(
        0, 76 * amount_of_requests
    )  # don't care about the zeroes added by MSTORE at [76,96] bytes

    pre[Spec_EIP7002.WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS] = Account(
        code=modified_code,
        nonce=1,
        balance=0,
    )

    # given a list of withdrawal requests construct a withdrawal request transaction
    withdrawal_request_transaction = WithdrawalRequestTransaction(requests=requests_list)
    # prepare withdrawal senders
    withdrawal_request_transaction.update_pre(pre=pre)
    # get transaction list
    txs: List[Transaction] = withdrawal_request_transaction.transactions()

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
