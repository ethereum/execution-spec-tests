"""
Tests for the fixture `post` (expect) section.
"""

from collections import namedtuple
from typing import Any, Mapping, Optional

import pytest

from ethereum_test_forks import Fork, Shanghai
from evm_transition_tool import GethTransitionTool

from ..common import Account, Environment, Transaction
from ..common.types import Storage
from ..filling import fill_test
from ..spec import BaseTestConfig, StateTest

test_fork = Shanghai
sender_address = "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b"
test_address = "0x1000000000000000000000000000000000000000"
test_transaction = Transaction(
    ty=0x0,
    chain_id=0x0,
    nonce=0,
    to=test_address,
    gas_limit=100000000,
    gas_price=10,
    protected=False,
)


def run_test(
    pre: Mapping[Any, Any], post: Mapping[Any, Any], tx: Transaction, fork: Fork, exception: Any
) -> Optional[pytest.ExceptionInfo]:
    """
    Perform the test execution and post state verification given pre and post
    """
    state_test = StateTest(
        env=Environment(),
        pre=pre,
        post=post,
        txs=[tx],
        tag="post_storage_value_mismatch",
        base_test_config=BaseTestConfig(enable_hive=False),
    )

    t8n = GethTransitionTool()

    e_info: pytest.ExceptionInfo
    if exception is not None:
        with pytest.raises(exception) as e_info:
            fixture = {
                f"000/my_chain_id_test/{fork}": fill_test(
                    t8n=t8n,
                    test_spec=state_test,
                    fork=fork,
                    spec=None,
                ),
            }
        return e_info
    else:
        fixture = {
            f"000/my_chain_id_test/{fork}": fill_test(
                t8n=t8n,
                test_spec=state_test,
                fork=fork,
                spec=None,
            ),
        }
        return None


def test_post_account_mismatch_nonce():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1),
    }

    post = {
        test_address: Account(nonce=2),
    }

    e_info = run_test(pre, post, test_transaction, test_fork, Account.NonceMismatch)
    assert e_info.value.want == 2
    assert e_info.value.got == 1
    assert e_info.value.address == test_address
    assert "unexpected nonce for account" in str(e_info.value)


def test_post_account_mismatch_nonce_a():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1),
    }

    post = {
        test_address: Account(),
    }

    run_test(pre, post, test_transaction, test_fork, None)


def test_post_account_mismatch_nonce_b():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1),
    }

    post = {
        test_address: Account(nonce=0),
    }

    e_info = run_test(pre, post, test_transaction, test_fork, Account.NonceMismatch)
    assert e_info.value.want == 0
    assert e_info.value.got == 1
    assert e_info.value.address == test_address
    assert "unexpected nonce for account" in str(e_info.value)


def test_post_account_mismatch_code():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(code="0x02"),
    }

    post = {
        test_address: Account(code="0x01"),
    }

    e_info = run_test(pre, post, test_transaction, test_fork, Account.CodeMismatch)
    assert e_info.value.want == "0x01"
    assert e_info.value.got == "0x02"
    assert e_info.value.address == test_address
    assert "unexpected code for account" in str(e_info.value)


def test_post_account_mismatch_code_a():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(code="0x02"),
    }

    post = {
        test_address: Account(),
    }

    run_test(pre, post, test_transaction, test_fork, None)


def test_post_account_mismatch_code_b():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(code="0x02"),
    }

    post = {
        test_address: Account(code=""),
    }

    e_info = run_test(pre, post, test_transaction, test_fork, Account.CodeMismatch)
    assert e_info.value.want == "0x"
    assert e_info.value.got == "0x02"
    assert e_info.value.address == test_address
    assert "unexpected code for account" in str(e_info.value)


def test_post_account_mismatch_balance():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(balance=1),
    }

    post = {
        test_address: Account(balance=2),
    }

    test_transaction.value = 0
    e_info = run_test(pre, post, test_transaction, test_fork, Account.BalanceMismatch)
    assert e_info.value.want == 2
    assert e_info.value.got == 1
    assert e_info.value.address == test_address
    assert "unexpected balance for account" in str(e_info.value)


def test_post_account_mismatch_balance_a():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(balance=1),
    }

    post = {
        test_address: Account(),
    }

    test_transaction.value = 0
    run_test(pre, post, test_transaction, test_fork, None)


def test_post_account_mismatch_balance_b():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(balance=1),
    }

    post = {
        test_address: Account(balance=0),
    }

    e_info = run_test(pre, post, test_transaction, test_fork, Account.BalanceMismatch)
    assert e_info.value.want == 0
    assert e_info.value.got == 1
    assert e_info.value.address == test_address
    assert "unexpected balance for account" in str(e_info.value)


def test_post_account_mismatch_account():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(balance=1),
    }

    post = {
        test_address: Account(),
    }

    run_test(pre, post, test_transaction, test_fork, None)


def test_post_account_mismatch_account_a():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(balance=1),
    }

    post = {
        0x1000000000000000000000000000000000000001: Account(),
    }

    e_info = run_test(pre, post, test_transaction, test_fork, Exception)
    assert "expected account not found" in str(e_info.value)


def test_post_account_mismatch_account_b():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(balance=1),
    }

    post = {}

    run_test(pre, post, test_transaction, test_fork, None)


def test_post_account_mismatch_account_c():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(balance=1),
    }

    post = {test_address: Account.NONEXISTENT}

    e_info = run_test(pre, post, test_transaction, test_fork, Exception)
    assert "found unexpected account" in str(e_info.value)
