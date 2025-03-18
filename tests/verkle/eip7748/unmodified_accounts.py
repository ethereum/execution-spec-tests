"""
abstract: Tests [EIP-7748: State conversion to Verkle Tree]
(https://eips.ethereum.org/EIPS/eip-7748)
    Tests for [EIP-7748: State conversion to Verkle Tree]
    (https://eips.ethereum.org/EIPS/eip-7748).
"""

import pytest
import math
from typing import Optional

from ethereum_test_tools import BlockchainTestFiller
from .utils import AccountConfig, stride, _generic_conversion

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7748.md"
REFERENCE_SPEC_VERSION = "TODO"


@pytest.mark.valid_from("EIP6800Transition")
@pytest.mark.parametrize(
    "account_configs",
    [
        [AccountConfig(0, 0)],
        [AccountConfig(0, 0)] * 2,
        [AccountConfig(0, 0)] * stride,
        [AccountConfig(15, 2)],
        [AccountConfig(31 * 2 + 1, 3)],  # 3 code-chunks + 3 slots + account data = stride
        [AccountConfig(0, 0), AccountConfig(15, 2)],
        [
            AccountConfig(0, 0),
            AccountConfig(31 + 1, 3),
        ],
        [
            AccountConfig(15, 2),
            AccountConfig(0, 0),
        ],
        [
            AccountConfig(31 + 1, 3),
            AccountConfig(0, 0),
        ],
        [
            AccountConfig(5, 1),
            AccountConfig(8, 1),
        ],
        [
            AccountConfig(5, 2),
            AccountConfig(8, 1),
        ],
        [AccountConfig(0, stride - 1)],
    ],
    ids=[
        "EOA",
        "EOAs under-fit",
        "EOAs perfect-fit",
        "Contract under-fit",
        "Contract perfect-fit",
        "EOA and Contract under-fit",
        "EOA and Contract perfect-fit",
        "Contract and EOA under-fit",
        "Contract and EOA perfect-fit",
        "Contract and Contract under-fit",
        "Contract and Contract perfect-fit",
        "Empty code with storage slots perfect-fit",
    ],
)
@pytest.mark.parametrize(
    "fill_first_block",
    [True, False],
)
@pytest.mark.parametrize(
    "fill_last_block",
    [True, False],
)
def test_non_partial(
    blockchain_test: BlockchainTestFiller,
    account_configs: list[AccountConfig],
    fill_first_block: bool,
    fill_last_block: bool,
):
    """
    Test non-partial account conversions.
    """
    _generic_conversion(blockchain_test, account_configs, fill_first_block, fill_last_block)


@pytest.mark.valid_from("EIP6800Transition")
@pytest.mark.parametrize(
    "storage_slots_overlow",
    [
        2,
        1,
        0,
    ],
    ids=[
        "Two storage slots overflowed to next block",
        "One storage slot overflowed to next block",
        "Storage slots fit in one block",
    ],
)
@pytest.mark.parametrize(
    "account_prefix",
    [
        None,
        AccountConfig(0, 0),
        AccountConfig(10, 1),
    ],
    ids=[
        "No prefix",
        "EOA prefix",
        "Contract prefix",
    ],
)
@pytest.mark.parametrize(
    "empty_code",
    [True, False],
)
@pytest.mark.parametrize(
    "fill_first_block",
    [True, False],
)
@pytest.mark.parametrize(
    "fill_last_block",
    [True, False],
)
def test_partial(
    blockchain_test: BlockchainTestFiller,
    storage_slots_overlow: int,
    account_prefix: Optional[AccountConfig],
    empty_code: bool,
    fill_first_block: bool,
    fill_last_block: bool,
):
    """
    Test partial account conversions.
    """
    conversion_unit_offset = 0
    account_configs = []
    if account_prefix is not None:
        conversion_unit_offset += 1  # Account basic data
        conversion_unit_offset += math.ceil(account_prefix.code_length / 31)  # Code-chunks
        conversion_unit_offset += account_prefix.storage_slots_count
        account_configs.append(account_prefix)

    code_length = 0 if empty_code else 31
    # For the `stride` quota in this block, we already used `conversion_unit_offset` units from the accounts prefixes.
    # For the remaining quota (i.e., `stride-conversion_unit_offset`), we should configure the contract having
    # `(stride - conversion_unit_offset)+storage_slots_overlow` so we can overflow the desired storage slots to the
    # next block.
    num_storage_slots = stride - conversion_unit_offset + storage_slots_overlow
    account_configs.append(AccountConfig(code_length, num_storage_slots))

    _generic_conversion(blockchain_test, account_configs, fill_first_block, fill_last_block)


@pytest.mark.valid_from("EIP6800Transition")
@pytest.mark.parametrize(
    "account_configs",
    [
        [AccountConfig(31 * (stride + 10) + 1, 4)],
        [AccountConfig(31 * (stride + 3), 1), AccountConfig(0, 0)],
    ],
    ids=[
        "Stride overflow",
        "Stride overflow followed by EOA",
    ],
)
@pytest.mark.parametrize(
    "fill_first_block",
    [False, True],
)
@pytest.mark.parametrize(
    "fill_last_block",
    [False, True],
)
def test_codechunks_stride_overflow(
    blockchain_test: BlockchainTestFiller,
    account_configs: list[AccountConfig],
    fill_first_block: bool,
    fill_last_block: bool,
):
    """
    Test code-chunks stride overflow.
    """
    _generic_conversion(blockchain_test, account_configs, fill_first_block, fill_last_block)


# @pytest.mark.skip("stride config not supported yet")
# @pytest.mark.valid_from("EIP6800Transition")
# @pytest.mark.parametrize(
#     "fcb, stride, num_expected_blocks",
#     [
#         (True, 1, 2),
#         (True, 2, 1),
#         (False, 1, 1),
#         (False, 2, 1),
#     ],
# )
# def test_empty_account(
#     blockchain_test: BlockchainTestFiller,
#     fcb: bool,
#     stride: int,
#     num_expected_blocks: int,
# ):
#     """
#     Test EIP-161 accounts.
#     """
#     pre_state = {}
#     if not fcb:
#         pre_state[Account0] = Account(balance=1000)

#     # Empty account (EIP-161)
#     pre_state[Account1] = Account(
#         balance=0,
#         nonce=0,
#         storage={0: 0x1, 1: 0x2},
#     )

#     pre_state[Account2] = Account(balance=1001)

#     _state_conversion(blockchain_test, pre_state, stride, num_expected_blocks)


# @pytest.mark.skip("stride config not supported yet")
# @pytest.mark.valid_from("EIP6800Transition")
# @pytest.mark.parametrize(
#     "fcb, stride, num_expected_blocks",
#     [
#         (True, 1, 2),
#         (True, 2, 1),
#         (False, 1, 1),
#     ],
# )
# def test_last_conversion_block(
#     blockchain_test: BlockchainTestFiller,
#     fcb: bool,
#     stride: int,
#     num_expected_blocks: int,
# ):
#     """
#     Test last conversion block scenario.
#     """
#     pre_state = {}
#     if not fcb:
#         pre_state[Account0] = Account(balance=1000)

#     # Empty account (EIP-161)
#     pre_state[Account1] = Account(
#         balance=0,
#         nonce=0,
#         storage={0: 0x1, 1: 0x2},
#     )

#     _state_conversion(blockchain_test, pre_state, stride, num_expected_blocks)
