"""Test address field in transaction rlp."""

from typing import Optional, Union

import pytest
from pydantic import Field

from ethereum_test_base_types import Bytes
from ethereum_test_tools import (
    Address,
    Alloc,
    Transaction,
    TransactionException,
    TransactionTestFiller,
)

REFERENCE_SPEC_GIT_PATH = None
REFERENCE_SPEC_VERSION = None

pytestmark = pytest.mark.valid_from("Frontier")


class TestTransaction(Transaction):
    """Test version of the Transaction class where 'to' accepts Bytes."""

    to: Optional[Union[Bytes, Address, None]] = Field(Bytes(bytes.fromhex("00")))


def test_tx_address_less_than_20(
    transaction_test: TransactionTestFiller,
    pre: Alloc,
):
    """Test sending a transaction with an empty authorization list."""
    tx = TestTransaction(
        gas_limit=100_000,
        to=bytes.fromhex("0011"),
        value=0,
        error=TransactionException.TYPE_3_TX_MAX_BLOB_GAS_ALLOWANCE_EXCEEDED,
        sender=pre.fund_eoa(),
    )
    tx = tx.with_signature_and_sender()
    hash = tx.hash

    transaction_test(
        pre=pre,
        tx=tx,
    )
