"""
abstract: Test MODEXP (0x0000..0005)

    Tests the MODEXP precompile, located at address 0x0000..0005
    Tests were filled `with evm version 1.13.4-stable-3f907d6a`
"""
from typing import List

import pytest

from ethereum_test_tools import (
    Account,
    Environment,
    StateTestFiller,
    TestAddress,
    Transaction,
    to_address,
)


def create_modexp_tx_data(b: str, e: str, m: str, extra: str):
    """
    Generates input for the MODEXP precompile, with the inputs `b` (base), `e` (exponent),
    `m` (modulus) and optionally extra bytes to append at the end of the call input
    """
    return (
        "0x"
        + f"{int(len(b)/2):x}".zfill(64)
        + f"{int(len(e)/2):x}".zfill(64)
        + f"{int(len(m)/2):x}".zfill(64)
        + b
        + e
        + m
        + extra
    )


@pytest.mark.valid_from("Byzantium")
@pytest.mark.parametrize(
    ["input", "output"],
    [
        # format: ([b, e, m, extraData?], output)
        # Here, `b`, `e` and `m` are the inputs to the ModExp precompile
        # The output is the expected output of the call
        # The optional extraData is extra padded data at the end of the calldata to the precompile
        (["", "", "02"], "0x01"),
        (["", "", "0002"], "0x0001"),
        (["00", "00", "02"], "0x01"),
        (["", "01", "02"], "0x00"),
        (["01", "01", "02"], "0x01"),
        (["02", "01", "03"], "0x02"),
        (["02", "02", "05"], "0x04"),
        (["", "", ""], "0x"),
        (["", "", "00"], "0x00"),
        (["", "", "01"], "0x00"),
        (["", "", "0001"], "0x0000"),
        # Test cases from EIP 198 (Note: the cases where the call goes out-of-gas and the
        # final test case are not yet tested)
        pytest.param(
            [
                "03",
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2e",
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f",
            ],
            "0000000000000000000000000000000000000000000000000000000000000001",
            id="EIP-198-case1",
        ),
        pytest.param(
            [
                "",
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2e",
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f",
            ],
            "0000000000000000000000000000000000000000000000000000000000000000",
            id="EIP-198-case2",
        ),
        pytest.param(
            [
                "03",
                "ffff",
                "8000000000000000000000000000000000000000000000000000000000000000",
                "07",
            ],
            "0x3b01b01ac41f2d6e917c6d6a221ce793802469026d9ab7578fa2e79e4da6aaab",
            id="EIP-198-case3",
        ),
    ],
)
def test_modexp(state_test: StateTestFiller, input: List[str], output: str):
    """
    Test the MODEXP precompile
    """
    env = Environment()
    pre = {TestAddress: Account(balance=1000000000000000000000)}
    post = {}

    account = to_address(0x100)

    pre[account] = Account(
        code=(
            # Store all CALLDATA into memory (offset 0)
            """0x366000600037"""
            +
            # Setup stack to CALL into ModExp with the CALLDATA and CALL into it (+ pop value)
            """60006000366000600060055AF150"""
            +
            # Store contract deployment code to deploy the returned data from ModExp as
            # contract code (16 bytes)
            """7F601038036010600039601038036000F300000000000000000000000000000000600052"""
            +
            # RETURNDATACOPY the returned data from ModExp into memory (offset 16 bytes)
            """3D600060103E"""
            +
            # CREATE contract with the deployment code + the returned data from ModExp
            """3D60100160006000F0"""
            +
            # STOP (handy for tracing)
            "00"
        )
    )

    if len(input) < 4:
        input.append("")

    tx = Transaction(
        ty=0x0,
        nonce=0,
        to=account,
        data=create_modexp_tx_data(*input),
        gas_limit=500000,
        gas_price=10,
        protected=True,
    )
    # Address of the contract which gets generated once the contract is invoked
    post["0xa7f2bd73a7138a2dec709484ad9c3542d7bc7534"] = Account(code=output)

    state_test(env=env, pre=pre, post=post, txs=[tx])
