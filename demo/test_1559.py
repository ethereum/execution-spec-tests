"""
Dummy test module for eip version check demoing.
"""

import pytest

from ethereum_test_tools import Alloc, StateTestFiller

pytestmark = [pytest.mark.valid_from("Cancun")]


@pytest.mark.requires("EIP-1559", "1.0.0")
def test_1559_incorrect_major_version_should_pass(state_test: StateTestFiller, pre: Alloc):
    """
    Dummy test for eip version check demoing
    """
    pass


@pytest.mark.requires("EIP-1559", "1.0.0")
def test_1559_incorrect_major_version_should_fail(state_test: StateTestFiller, pre: Alloc):
    """
    Dummy test for eip version check demoing
    """
    assert False


@pytest.mark.requires("EIP-1559", "2.0.0")
def test_1559_correct_major_version_should_pass(state_test: StateTestFiller, pre: Alloc):
    """
    Dummy test for eip version check demoing
    """
    pass


@pytest.mark.requires("EIP-1559", "2.0.0")
def test_1559_correct_major_version_should_fail(state_test: StateTestFiller, pre: Alloc):
    """
    Dummy test for eip version check demoing
    """
    assert False
