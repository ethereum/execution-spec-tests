"""
Helpers for EIP-6206 JUMPF containers.
"""
import itertools

from ethereum_test_tools import (
    Account,
    Environment,
    EOFTestFiller,
    StateTestFiller,
    TestAddress,
    TestAddress2,
    Transaction,
)
from ethereum_test_tools.eof.v1 import Container

"""Storage addresses for common testing fields"""
_slot = itertools.count()
next(_slot)  # don't use slot 0
slot_code_worked = next(_slot)
slot_last_slot = next(_slot)

"""Storage values for common testing fields"""
value_code_worked = 0x2015


def execute_tests(state_test: StateTestFiller, eof_test: EOFTestFiller, container: Container):
    """
    Executes EOF validaiton on the container, and if valid executes the container, checking for
    a canary of {0, 1} for successful execution.
    """
    eof_test(
        data=container,
        expect_exception=container.validity_error,
    )

    if container.validity_error is None:
        env = Environment()

        pre = {
            TestAddress: Account(
                balance=1000000000000000000000,
                nonce=1,
            ),
            TestAddress2: Account(
                code=container,
                nonce=1,
            ),
        }

        tx = Transaction(
            nonce=1,
            to=TestAddress2,
            gas_limit=44_000,
            gas_price=10,
            protected=False,
            data="1",
        )

        post = {TestAddress2: Account(storage={slot_code_worked: value_code_worked})}

        state_test(
            env=env,
            pre=pre,
            post=post,
            tx=tx,
        )


def container_name(c: Container):
    """
    Return the name of the container for use in pytest ids.
    """
    if hasattr(c, "name"):
        return c.name
    else:
        return c.__class__.__name__
