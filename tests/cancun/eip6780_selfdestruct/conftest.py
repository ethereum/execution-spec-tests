"""Pytest (plugin) definitions local to EIP-6780 tests."""

import random

import pytest

from ethereum_test_tools import EOA, Address, Alloc, Environment


@pytest.fixture
def sender(pre: Alloc) -> EOA:
    """EOA that will be used to send transactions."""
    return pre.fund_eoa()


@pytest.fixture
def env() -> Environment:
    """Environment for all tests."""
    return Environment()


@pytest.fixture
def selfdestruct_recipient_address() -> Address:
    """Address that can receive a SELFDESTRUCT operation."""
    return Address("0x" + "".join(["{:02x}".format(random.randint(0, 255)) for _ in range(20)]))
