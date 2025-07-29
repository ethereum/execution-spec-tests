"""abstract: Test [EIP-7892: Blob Parameter Only Hardforks](https://eips.ethereum.org/EIPS/eip-7892)."""

import pytest

from ethereum_test_base_types.base_types import Address, Hash
from ethereum_test_base_types.composite_types import ForkBlobSchedule, TimestampBlobSchedule
from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Alloc,
    Block,
    BlockchainTestFiller,
)
from ethereum_test_types import Environment
from ethereum_test_types.helpers import add_kzg_version
from ethereum_test_types.transaction_types import Transaction
from tests.osaka.eip7594_peerdas.spec import Spec

from .spec import ref_spec_7892  # type: ignore

REFERENCE_SPEC_GIT_PATH = ref_spec_7892.git_path
REFERENCE_SPEC_VERSION = ref_spec_7892.version


# def min_base_fee_per_blob_gas_bpo(block_number: int = 0, timestamp: int = 0) -> int:
#     """Return the minimum base fee per blob gas for BPO fork."""
#     return 1


# def blob_gas_price_calculator_bpo(
#     fork_blob_schedule: ForkBlobSchedule,
#     block_number: int = 0,
#     timestamp: int = 0,
# ) -> BlobGasPriceCalculator:
#     """Return a callable that calculates the blob gas price at Cancun."""
#     fake_exponential(
#         factor=min_base_fee_per_blob_gas_bpo(block_number=block_number, timestamp=timestamp),
#         numerator=excess_blob_gas,
#         denominator=fork_blob_schedule.base_fee_update_fraction,
#     )


@pytest.fixture
def bpo_schedule() -> TimestampBlobSchedule:
    """Create and return the BPO pseudo schedule used for the tests in this file."""
    bpo_schedule = TimestampBlobSchedule()
    # below ensure that there is a timestamp difference of at least 3 between each scheduled fork
    bpo_schedule.add_schedule(
        20000, ForkBlobSchedule(max=6, target_blobs_per_block=5, base_fee_update_fraction=5007716)
    )
    bpo_schedule.add_schedule(
        21000, ForkBlobSchedule(max=8, target_blobs_per_block=7, base_fee_update_fraction=5555555)
    )
    bpo_schedule.add_schedule(
        22000, ForkBlobSchedule(max=4, target_blobs_per_block=3, base_fee_update_fraction=4444444)
    )
    return bpo_schedule


def tx(
    sender: Address,
    fork_blob_schedule: ForkBlobSchedule,
) -> Transaction:
    """Blob transaction fixture."""
    # calculator = blob_gas_price_calculator_bpo(fork_blob_schedule=fork_blob_schedule)
    # max_fee_per_blob_gas = calculator()

    return Transaction(
        ty=3,
        sender=sender,
        value=1,
        gas_limit=21_000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=1,
        max_fee_per_blob_gas=999_999_999_999,  # idk how to use the excess_blob_gas fixtures with bpo which is not a fork in our modelling  # noqa: E501
        access_list=[],
        blob_versioned_hashes=add_kzg_version(
            [Hash(i) for i in range(0, fork_blob_schedule.max_blobs_per_block)],
            Spec.BLOB_COMMITMENT_VERSION_KZG,
        ),
    )


@pytest.mark.valid_from("Osaka")
def test_bpo_schedule(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    env: Environment,
    fork: Fork,
    sender: Address,
    bpo_schedule: TimestampBlobSchedule,
):
    """Test whether clients correctly set provided BPO schedules."""
    blocks = []
    for schedule_dict in bpo_schedule.root:  # each schedule_dict is Dict[int, ForkBlobSchedule] where int is the timestamp  # noqa: E501
        timestamp = next(iter(schedule_dict))  # first key is timestamp
        fork_blob_schedule: ForkBlobSchedule | None = schedule_dict.get(timestamp)
        assert fork_blob_schedule is not None

        # add block before bpo
        blocks.append(
            Block(
                txs=[
                    tx(sender=sender, fork_blob_schedule=fork_blob_schedule)
                ],  # tx should pick up fork_blob_schedule as input parameter
                timestamp=timestamp - 1,
            )
        )
        # add block at bpo
        blocks.append(
            Block(
                txs=[tx(sender=sender, fork_blob_schedule=fork_blob_schedule)],
                timestamp=timestamp,
            )
        )
        # add block after bpo
        blocks.append(
            Block(
                txs=[tx(sender=sender, fork_blob_schedule=fork_blob_schedule)],
                timestamp=timestamp + 1,
            )
        )

    # amount of created blocks = 3 * len(bpo_schedule.root)
    assert len(blocks) == 3 * len(bpo_schedule.root)

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
        bpo_schedule=bpo_schedule,
    )
