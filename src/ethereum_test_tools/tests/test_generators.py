"""
Test suite for model generators (Transactions, Withdrawals, Blocks).
"""

from itertools import count
from typing import List

import pytest

from ..common import Address, Transaction, Transactions, Withdrawal, Withdrawals
from ..common.base_types import ModelGenerator
from ..spec.blockchain.types import Block


# Blocks is currently broken, single test involving Blocks is expected to fail
class Blocks(ModelGenerator, model=Block):
    """
    Block generator.

    This class is used to generate blocks for a blockchain test case.

    Takes the same arguments as `Block`, but if an iterable is provided for a
    field, it will generate a block for each element in the iterable.

    If none of the values are iterables, an exception will be raised because none of the provided
    values will be bounded, unless the `limit` argument is provided, which will limit the number
    of blocks generated.

    Fields that are already supposed to be iterables, such as `txs` and
    `withdrawals`, can be parametrized as `txs_iter` and
    `withdrawals_iter` respectively and an iterable of iterables can be provided to be
    used in each generated block.
    """

    pass


@pytest.mark.parametrize(
    [
        "generator",
        "chunks",
        "expected_lists",
    ],
    [
        pytest.param(
            Transactions(
                gas_price=range(1000000000, 2000000001, 1000000000),
            ),
            1,
            [
                [
                    Transaction(
                        gas_price=1000000000,
                    ),
                    Transaction(
                        nonce=1,
                        gas_price=2000000000,
                    ),
                ]
            ],
            id="type-0-gas-price-range",
        ),
        pytest.param(
            Transactions(
                gas_price=[1000000000, 2000000000],
            ),
            1,
            [
                [
                    Transaction(
                        gas_price=1000000000,
                    ),
                    Transaction(
                        nonce=1,
                        gas_price=2000000000,
                    ),
                ]
            ],
            id="type-0-gas-price-list",
        ),
        pytest.param(
            Transactions(
                gas_price=[1000000000, 2000000000],
                data=b"\x00\x01",
            ),
            1,
            [
                [
                    Transaction(
                        gas_price=1000000000,
                        data=b"\x00\x01",
                    ),
                    Transaction(
                        nonce=1,
                        gas_price=2000000000,
                        data=b"\x00\x01",
                    ),
                ]
            ],
            id="type-0-gas-price-list-with-data",
        ),
        pytest.param(
            Transactions(
                data=[b"\x00\x01", b"\x00\x02"],
            ),
            1,
            [
                [
                    Transaction(
                        data=b"\x00\x01",
                    ),
                    Transaction(
                        nonce=1,
                        data=b"\x00\x02",
                    ),
                ]
            ],
            id="type-0-data-list",
        ),
        pytest.param(
            Transactions(
                nonce=1,
                data=[b"\x00\x01", b"\x00\x02"],
            ),
            1,
            [
                [
                    Transaction(
                        nonce=1,
                        data=b"\x00\x01",
                    ),
                    Transaction(
                        nonce=2,
                        data=b"\x00\x02",
                    ),
                ]
            ],
            id="type-0-data-list-non-zero-nonce",
        ),
        pytest.param(
            Transactions(
                nonce=range(2),
                data=[b"\x00\x01", b"\x00\x02"],
            ),
            1,
            [
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                    ),
                    Transaction(
                        nonce=1,
                        data=b"\x00\x02",
                    ),
                ]
            ],
            id="type-0-data-list-iterator-nonce",
        ),
        pytest.param(
            Transactions(
                nonce=range(2),
                data=[b"\x00\x01", b"\x00\x02", b"\x00\x03"],
            ),
            1,
            [
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                    ),
                    Transaction(
                        nonce=1,
                        data=b"\x00\x02",
                    ),
                ]
            ],
            id="type-0-data-list-shorter-iterator-nonce",
        ),
        pytest.param(
            Transactions(
                data=b"\x00\x01",
                gas_limit=1000000,
                gas_price=1000000000,
                limit=2,
            ),
            1,
            [
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                    ),
                    Transaction(
                        nonce=1,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                    ),
                ]
            ],
            id="type-0-limit",
        ),
        pytest.param(
            Transactions(
                nonce=range(1000),
                data=b"\x00\x01",
                gas_limit=1000000,
                gas_price=1000000000,
                limit=2,
            ),
            1,
            [
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                    ),
                    Transaction(
                        nonce=1,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                    ),
                ]
            ],
            id="type-0-limit-longer-iterator",
        ),
        pytest.param(
            Transactions(
                nonce=range(1000),
                data=b"\x00\x01",
                gas_limit=1000000,
                gas_price=1000000000,
                blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                limit=2,
            ),
            1,
            [
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=1,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ]
            ],
            id="type-3-list-type",
        ),
        pytest.param(
            Transactions(
                nonce=range(1000),
                data=b"\x00\x01",
                gas_limit=1000000,
                gas_price=1000000000,
                blob_versioned_hashes_iter=[
                    [b"\x00\x01", b"\x00\x02"],
                    [b"\x00\x01", b"\x00\x03"],
                ],
            ),
            1,
            [
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=1,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x03"],
                    ),
                ]
            ],
            id="type-3-list-list-type",
        ),
        pytest.param(
            Transactions(
                nonce=range(1000),
                data=b"\x00\x01",
                gas_limit=1000000,
                gas_price=1000000000,
                blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                limit=2,
            ),
            1,
            [
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=1,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ]
            ],
            id="type-3-list-type",
        ),
        pytest.param(
            Transactions(
                nonce=range(1000),
                data=b"\x00\x01",
                gas_limit=1000000,
                gas_price=1000000000,
                blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                limit=2,
            ),
            2,
            [
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=1,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ],
                [
                    Transaction(
                        nonce=2,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=3,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ],
            ],
            id="type-3-list-type-limit-int",
        ),
        pytest.param(
            Transactions(
                nonce=range(1000),
                data=b"\x00\x01",
                gas_limit=1000000,
                gas_price=1000000000,
                blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                limit=[1, 2],
            ),
            2,
            [
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ],
                [
                    Transaction(
                        nonce=1,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=2,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ],
            ],
            id="type-3-list-type-limit-list",
        ),
        pytest.param(
            Transactions(
                nonce=range(1000),
                data=b"\x00\x01",
                gas_limit=1000000,
                gas_price=1000000000,
                blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                limit=count(1),  # Increasing number of transactions each block
            ),
            3,
            [
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ],
                [
                    Transaction(
                        nonce=1,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=2,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ],
                [
                    Transaction(
                        nonce=3,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=4,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=5,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ],
            ],
            id="type-3-list-type-limit-count",
        ),
        pytest.param(
            Transactions(
                nonce=range(1000),
                data=b"\x00\x01",
                gas_limit=1000000,
                gas_price=1000000000,
                blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                limit=count(),  # Increasing number of transactions each block
            ),
            4,
            [
                [],
                [
                    Transaction(
                        nonce=0,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ],
                [
                    Transaction(
                        nonce=1,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=2,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ],
                [
                    Transaction(
                        nonce=3,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=4,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                    Transaction(
                        nonce=5,
                        data=b"\x00\x01",
                        gas_limit=1000000,
                        gas_price=1000000000,
                        blob_versioned_hashes=[b"\x00\x01", b"\x00\x02"],
                    ),
                ],
            ],
            id="type-3-list-type-limit-count-from-zero",
        ),
        pytest.param(
            Withdrawals(
                validator_index=count(1),
                address=b"\x00" * 20,
                amount=1,
                limit=2,
            ),
            1,
            [
                [
                    Withdrawal(
                        index=0,
                        validator_index=1,
                        address=b"\x00" * 20,
                        amount=1,
                    ),
                    Withdrawal(
                        index=1,
                        validator_index=2,
                        address=b"\x00" * 20,
                        amount=1,
                    ),
                ]
            ],
            id="withdrawals-1",
        ),
        pytest.param(
            Blocks(
                txs_iter=Transactions(
                    to=(Address(i * 0x100) for i in count(1)),
                    limit=[3, 2],
                ),
                limit=2,
            ),
            1,
            [
                [
                    Block(
                        txs=[
                            Transaction(
                                to=Address(0x100),
                            ),
                            Transaction(
                                to=Address(0x200),
                            ),
                            Transaction(
                                to=Address(0x300),
                            ),
                        ],
                    ),
                    Block(
                        txs=[
                            Transaction(
                                to=Address(0x400),
                            ),
                            Transaction(
                                to=Address(0x500),
                            ),
                        ],
                    ),
                ]
            ],
            marks=pytest.mark.xfail(reason="Blocks generator is broken"),
            id="blocks-1",
        ),
    ],
)
def test_generators(
    generator: Transactions | Withdrawals | Blocks,
    chunks: int,
    expected_lists: List[List[Transaction | Withdrawal | Block]],
):
    chunked_elements: List[List[Transaction | Withdrawal | Block]] = []
    for _ in range(chunks):
        chunked_elements.append(list(generator))
    for chunk_1, chunk_2 in zip(chunked_elements, expected_lists):
        assert len(chunk_1) == len(chunk_2)
        for element_1, element_2 in zip(chunk_1, chunk_2):
            assert element_1 == element_2
