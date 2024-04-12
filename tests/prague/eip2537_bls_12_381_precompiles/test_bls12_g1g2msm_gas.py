"""
abstract: Tests gas discount table for BLS12_G1MSM, BLS12_G2MSM precompiles of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Tests gas discount table for BLS12_G1MSM, BLS12_G2MSM precompiles of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501

from typing import List

import pytest

from ethereum_test_tools import Conditional, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import StateTestFiller, Storage, Transaction

from .spec import FORK, GAS_CALCULATION_FUNCTION_MAP, Spec, ref_spec_2537

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = pytest.mark.valid_from(str(FORK))


@pytest.fixture
def input() -> bytes:
    """Input data for the contract."""
    return b""


@pytest.fixture
def call_contract_code(
    precompile_address: int,
    precompile_gas_list: List[int],
    precompile_args_length_list: List[int],
    call_succeeds: bool,
    call_contract_post_storage: Storage,
) -> bytes:
    """Code of the test contract to measure gas in the MSM pre-compiles."""
    assert len(precompile_gas_list) == len(precompile_args_length_list)
    code = b""
    for precompile_gas, precompile_args_length in zip(
        precompile_gas_list, precompile_args_length_list
    ):
        # For each given precompile gas value, and given arguments length (all zeros), call the
        # precompile and compare the result.
        code += bytes(
            Conditional(
                condition=Op.EQ(
                    1 if call_succeeds else 0,
                    Op.CALL(
                        precompile_gas,
                        precompile_address,
                        0,
                        0,
                        precompile_args_length,
                        0,
                        0,
                    ),
                ),
                if_true=b"",
                if_false=Op.REVERT(0, 0),
            )
        )
    code += Op.SSTORE(call_contract_post_storage.store_next(1), 1)
    return code


@pytest.mark.parametrize(
    "precompile_gas_list,precompile_args_length_list,call_succeeds",
    [
        pytest.param(
            [GAS_CALCULATION_FUNCTION_MAP[Spec.G1MSM](i * 160) for i in range(1, 129)],
            [i * 160 for i in range(1, 129)],
            True,
            id="exact_gas_full_discount_table",
        ),
        pytest.param(
            [GAS_CALCULATION_FUNCTION_MAP[Spec.G1MSM](i * 160) + 1 for i in range(1, 129)],
            [i * 160 for i in range(1, 129)],
            True,
            id="one_extra_gas_full_discount_table",
        ),
        pytest.param(
            [GAS_CALCULATION_FUNCTION_MAP[Spec.G1MSM](i * 160) - 1 for i in range(1, 129)],
            [i * 160 for i in range(1, 129)],
            False,
            id="insufficient_gas_full_discount_table",
        ),
    ],
)
@pytest.mark.parametrize("tx_gas_limit", [100_000_000], ids=[""])
@pytest.mark.parametrize("precompile_address", [Spec.G1MSM])
def test_gas_g1msm(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G1MSM discount gas table in full, by expecting the call to succeed or fail for
    all possible input lengths.

    If any of the calls succeeds or fails when it should not, the test will fail.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "precompile_gas_list,precompile_args_length_list,call_succeeds",
    [
        pytest.param(
            [GAS_CALCULATION_FUNCTION_MAP[Spec.G2MSM](i * 288) for i in range(1, 129)],
            [i * 288 for i in range(1, 129)],
            True,
            id="exact_gas_full_discount_table",
        ),
        pytest.param(
            [GAS_CALCULATION_FUNCTION_MAP[Spec.G2MSM](i * 288) + 1 for i in range(1, 129)],
            [i * 288 for i in range(1, 129)],
            True,
            id="one_extra_gas_full_discount_table",
        ),
        pytest.param(
            [GAS_CALCULATION_FUNCTION_MAP[Spec.G2MSM](i * 288) - 1 for i in range(1, 129)],
            [i * 288 for i in range(1, 129)],
            False,
            id="insufficient_gas_full_discount_table",
        ),
    ],
)
@pytest.mark.parametrize("tx_gas_limit", [100_000_000], ids=[""])
@pytest.mark.parametrize("precompile_address", [Spec.G2MSM])
def test_gas_g2msm(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G1MSM discount gas table in full, by expecting the call to succeed or fail for
    all possible input lengths.

    If any of the calls succeeds or fails when it should not, the test will fail.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
