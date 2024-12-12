"""
abstract: Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
    Tests correct excess blob gas calculation given the dynamic uncoupled blob count of [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
    This file is based on the EIP-4844 tests of the same name, but modified to test the EIP-7742.
"""  # noqa: E501

import itertools
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Tuple

import pytest

from ethereum_test_tools import (
    EOA,
    Account,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    BlockException,
    Bytecode,
    Environment,
    Hash,
    Header,
)
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import Transaction, add_kzg_version

from .spec import Spec, SpecHelpers, ref_spec_7742

REFERENCE_SPEC_GIT_PATH = ref_spec_7742.git_path
REFERENCE_SPEC_VERSION = ref_spec_7742.version

# All tests run from Prague fork
pytestmark = pytest.mark.valid_from("Prague")


@pytest.fixture
def parent_excess_blobs() -> int:  # noqa: D103
    """
    By default we start with an intermediate value between the target and max.
    """
    return (Spec.PRAGUE_MAX_BLOBS_PER_BLOCK + Spec.PRAGUE_TARGET_BLOBS_PER_BLOCK) // 2 + 1


@pytest.fixture
def parent_excess_blob_gas(parent_excess_blobs: int) -> int:  # noqa: D103
    return parent_excess_blobs * Spec.GAS_PER_BLOB


@pytest.fixture
def parent_target_blobs() -> int:  # noqa: D103
    return Spec.PRAGUE_TARGET_BLOBS_PER_BLOCK


@pytest.fixture
def target_blobs() -> int:  # noqa: D103
    return Spec.PRAGUE_TARGET_BLOBS_PER_BLOCK


@pytest.fixture
def correct_excess_blob_gas(  # noqa: D103
    parent_excess_blob_gas: int,
    parent_blobs: int,
    parent_target_blobs: int,
) -> int:
    return SpecHelpers.calc_excess_blob_gas_from_blob_count(
        parent_excess_blob_gas=parent_excess_blob_gas,
        parent_blob_count=parent_blobs,
        parent_target_blobs_per_block=parent_target_blobs,
    )


@pytest.fixture
def header_excess_blobs_delta() -> Optional[int]:  # noqa: D103
    return None


@pytest.fixture
def header_excess_blob_gas_delta() -> Optional[int]:  # noqa: D103
    return None


@pytest.fixture
def header_excess_blob_gas(  # noqa: D103
    correct_excess_blob_gas: int,
    header_excess_blobs_delta: Optional[int],
    header_excess_blob_gas_delta: Optional[int],
) -> Optional[int]:
    if header_excess_blobs_delta is not None:
        modified_excess_blob_gas = correct_excess_blob_gas + (
            header_excess_blobs_delta * Spec.GAS_PER_BLOB
        )
        if modified_excess_blob_gas < 0:
            modified_excess_blob_gas = 2**64 + (modified_excess_blob_gas)
        return modified_excess_blob_gas
    if header_excess_blob_gas_delta is not None:
        return correct_excess_blob_gas + header_excess_blob_gas_delta
    return None


@pytest.fixture
def block_fee_per_blob_gas(  # noqa: D103
    correct_excess_blob_gas: int,
) -> int:
    return Spec.get_blob_gasprice(excess_blob_gas=correct_excess_blob_gas)


@pytest.fixture
def block_base_fee() -> int:  # noqa: D103
    return 7


@pytest.fixture
def genesis_environment(  # noqa: D103
    parent_excess_blob_gas: int,
    parent_target_blobs: int,
    parent_blobs: int,
    block_base_fee: int,
) -> Environment:
    if parent_blobs == 0:
        # No extra block necessary
        return Environment(
            excess_blob_gas=parent_excess_blob_gas,
            base_fee_per_gas=block_base_fee,
            target_blobs_per_block=parent_target_blobs,
        )
    else:
        # Intermediate block containing blobs between genesis and test block
        return Environment(
            # We set the target to zero so the intermediate block will have the same excess blob
            # gas as the genesis
            excess_blob_gas=parent_excess_blob_gas,
            base_fee_per_gas=block_base_fee,
            target_blobs_per_block=0,
        )


@pytest.fixture
def non_zero_blob_gas_used_genesis_block(
    pre: Alloc,
    genesis_environment: Environment,
    parent_blobs: int,
    parent_excess_blob_gas: int,
    parent_target_blobs: int,
    tx_max_fee_per_gas: int,
) -> Block | None:
    """
    For test cases with a non-zero blobGasUsed field in the
    original genesis block header we must instead utilize an
    intermediate block to act on its behalf.

    Genesis blocks with a non-zero blobGasUsed field are invalid as
    they do not have any blob txs.

    For the intermediate block to align with default genesis values,
    we must add TARGET_BLOB_GAS_PER_BLOCK to the excessBlobGas of the
    genesis value, expecting an appropriate drop to the intermediate block.
    Similarly, we must add parent_blobs to the intermediate block within
    a blob tx such that an equivalent blobGasUsed field is wrote.
    """
    if parent_blobs == 0:
        return None

    genesis_excess_blob_gas = genesis_environment.excess_blob_gas
    assert genesis_excess_blob_gas is not None, "genesis excess blob gas is None"
    genesis_target_blobs_per_block = genesis_environment.target_blobs_per_block
    assert genesis_target_blobs_per_block is not None, "genesis target blobs per block is None"
    assert parent_excess_blob_gas == SpecHelpers.calc_excess_blob_gas_from_blob_count(
        parent_excess_blob_gas=genesis_excess_blob_gas,
        parent_blob_count=0,
        parent_target_blobs_per_block=genesis_target_blobs_per_block,
    ), "parent excess blob gas is incorrect"

    sender = pre.fund_eoa(10**27)

    # Address that contains no code, nor balance and is not a contract.
    empty_account_destination = pre.fund_eoa(0)

    return Block(
        txs=[
            Transaction(
                ty=Spec.BLOB_TX_TYPE,
                sender=sender,
                to=empty_account_destination,
                value=1,
                gas_limit=21_000,
                max_fee_per_gas=tx_max_fee_per_gas,
                max_priority_fee_per_gas=0,
                max_fee_per_blob_gas=Spec.get_blob_gasprice(
                    excess_blob_gas=parent_excess_blob_gas
                ),
                access_list=[],
                blob_versioned_hashes=add_kzg_version(
                    [Hash(x) for x in range(parent_blobs)],
                    Spec.BLOB_COMMITMENT_VERSION_KZG,
                ),
            )
        ],
        target_blobs_per_block=parent_target_blobs,
        header_verify=Header(
            excess_blob_gas=parent_excess_blob_gas,
        ),
    )


@pytest.fixture
def tx_max_fee_per_gas(  # noqa: D103
    block_base_fee: int,
) -> int:
    return block_base_fee


@pytest.fixture
def tx_max_fee_per_blob_gas(  # noqa: D103
    block_fee_per_blob_gas: int,
) -> int:
    return block_fee_per_blob_gas


@pytest.fixture
def tx_data_cost(  # noqa: D103
    tx_max_fee_per_blob_gas: int,
    new_blobs: int,
) -> int:
    return tx_max_fee_per_blob_gas * Spec.GAS_PER_BLOB * new_blobs


@pytest.fixture
def tx_value() -> int:  # noqa: D103
    return 1


@pytest.fixture
def tx_gas_limit() -> int:  # noqa: D103
    return 45000


@pytest.fixture
def tx_exact_cost(  # noqa: D103
    tx_value: int, tx_max_fee_per_gas: int, tx_data_cost: int, tx_gas_limit: int
) -> int:
    return (tx_gas_limit * tx_max_fee_per_gas) + tx_value + tx_data_cost


@pytest.fixture
def destination_account_bytecode() -> Bytecode:  # noqa: D103
    # Verify that the BLOBBASEFEE opcode reflects the current blob gas cost
    return Op.SSTORE(0, Op.BLOBBASEFEE)


@pytest.fixture
def destination_account(  # noqa: D103
    pre: Alloc,
    destination_account_bytecode: Bytecode,
) -> Address:
    return pre.deploy_contract(destination_account_bytecode)


@pytest.fixture
def sender(pre: Alloc, tx_exact_cost: int) -> Address:  # noqa: D103
    return pre.fund_eoa(tx_exact_cost)


@pytest.fixture
def post(  # noqa: D103
    destination_account: Address, tx_value: int, block_fee_per_blob_gas: int
) -> Mapping[Address, Account]:
    return {
        destination_account: Account(
            storage={0: block_fee_per_blob_gas},
            balance=tx_value,
        ),
    }


@pytest.fixture
def tx(  # noqa: D103
    sender: EOA,
    new_blobs: int,
    tx_max_fee_per_gas: int,
    tx_max_fee_per_blob_gas: int,
    tx_gas_limit: int,
    destination_account: Address,
):
    if new_blobs == 0:
        # Send a normal type two tx instead
        return Transaction(
            ty=2,
            sender=sender,
            to=destination_account,
            value=1,
            gas_limit=tx_gas_limit,
            max_fee_per_gas=tx_max_fee_per_gas,
            max_priority_fee_per_gas=0,
            access_list=[],
        )
    else:
        return Transaction(
            ty=Spec.BLOB_TX_TYPE,
            sender=sender,
            to=destination_account,
            value=1,
            gas_limit=tx_gas_limit,
            max_fee_per_gas=tx_max_fee_per_gas,
            max_priority_fee_per_gas=0,
            max_fee_per_blob_gas=tx_max_fee_per_blob_gas,
            access_list=[],
            blob_versioned_hashes=add_kzg_version(
                [Hash(x) for x in range(new_blobs)],
                Spec.BLOB_COMMITMENT_VERSION_KZG,
            ),
        )


@pytest.fixture
def header_blob_gas_used() -> Optional[int]:  # noqa: D103
    return None


@pytest.fixture
def correct_blob_gas_used(  # noqa: D103
    tx: Transaction,
) -> int:
    return Spec.get_total_blob_gas(tx)


@pytest.fixture
def blocks(  # noqa: D103
    tx: Transaction,
    header_excess_blob_gas: Optional[int],
    header_blob_gas_used: Optional[int],
    correct_excess_blob_gas: int,
    correct_blob_gas_used: int,
    non_zero_blob_gas_used_genesis_block: Block,
    target_blobs: int,
    parent_target_blobs: int,
):
    blocks = (
        []
        if non_zero_blob_gas_used_genesis_block is None
        else [non_zero_blob_gas_used_genesis_block]
    )

    header_modifier: Dict | None = None
    exception_message: BlockException | List[BlockException] | None = None

    if header_excess_blob_gas is not None:
        header_modifier = {"excess_blob_gas": header_excess_blob_gas}
        exception_message = BlockException.INCORRECT_EXCESS_BLOB_GAS
    elif header_blob_gas_used is not None:
        header_modifier = {"blob_gas_used": header_blob_gas_used}
        exception_message = (
            [
                BlockException.BLOB_GAS_USED_ABOVE_LIMIT,
                BlockException.INCORRECT_BLOB_GAS_USED,
            ]
            if header_blob_gas_used > target_blobs
            else BlockException.INCORRECT_BLOB_GAS_USED
        )

    blocks.append(
        Block(
            txs=[tx],
            rlp_modifier=Header(**header_modifier) if header_modifier else None,
            header_verify=Header(
                excess_blob_gas=correct_excess_blob_gas,
                blob_gas_used=correct_blob_gas_used,
            ),
            exception=exception_message,
            target_blobs_per_block=target_blobs,
        )
    )

    return blocks


BLOB_COMBINATIONS_PRAGUE = [
    0,
    1,
    Spec.PRAGUE_TARGET_BLOBS_PER_BLOCK - 1,
    Spec.PRAGUE_TARGET_BLOBS_PER_BLOCK,
    Spec.PRAGUE_TARGET_BLOBS_PER_BLOCK + 1,
    Spec.PRAGUE_MAX_BLOBS_PER_BLOCK,
    Spec.PRAGUE_MAX_BLOBS_PER_BLOCK + 1,
]


@pytest.mark.parametrize("parent_blobs", BLOB_COMBINATIONS_PRAGUE)
@pytest.mark.parametrize("parent_excess_blobs", BLOB_COMBINATIONS_PRAGUE)
@pytest.mark.parametrize("parent_target_blobs", BLOB_COMBINATIONS_PRAGUE)
@pytest.mark.parametrize("new_blobs", [1])
def test_correct_excess_blob_gas_calculation(
    blockchain_test: BlockchainTestFiller,
    genesis_environment: Environment,
    pre: Mapping[Address, Account],
    blocks: List[Block],
    post: Mapping[Address, Account],
    correct_excess_blob_gas: int,
):
    """
    Test calculation of the `excessBlobGas` increase/decrease across
    multiple blocks with and without blobs:

    - With parent block containing `[0, MAX_BLOBS_PER_BLOCK]` blobs
    - With parent block containing `[0, (MAX_BLOBS_PER_BLOCK - TARGET_BLOBS_PER_BLOCK)]`
      equivalent value of excess blob gas
    """  # noqa: E501
    blockchain_test(
        pre=pre,
        post=post,
        blocks=blocks,
        genesis_environment=genesis_environment,
        tag=f"expected_excess_blob_gas:{hex(correct_excess_blob_gas)}",
    )


# BLOB_GAS_COST_INCREASES = [
#     SpecHelpers.get_min_excess_blobs_for_blob_gas_price(i)
#     for i in [
#         2,  # First blob gas cost increase
#         2**32 // Spec.GAS_PER_BLOB,  # Data tx wei cost 2^32
#         2**32,  # blob gas cost 2^32
#         2**64 // Spec.GAS_PER_BLOB,  # Data tx wei cost 2^64
#         2**64,  # blob gas cost 2^64
#         (
#             120_000_000 * (10**18) // Spec.GAS_PER_BLOB
#         ),  # Data tx wei is current total Ether supply
#     ]
# ]


# @pytest.mark.parametrize(
#     "parent_excess_blobs",
#     [g - 1 for g in BLOB_GAS_COST_INCREASES],
# )
# @pytest.mark.parametrize("parent_blobs", [SpecHelpers.target_blobs_per_block() + 1])
# @pytest.mark.parametrize("new_blobs", [1])
# def test_correct_increasing_blob_gas_costs(
#     blockchain_test: BlockchainTestFiller,
#     genesis_environment: Environment,
#     pre: Mapping[Address, Account],
#     blocks: List[Block],
#     post: Mapping[Address, Account],
#     correct_excess_blob_gas: int,
# ):
#     """
#     Test calculation of the `excessBlobGas` and blob gas tx costs at
#     value points where the cost increases to interesting amounts:

#     - At the first blob gas cost increase (1 to 2)
#     - At total transaction data cost increase to `> 2^32`
#     - At blob gas wei cost increase to `> 2^32`
#     - At total transaction data cost increase to `> 2^64`
#     - At blob gas wei cost increase to `> 2^64`
#     - At blob gas wei cost increase of around current total Ether supply
#     """
#     blockchain_test(
#         pre=pre,
#         post=post,
#         blocks=blocks,
#         genesis_environment=genesis_environment,
#         tag=f"expected_excess_blob_gas:{hex(correct_excess_blob_gas)}",
#     )


# @pytest.mark.parametrize(
#     "parent_excess_blobs",
#     [g for g in BLOB_GAS_COST_INCREASES],
# )
# @pytest.mark.parametrize("parent_blobs", [SpecHelpers.target_blobs_per_block() - 1])
# @pytest.mark.parametrize("new_blobs", [1])
# def test_correct_decreasing_blob_gas_costs(
#     blockchain_test: BlockchainTestFiller,
#     genesis_environment: Environment,
#     pre: Mapping[Address, Account],
#     blocks: List[Block],
#     post: Mapping[Address, Account],
#     correct_excess_blob_gas: int,
# ):
#     """
#     Test calculation of the `excessBlobGas` and blob gas tx costs at
#     value points where the cost decreases to interesting amounts.

#     See test_correct_increasing_blob_gas_costs.
#     """
#     blockchain_test(
#         pre=pre,
#         post=post,
#         blocks=blocks,
#         genesis_environment=genesis_environment,
#         tag=f"expected_excess_blob_gas:{hex(correct_excess_blob_gas)}",
#     )


def generate_excess_blobs_combinations(
    *,
    expected_excess_blobs: int | List[int] | None = None,
    expected_excess_blobs_delta: int | List[int] | None = None,
    parent_excess_blobs_values: Iterable[int]
    | range = range(0, Spec.PRAGUE_MAX_BLOBS_PER_BLOCK + 1),
    parent_blobs_values: Iterable[int] | range = range(0, Spec.PRAGUE_MAX_BLOBS_PER_BLOCK + 1),
    target_blobs_values: Iterable[int] | range = range(0, Spec.PRAGUE_MAX_BLOBS_PER_BLOCK + 1),
) -> Iterator[Tuple[int, int, int]]:
    """
    Returns all parent_excess_blobs+parent_blobs+target_blobs combinations given
    the expected excess blobs.
    """
    if expected_excess_blobs is None and expected_excess_blobs_delta is None:
        raise Exception("invalid test case")

    if expected_excess_blobs is not None and isinstance(expected_excess_blobs, int):
        expected_excess_blobs = [expected_excess_blobs]

    if expected_excess_blobs_delta is not None and isinstance(expected_excess_blobs_delta, int):
        expected_excess_blobs_delta = [expected_excess_blobs_delta]

    def calculate_excess_blobs(
        parent_excess_blobs: int, parent_blobs: int, target_blobs: int
    ) -> int:
        if parent_excess_blobs + parent_blobs < target_blobs:
            return 0
        return parent_excess_blobs + parent_blobs - target_blobs

    for parent_excess_blobs in parent_excess_blobs_values:
        for parent_blobs in parent_blobs_values:
            for target_blobs in target_blobs_values:
                new_excess_blobs = calculate_excess_blobs(
                    parent_excess_blobs, parent_blobs, target_blobs
                )
                if (
                    expected_excess_blobs is not None and new_excess_blobs in expected_excess_blobs
                ) or (
                    expected_excess_blobs_delta is not None
                    and new_excess_blobs - parent_excess_blobs in expected_excess_blobs_delta
                ):
                    yield (parent_excess_blobs, parent_blobs, target_blobs)


@pytest.mark.parametrize(
    "parent_excess_blobs,parent_blobs,parent_target_blobs",
    generate_excess_blobs_combinations(
        # Test all combinations where the calculated excess blobs for the block should be non-zero
        expected_excess_blobs=1,
        parent_excess_blobs_values=BLOB_COMBINATIONS_PRAGUE,
        parent_blobs_values=BLOB_COMBINATIONS_PRAGUE,
        target_blobs_values=BLOB_COMBINATIONS_PRAGUE,
    ),
)
@pytest.mark.parametrize("header_excess_blob_gas", [0])
@pytest.mark.parametrize("new_blobs", [0, 1])
def test_invalid_zero_excess_blob_gas_in_header(
    blockchain_test: BlockchainTestFiller,
    genesis_environment: Environment,
    pre: Mapping[Address, Account],
    blocks: List[Block],
    correct_excess_blob_gas: int,
    header_excess_blob_gas: Optional[int],
):
    """
    Test rejection of blocks where the `excessBlobGas` in the header drops to
    zero in a block with or without data blobs, but the excess blobs in the parent are
    greater than the current block's target.
    """
    if header_excess_blob_gas is None:
        raise Exception("test case is badly formatted")

    if header_excess_blob_gas == correct_excess_blob_gas:
        raise Exception("invalid test case")

    blockchain_test(
        pre=pre,
        post={},
        blocks=blocks,
        genesis_environment=genesis_environment,
        tag="-".join(
            [
                f"correct:{hex(correct_excess_blob_gas)}",
                f"header:{hex(header_excess_blob_gas)}",
            ]
        ),
    )


@pytest.mark.parametrize(
    "header_excess_blobs_delta,parent_blobs",
    [
        pytest.param(
            -1,
            0,
            id="zero_blobs_decrease_more_than_expected",
        ),
        pytest.param(
            +1,
            Spec.PRAGUE_MAX_BLOBS_PER_BLOCK,
            id="max_blobs_increase_more_than_expected",
        ),
        pytest.param(
            +1,
            Spec.PRAGUE_MAX_BLOBS_PER_BLOCK + 1,
            id="above_max_blobs_increase_more_than_expected",
        ),
    ],
)
@pytest.mark.parametrize("parent_target_blobs", BLOB_COMBINATIONS_PRAGUE)
@pytest.mark.parametrize("parent_excess_blobs", [Spec.PRAGUE_MAX_BLOBS_PER_BLOCK * 2])
@pytest.mark.parametrize("new_blobs", [1])
def test_invalid_excess_blob_gas_above_target_change(
    blockchain_test: BlockchainTestFiller,
    genesis_environment: Environment,
    pre: Mapping[Address, Account],
    blocks: List[Block],
    correct_excess_blob_gas: int,
    header_excess_blob_gas: Optional[int],
):
    """
    Test rejection of blocks where the `excessBlobGas`

    - decreases more than current block's blob target in a single block with zero blobs
    - increases more than the parent block's blobs minus the current block's blob target in a
      single block
    """
    if header_excess_blob_gas is None:
        raise Exception("test case is badly formatted")

    if header_excess_blob_gas == correct_excess_blob_gas:
        raise Exception("invalid test case")

    blockchain_test(
        pre=pre,
        post={},
        blocks=blocks,
        genesis_environment=genesis_environment,
        tag="-".join(
            [
                f"correct:{hex(correct_excess_blob_gas)}",
                f"header:{hex(header_excess_blob_gas)}",
            ]
        ),
    )


# def all_invalid_blob_gas_used_combinations() -> Iterator[Tuple[int, int]]:
#     """
#     Returns all invalid blob gas used combinations.
#     """
#     for new_blobs in range(0, SpecHelpers.max_blobs_per_block() + 1):
#         for header_blob_gas_used in range(0, SpecHelpers.max_blobs_per_block() + 1):
#             if new_blobs != header_blob_gas_used:
#                 yield (new_blobs, header_blob_gas_used * Spec.GAS_PER_BLOB)
#         yield (new_blobs, 2**64 - 1)


# @pytest.mark.parametrize(
#     "new_blobs,header_blob_gas_used",
#     all_invalid_blob_gas_used_combinations(),
# )
# @pytest.mark.parametrize("parent_blobs", [0])
# def test_invalid_blob_gas_used_in_header(
#     blockchain_test: BlockchainTestFiller,
#     genesis_environment: Environment,
#     pre: Mapping[Address, Account],
#     blocks: List[Block],
#     new_blobs: int,
#     header_blob_gas_used: Optional[int],
# ):
#     """
#     Test rejection of blocks where the `blobGasUsed` in the header is invalid:

#     - `blobGasUsed` is not equal to the number of data blobs in the block
#     - `blobGasUsed` is the max uint64 value
#     """
#     if header_blob_gas_used is None:
#         raise Exception("test case is badly formatted")
#     blockchain_test(
#         pre=pre,
#         post={},
#         blocks=blocks,
#         genesis_environment=genesis_environment,
#         tag="-".join(
#             [
#                 f"correct:{hex(new_blobs * Spec.GAS_PER_BLOB)}",
#                 f"header:{hex(header_blob_gas_used)}",
#             ]
#         ),
#     )


@pytest.mark.parametrize(
    "parent_blobs,parent_target_blobs",
    itertools.permutations(BLOB_COMBINATIONS_PRAGUE, 2),
)
@pytest.mark.parametrize(
    "parent_excess_blobs",
    BLOB_COMBINATIONS_PRAGUE[1:],
)  # Zero parent excess blobs results in zero excess blobs for some cases
@pytest.mark.parametrize("new_blobs", [1])
def test_invalid_static_excess_blob_gas(
    blockchain_test: BlockchainTestFiller,
    genesis_environment: Environment,
    pre: Mapping[Address, Account],
    blocks: List[Block],
    correct_excess_blob_gas: int,
    parent_excess_blob_gas: int,
):
    """
    Test rejection of blocks where the `excessBlobGas` remains unchanged
    but the parent blobs included are different from the current block target.

    Test is parametrized with different values for the current block's target blobs,
    so that the parent blobs are always different than this value.

    Parent excess blobs is always greater than zero to ensure that the expected
    excess blobs do not result equal to the previous excess blobs due to subtraction.
    """
    assert correct_excess_blob_gas != parent_excess_blob_gas
    blocks[-1].rlp_modifier = Header(excess_blob_gas=parent_excess_blob_gas)
    blocks[-1].header_verify = None
    blocks[-1].exception = BlockException.INCORRECT_EXCESS_BLOB_GAS
    blockchain_test(
        pre=pre,
        post={},
        blocks=blocks,
        genesis_environment=genesis_environment,
        tag="-".join(
            [
                f"correct:{hex(correct_excess_blob_gas)}",
                f"header:{hex(parent_excess_blob_gas)}",
            ]
        ),
    )


@pytest.mark.parametrize(
    "parent_excess_blobs,parent_blobs,parent_target_blobs",
    generate_excess_blobs_combinations(
        # Test all combinations where the calculated excess blobs for the block should be zero
        expected_excess_blobs=0,
        parent_excess_blobs_values=[0],
        parent_blobs_values=BLOB_COMBINATIONS_PRAGUE,
        target_blobs_values=BLOB_COMBINATIONS_PRAGUE,
    ),
)
@pytest.mark.parametrize("header_excess_blobs_delta", [1])
@pytest.mark.parametrize("new_blobs", [1])
def test_invalid_excess_blob_gas_target_blobs_increase_from_zero(
    blockchain_test: BlockchainTestFiller,
    genesis_environment: Environment,
    pre: Mapping[Address, Account],
    blocks: List[Block],
    correct_excess_blob_gas: int,
    header_excess_blob_gas: Optional[int],
):
    """
    Test rejection of blocks where the `excessBlobGas` increases from zero,
    even when the included blobs are on or below target.

    Test is parametrized as follows:
    - parent excess blobs is always zero
    - parent blobs is always below current block target
    - current block target blobs is 0, 1, Prague's target or max blobs
    """
    if header_excess_blob_gas is None:
        raise Exception("test case is badly formatted")

    if header_excess_blob_gas == correct_excess_blob_gas:
        raise Exception("invalid test case")

    blockchain_test(
        pre=pre,
        post={},
        blocks=blocks,
        genesis_environment=genesis_environment,
        tag="-".join(
            [
                f"correct:{hex(correct_excess_blob_gas)}",
                f"header:{hex(header_excess_blob_gas)}",
            ]
        ),
    )


@pytest.mark.parametrize(
    "parent_excess_blobs,parent_blobs,parent_target_blobs",
    generate_excess_blobs_combinations(
        # Test all combinations where the calculated excess blobs for the block should be
        # greater than zero
        expected_excess_blobs=[1],
        parent_excess_blobs_values=[0],
        parent_blobs_values=BLOB_COMBINATIONS_PRAGUE,
        target_blobs_values=BLOB_COMBINATIONS_PRAGUE,
    ),
)
@pytest.mark.parametrize("header_excess_blob_gas", [0])
@pytest.mark.parametrize("new_blobs", [1])
def test_invalid_static_excess_blob_gas_from_zero_on_blobs_above_target(
    blockchain_test: BlockchainTestFiller,
    genesis_environment: Environment,
    pre: Mapping[Address, Account],
    blocks: List[Block],
    correct_excess_blob_gas: int,
    header_excess_blob_gas: Optional[int],
):
    """
    Test rejection of blocks where the `excessBlobGas` does not increase from
    zero, even when the included blobs is above target.

    Test is parametrized as follows:
    - parent excess blobs is always zero
    - parent blobs is always above current block target
    - current block target blobs is 0, 1, Prague's target or max blobs
    """
    if header_excess_blob_gas is None:
        raise Exception("test case is badly formatted")

    if header_excess_blob_gas == correct_excess_blob_gas:
        raise Exception("invalid test case")

    blockchain_test(
        pre=pre,
        post={},
        blocks=blocks,
        genesis_environment=genesis_environment,
        tag="-".join(
            [
                f"correct:{hex(correct_excess_blob_gas)}",
                f"header:{hex(header_excess_blob_gas)}",
            ]
        ),
    )


# @pytest.mark.parametrize(
#     "parent_blobs,header_excess_blobs_delta",
#     itertools.product(
#         # parent_blobs
#         range(0, SpecHelpers.max_blobs_per_block() + 1),
#         # header_excess_blobs_delta (from correct value)
#         [
#             x
#             for x in range(
#                 -SpecHelpers.target_blobs_per_block(), SpecHelpers.target_blobs_per_block() + 1
#             )
#             if x != 0
#         ],
#     ),
# )
# @pytest.mark.parametrize("new_blobs", [1])
# def test_invalid_excess_blob_gas_change(
#     blockchain_test: BlockchainTestFiller,
#     genesis_environment: Environment,
#     pre: Mapping[Address, Account],
#     blocks: List[Block],
#     correct_excess_blob_gas: int,
#     header_excess_blob_gas: Optional[int],
# ):
#     """
#     Test rejection of blocks where the `excessBlobGas` changes to an invalid
#     value.

#     Given a parent block containing `[0, MAX_BLOBS_PER_BLOCK]` blobs, test an invalid
#     `excessBlobGas` value by changing it by `[-TARGET_BLOBS_PER_BLOCK, TARGET_BLOBS_PER_BLOCK]`
#     from the correct value.
#     """
#     if header_excess_blob_gas is None:
#         raise Exception("test case is badly formatted")

#     if header_excess_blob_gas == correct_excess_blob_gas:
#         raise Exception("invalid test case")

#     blockchain_test(
#         pre=pre,
#         post={},
#         blocks=blocks,
#         genesis_environment=genesis_environment,
#         tag="-".join(
#             [
#                 f"correct:{hex(correct_excess_blob_gas)}",
#                 f"header:{hex(header_excess_blob_gas)}",
#             ]
#         ),
#     )


# @pytest.mark.parametrize(
#     "header_excess_blob_gas",
#     [(2**64 + (x * Spec.GAS_PER_BLOB)) for x in range(-SpecHelpers.target_blobs_per_block(), 0)],
# )
# @pytest.mark.parametrize("parent_blobs", range(SpecHelpers.target_blobs_per_block()))
# @pytest.mark.parametrize("new_blobs", [1])
# @pytest.mark.parametrize("parent_excess_blobs", range(SpecHelpers.target_blobs_per_block()))
# def test_invalid_negative_excess_blob_gas(
#     blockchain_test: BlockchainTestFiller,
#     genesis_environment: Environment,
#     pre: Mapping[Address, Account],
#     blocks: List[Block],
#     correct_excess_blob_gas: int,
#     header_excess_blob_gas: Optional[int],
# ):
#     """
#     Test rejection of blocks where the `excessBlobGas` changes to the two's
#     complement equivalent of the negative value after subtracting target blobs.

#     Reasoning is that the `excessBlobGas` is a `uint64`, so it cannot be negative, and
#     we test for a potential underflow here.
#     """
#     if header_excess_blob_gas is None:
#         raise Exception("test case is badly formatted")

#     if header_excess_blob_gas == correct_excess_blob_gas:
#         raise Exception("invalid test case")

#     blockchain_test(
#         pre=pre,
#         post={},
#         blocks=blocks,
#         genesis_environment=genesis_environment,
#         tag="-".join(
#             [
#                 f"correct:{hex(correct_excess_blob_gas)}",
#                 f"header:{hex(header_excess_blob_gas)}",
#             ]
#         ),
#     )


# @pytest.mark.parametrize(
#     "parent_blobs,header_excess_blob_gas_delta",
#     [
#         (SpecHelpers.target_blobs_per_block() + 1, 1),
#         (SpecHelpers.target_blobs_per_block() + 1, Spec.GAS_PER_BLOB - 1),
#         (SpecHelpers.target_blobs_per_block() - 1, -1),
#         (SpecHelpers.target_blobs_per_block() - 1, -(Spec.GAS_PER_BLOB - 1)),
#     ],
# )
# @pytest.mark.parametrize("new_blobs", [1])
# @pytest.mark.parametrize("parent_excess_blobs", [SpecHelpers.target_blobs_per_block() + 1])
# def test_invalid_non_multiple_excess_blob_gas(
#     blockchain_test: BlockchainTestFiller,
#     genesis_environment: Environment,
#     pre: Mapping[Address, Account],
#     blocks: List[Block],
#     correct_excess_blob_gas: int,
#     header_excess_blob_gas: Optional[int],
# ):
#     """
#     Test rejection of blocks where the `excessBlobGas` changes to a value that
#     is not a multiple of Spec.GAS_PER_BLOB`:

#     - Parent block contains `TARGET_BLOBS_PER_BLOCK + 1` blobs, but `excessBlobGas` is off by +/-1
#     - Parent block contains `TARGET_BLOBS_PER_BLOCK - 1` blobs, but `excessBlobGas` is off by +/-1
#     """
#     if header_excess_blob_gas is None:
#         raise Exception("test case is badly formatted")

#     if header_excess_blob_gas == correct_excess_blob_gas:
#         raise Exception("invalid test case")

#     blockchain_test(
#         pre=pre,
#         post={},
#         blocks=blocks,
#         genesis_environment=genesis_environment,
#         tag="-".join(
#             [
#                 f"correct:{hex(correct_excess_blob_gas)}",
#                 f"header:{hex(header_excess_blob_gas)}",
#             ]
#         ),
#     )
