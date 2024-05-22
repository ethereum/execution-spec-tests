"""
EOF V1 Code Validation tests
"""

from ethereum_test_tools import (
    Account,
    Address,
    Environment,
    EOFTestFiller,
    StateTestFiller,
    TestAddress,
    Transaction,
)
from ethereum_test_tools.eof.v1 import Container


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
            Address(0x100): Account(
                code=container,
                nonce=1,
            ),
        }

        tx = Transaction(
            nonce=1,
            to=Address(0x100),
            gas_limit=44_000,
            gas_price=10,
            protected=False,
            data="1",
        )

        post = {Address(0x100): Account(storage={0: 1})}

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
