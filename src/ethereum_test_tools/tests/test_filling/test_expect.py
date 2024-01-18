"""
Test suite for `ethereum_test_tools.filling` fixture post (expect) section.
"""
from typing import Any, Mapping, Optional

import pytest

from ethereum_test_forks import Shanghai
from evm_transition_tool import FixtureFormats, GethTransitionTool

from ...common import Account, Environment, TestAddress, Transaction, to_address
from ...common.types import Storage
from ...spec import StateTest

# from ...spec.blockchain.types import FixtureCommon as BlockchainFixtureCommon

ADDRESS_UNDER_TEST = to_address(0x01)
pre = {
    TestAddress: Account(balance=1000000000000000000000),
}
post = {}


def run_post_state_mismatch_test(
    pre: Mapping[Any, Any], post: Mapping[Any, Any], exception: Any
) -> Optional[pytest.ExceptionInfo]:
    """
    Performs test filling and post state verification.
    """
    fork = Shanghai
    t8n = GethTransitionTool()
    fixture_format = FixtureFormats.BLOCKCHAIN_TEST
    state_test = StateTest(
        env=Environment(),
        pre=pre,
        post=post,
        tx=Transaction(),
        tag="post_value_mismatch",
        fixture_format=fixture_format,
    )

    if exception:
        e_info: pytest.ExceptionInfo
        with pytest.raises(exception) as e_info:
            state_test.generate(t8n=t8n, fork=fork)
        return e_info
    else:
        return None


# Storage value mismatch tests
@pytest.mark.parametrize(
    "pre_storage,post_storage,expected_exception",
    [
        (  # mismatch_1: 1:1 vs 1:2
            {"0x01": "0x01"},
            {"0x01": "0x02"},
            Storage.KeyValueMismatch(address=ADDRESS_UNDER_TEST, key=1, want=2, got=1),
        ),
        (  # mismatch_2: 1:1 vs 2:1
            {"0x01": "0x01"},
            {"0x02": "0x01"},
            Storage.KeyValueMismatch(address=ADDRESS_UNDER_TEST, key=1, want=0, got=1),
        ),
        (  # mismatch_2_a: 1:1 vs 0:0
            {"0x01": "0x01"},
            {"0x00": "0x00"},
            Storage.KeyValueMismatch(address=ADDRESS_UNDER_TEST, key=1, want=0, got=1),
        ),
        (  # mismatch_2_b: 1:1 vs empty
            {"0x01": "0x01"},
            {},
            Storage.KeyValueMismatch(address=ADDRESS_UNDER_TEST, key=1, want=0, got=1),
        ),
        (  # mismatch_3: 0:0 vs 1:2
            {"0x00": "0x00"},
            {"0x01": "0x02"},
            Storage.KeyValueMismatch(address=ADDRESS_UNDER_TEST, key=1, want=2, got=0),
        ),
        (  # mismatch_3_a: empty vs 1:2
            {},
            {"0x01": "0x02"},
            Storage.KeyValueMismatch(address=ADDRESS_UNDER_TEST, key=1, want=2, got=0),
        ),
        (  # mismatch_4: 0:3, 1:2 vs 1:2
            {"0x00": "0x03", "0x01": "0x02"},
            {"0x01": "0x02"},
            Storage.KeyValueMismatch(address=ADDRESS_UNDER_TEST, key=0, want=0, got=3),
        ),
        (  # mismatch_5: 1:2, 2:3 vs 1:2
            {"0x01": "0x02", "0x02": "0x03"},
            {"0x01": "0x02"},
            Storage.KeyValueMismatch(address=ADDRESS_UNDER_TEST, key=2, want=0, got=3),
        ),
        (  # mismatch_6: 1:2 vs 1:2, 2:3
            {"0x01": "0x02"},
            {"0x01": "0x02", "0x02": "0x03"},
            Storage.KeyValueMismatch(address=ADDRESS_UNDER_TEST, key=2, want=3, got=0),
        ),
    ],
)
def test_post_storage_value_mismatch(pre_storage, post_storage, expected_exception):
    """
    Test `ethereum_test.filler.fill_test` post state storage verification.
    """
    pre[ADDRESS_UNDER_TEST] = Account(nonce=1, storage=pre_storage)
    post[ADDRESS_UNDER_TEST] = Account(storage=post_storage)
    e_info = run_post_state_mismatch_test(pre, post, Storage.KeyValueMismatch)
    assert e_info.value == expected_exception


# Nonce value mismatch tests
@pytest.mark.parametrize(
    "pre_nonce,post_nonce",
    [(1, 2), (1, 0), (1, None)],
)
def test_post_nonce_value_mismatch(pre_nonce, post_nonce):
    """
    Test `ethereum_test.filler.fill_test` post state nonce verification.
    """
    pre[ADDRESS_UNDER_TEST] = Account(nonce=pre_nonce)
    post[ADDRESS_UNDER_TEST] = Account(nonce=post_nonce)
    if post_nonce is None:
        run_post_state_mismatch_test(pre, post, None)
    else:
        e_info = run_post_state_mismatch_test(pre, post, Account.NonceMismatch)
        assert e_info.value == Account.NonceMismatch(
            address=ADDRESS_UNDER_TEST, want=post_nonce, got=pre_nonce
        )


# Code value mismatch tests
@pytest.mark.parametrize(
    "pre_code,post_code",
    [
        (
            "0x02",
            "0x01",
        ),
        (
            "0x02",
            "0x",
        ),
        (
            "0x02",
            None,
        ),
    ],
)
def test_post_code_value_mismatch(pre_code, post_code):
    """
    Test `ethereum_test.filler.fill_test` post state code verification.
    """
    pre[ADDRESS_UNDER_TEST] = Account(code=pre_code)
    post[ADDRESS_UNDER_TEST] = Account(code=post_code)
    if post_code is None:
        run_post_state_mismatch_test(pre, post, None)
    else:
        e_info = run_post_state_mismatch_test(pre, post, Account.CodeMismatch)
        assert e_info.value == Account.CodeMismatch(
            address=ADDRESS_UNDER_TEST, want=post_code, got=pre_code
        )


# Balance value mismatch tests
@pytest.mark.parametrize(
    "pre_balance,post_balance",
    [
        (
            1,
            2,
        ),
        (
            1,
            0,
        ),
        (
            1,
            None,
        ),
    ],
)
def test_post_balance_value_mismatch(pre_balance, post_balance):
    """
    Test `ethereum_test.filler.fill_test` post state balance verification.
    """
    pre[ADDRESS_UNDER_TEST] = Account(balance=pre_balance)
    post[ADDRESS_UNDER_TEST] = Account(balance=post_balance)
    if post_balance is None:
        run_post_state_mismatch_test(pre, post, None)
    else:
        e_info = run_post_state_mismatch_test(pre, post, Account.BalanceMismatch)
        assert e_info.value == Account.BalanceMismatch(
            address=ADDRESS_UNDER_TEST, want=post_balance, got=pre_balance
        )


# Account mismatch tests
@pytest.mark.parametrize(
    "pre_accounts,post_accounts,error_str",
    [
        (
            {ADDRESS_UNDER_TEST: Account(balance=1)},
            {ADDRESS_UNDER_TEST: Account()},
            None,
        ),
        (
            {ADDRESS_UNDER_TEST: Account(balance=1)},
            {ADDRESS_UNDER_TEST: Account(balance=1), to_address(0x02): Account(balance=1)},
            "expected account not found",
        ),
        (
            {ADDRESS_UNDER_TEST: Account(balance=1)},
            {},
            None,
        ),
        (
            {ADDRESS_UNDER_TEST: Account(balance=1)},
            {ADDRESS_UNDER_TEST: Account.NONEXISTENT},
            "found unexpected account",
        ),
    ],
)
def test_post_account_mismatch(pre_accounts, post_accounts, error_str):
    """
    Test `ethereum_test.filler.fill_test` post state account verification.
    """
    pre.update(pre_accounts)
    post.update(post_accounts)
    if error_str is None:
        run_post_state_mismatch_test(pre, post, None)
    else:
        e_info = run_post_state_mismatch_test(pre, post, Exception)
        assert error_str in str(e_info.value)
