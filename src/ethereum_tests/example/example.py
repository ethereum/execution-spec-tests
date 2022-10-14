"""
Test Yul Source Code Examples
"""

from ethereum_test import (
    Account,
    Environment,
    StateTest,
    Transaction,
    Yul,
    TestAddress,
    test_from,
)


@test_from("berlin")
def test_yul():
    """
    Test CHAINID opcode.
    """
    env = Environment()

    pre = {
        "0x095e7baea6a6c7c4c2dfeb977efac326af552d87": Account(
            balance=0x0ba1a9ce0ba1a9ce,
            code=Yul("""
            {
                function f(a, b) -> c {
                    c := add(a, b)
                }

                sstore(0, f(1, 2))
                return(0, 32)
            }
            """)
        ),
        TestAddress: Account(
            balance=0x0ba1a9ce0ba1a9ce
        ),
    }

    tx = Transaction(
        ty=0x0,
        chain_id=0x0,
        nonce=0,
        to="0x095e7baea6a6c7c4c2dfeb977efac326af552d87",
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )

    post = {
        "0x095e7baea6a6c7c4c2dfeb977efac326af552d87": Account(
            code="0x6011565b600082820190505b92915050565b601b600260016003565b60005560206000f3", storage={"0x00": "0x03"}
        ),
    }

    return StateTest(env, pre, post, [tx])
