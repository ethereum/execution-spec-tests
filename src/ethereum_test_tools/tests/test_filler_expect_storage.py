"""
Tests for the fixture `post` (expect) section.
"""

from typing import Any, Mapping

import pytest

from ethereum_test_forks import Fork, Shanghai
from evm_transition_tool import GethTransitionTool

from ..common import Account, Environment, Transaction
from ..common.types import Storage
from ..filling import fill_test
from ..spec import BaseTestConfig, StateTest

# Test vectors:
# mismatch_1:    1:1 vs 1:2
# mismatch_2:    1:1 vs 2:1
# mismatch_2_a:  1:1 vs 0:0
# mismatch_2_b:  1:1 vs []
# mismatch_3:    0:0 vs 1:2
# mismatch_3_a:   [] vs 1:2
# mismatch_4:    0:3, 1:2 vs 1:2
# mismatch_5:    1:2, 2:3 vs 1:2
# mismatch_6:    1:2 vs 1:2, 2:3
# mismatch_7:    1:2 vs 1:2, 2:0

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


def run_test(pre: Mapping[Any, Any], post: Mapping[Any, Any], fork: Fork) -> pytest.ExceptionInfo:
    """
    Perform the test execution and post state verification given pre and post
    """
    state_test = StateTest(
        env=Environment(),
        pre=pre,
        post=post,
        txs=[test_transaction],
        tag="post_storage_value_mismatch",
        base_test_config=BaseTestConfig(enable_hive=False),
    )

    t8n = GethTransitionTool()

    e_info: pytest.ExceptionInfo
    with pytest.raises(Storage.KeyValueMismatch) as e_info:
        fixture = {
            f"000/my_chain_id_test/{fork}": fill_test(
                t8n=t8n,
                test_spec=state_test,
                fork=fork,
                spec=None,
            ),
        }
    return e_info


def test_post_storage_value_mismatch_1():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1, storage={"0x01": "0x01"}),
    }

    post = {
        test_address: Account(storage={"0x01": "0x02"}),
    }

    e_info = run_test(pre, post, test_fork)
    assert e_info.value.want == 2
    assert e_info.value.got == 1
    assert e_info.value.key == 1
    assert e_info.value.address == test_address
    assert "incorrect value in address" in str(e_info.value)


def test_post_storage_value_mismatch_2():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1, storage={"0x01": "0x01"}),
    }

    post = {
        test_address: Account(storage={"0x02": "0x01"}),
    }

    e_info = run_test(pre, post, test_fork)
    assert e_info.value.want == 0
    assert e_info.value.got == 1
    assert e_info.value.key == 1
    assert e_info.value.address == test_address
    assert "incorrect value in address" in str(e_info.value)


def test_post_storage_value_mismatch_2_a():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1, storage={"0x01": "0x01"}),
    }

    post = {
        test_address: Account(storage={"0x00": "0x00"}),
    }

    e_info = run_test(pre, post, test_fork)
    assert e_info.value.want == 0
    assert e_info.value.got == 1
    assert e_info.value.key == 1
    assert e_info.value.address == test_address
    assert "incorrect value in address" in str(e_info.value)


def test_post_storage_value_mismatch_2_b():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1, storage={"0x01": "0x01"}),
    }

    post = {
        test_address: Account(storage={}),
    }

    e_info = run_test(pre, post, test_fork)
    assert e_info.value.want == 0
    assert e_info.value.got == 1
    assert e_info.value.key == 1
    assert e_info.value.address == test_address
    assert "incorrect value in address" in str(e_info.value)


def test_post_storage_value_mismatch_3():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1, storage={"0x00": "0x00"}),
    }

    post = {
        test_address: Account(storage={"0x01": "0x02"}),
    }

    e_info = run_test(pre, post, test_fork)
    assert e_info.value.want == 2
    assert e_info.value.got == 0
    assert e_info.value.key == 1
    assert e_info.value.address == test_address
    assert "incorrect value in address" in str(e_info.value)


def test_post_storage_value_mismatch_3_a():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1, storage={}),
    }

    post = {
        test_address: Account(storage={"0x01": "0x02"}),
    }

    e_info = run_test(pre, post, test_fork)
    assert e_info.value.want == 2
    assert e_info.value.got == 0
    assert e_info.value.key == 1
    assert e_info.value.address == test_address
    assert "incorrect value in address" in str(e_info.value)


def test_post_storage_value_mismatch_4():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1, storage={"0x00": "0x03", "0x01": "0x02"}),
    }

    post = {
        test_address: Account(storage={"0x01": "0x02"}),
    }

    e_info = run_test(pre, post, test_fork)
    assert e_info.value.want == 0
    assert e_info.value.got == 3
    assert e_info.value.key == 0
    assert e_info.value.address == test_address
    assert "incorrect value in address" in str(e_info.value)


def test_post_storage_value_mismatch_5():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1, storage={"0x01": "0x02", "0x02": "0x03"}),
    }

    post = {
        test_address: Account(storage={"0x01": "0x02"}),
    }

    e_info = run_test(pre, post, test_fork)
    assert e_info.value.want == 0
    assert e_info.value.got == 3
    assert e_info.value.key == 2
    assert e_info.value.address == test_address
    assert "incorrect value in address" in str(e_info.value)


def test_post_storage_value_mismatch_6():
    """
    Test `ethereum_test.filler.fill_fixtures` with `StateTest` and post state verification.
    """
    pre = {
        sender_address: Account(balance=1000000000000000000000),
        test_address: Account(nonce=1, storage={"0x01": "0x02"}),
    }

    post = {
        test_address: Account(storage={"0x01": "0x02", "0x02": "0x03"}),
    }

    e_info = run_test(pre, post, test_fork)
    assert e_info.value.want == 3
    assert e_info.value.got == 0
    assert e_info.value.key == 2
    assert e_info.value.address == test_address
    assert "incorrect value in address" in str(e_info.value)
