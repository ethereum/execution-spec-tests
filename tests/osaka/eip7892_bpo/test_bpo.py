"""abstract: Test [EIP-7892: Blob Parameter Only Hardforks](https://eips.ethereum.org/EIPS/eip-7892)."""

import pytest

from ethereum_test_base_types.composite_types import ForkBlobSchedule, TimestampBlobSchedule
from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Alloc,
    Block,
    BlockchainTestFiller,
)
from ethereum_test_types import Environment

from .spec import ref_spec_7892  # type: ignore

REFERENCE_SPEC_GIT_PATH = ref_spec_7892.git_path
REFERENCE_SPEC_VERSION = ref_spec_7892.version


@pytest.mark.valid_from("Osaka")
def test_bpo_schedule(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    post: Alloc,
    env: Environment,
    fork: Fork,
):
    """Test whether clients correctly set provided BPO schedules."""
    bpo_schedule = TimestampBlobSchedule()
    # below ensure that there is a timestamp difference of at least 3 between each scheduled fork
    bpo_schedule.add_schedule(
        1234, ForkBlobSchedule(max=6, target=5, base_fee_update_fraction=5007716)
    )
    bpo_schedule.add_schedule(
        2345, ForkBlobSchedule(max=4, target=3, base_fee_update_fraction=5007716)
    )

    blocks = []
    for schedule_dict in bpo_schedule.root:
        for t in schedule_dict:
            # add block before bpo
            blocks.append(Block(timestamp=t - 1))
            # add block at bpo
            blocks.append(Block(timestamp=t))
            # add block after bpo
            blocks.append(Block(timestamp=t + 1))

    # amount of created blocks = 3 * len(bpo_schedule.root)
    assert len(blocks) == 3 * len(bpo_schedule.root)

    # TODO:
    # for each block the client should report the current values of: max, target and base_fee_update_fraction  # noqa: E501
    # we need to signal to the client that the expected response is according to the bpo_schedule defined above  # noqa: E501

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
        bpo_schedule=bpo_schedule,
    )
