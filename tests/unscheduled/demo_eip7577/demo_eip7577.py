"""
Dummy test module for eip version check demoing.
"""

import pytest

from ethereum_test_tools import Alloc, StateTestFiller

pytestmark = [pytest.mark.valid_from("CancunEIP7577")]

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7577.md"
REFERENCE_SPEC_VERSION = "1.0.0"


@pytest.mark.eip_version_test("EIP-7577", "1.0.0")
def test_7577_incorrect_major_version_should_pass(state_test: StateTestFiller, pre: Alloc):
    """
    Dummy test for eip version check demoing
    """
    pass


@pytest.mark.eip_version_test("EIP-7577", "1.0.0")
def test_7577_incorrect_major_version_should_fail(state_test: StateTestFiller, pre: Alloc):
    """
    Dummy test for eip version check demoing
    """
    assert False


@pytest.mark.eip_version_test("EIP-7577", "2.0.0")
def test_7577_correct_major_version_should_pass(state_test: StateTestFiller, pre: Alloc):
    """
    Dummy test for eip version check demoing
    """
    pass


@pytest.mark.eip_version_test("EIP-7577", "2.0.0")
def test_7577_correct_major_version_should_fail(state_test: StateTestFiller, pre: Alloc):
    """
    Dummy test for eip version check demoing
    """
    assert False
