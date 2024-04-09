"""
abstract: Tests point evaluation precompile for [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Test point evaluation precompile for [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501

import os
from typing import Annotated, List

import pytest
from ethereum.crypto.hash import keccak256
from pydantic import BaseModel, BeforeValidator, ConfigDict, RootModel, TypeAdapter
from pydantic.alias_generators import to_pascal

from ethereum_test_tools import Environment, StateTestFiller, TestAddress, Transaction
from ethereum_test_tools.vm import Opcodes as Op

from .spec import FORK, Spec, ref_spec_2537

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = pytest.mark.valid_from(str(FORK))


def current_python_script_directory() -> str:
    """
    Get the current Python script directory.
    """
    return os.path.dirname(os.path.realpath(__file__))


class TestVector(BaseModel):
    """
    Test vector for the BLS12-381 precompiles.
    """

    input: Annotated[bytes, BeforeValidator(bytes.fromhex)]
    expected: Annotated[bytes, BeforeValidator(bytes.fromhex)]
    gas: int
    name: str

    model_config = ConfigDict(alias_generator=to_pascal)

    def to_pytest_param(self):
        """
        Convert the test vector to a tuple that can be used as a parameter in a pytest test.
        """
        return pytest.param(self.input, self.expected, self.gas, id=self.name)


class TestVectorList(RootModel):
    """
    List of test vectors for the BLS12-381 precompiles.
    """

    root: List[TestVector]


TestVectorListAdapter = TypeAdapter(TestVectorList)


def vectors_from_file(filename: str) -> List[pytest.param]:
    """
    Load test vectors from a file.
    """
    full_path = os.path.join(
        current_python_script_directory(),
        "vectors",
        filename,
    )
    with open(full_path, "rb") as f:
        return [v.to_pytest_param() for v in TestVectorListAdapter.validate_json(f.read()).root]


sstore_key_expected_result = 0
sstore_key_expected_output_length = 1
sstore_key_expected_sha3 = 2


@pytest.fixture
def call_contract_code(precompile_address: int, precompile_gas: int) -> bytes:
    """Code of the test contract."""
    return (
        Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
        + Op.SSTORE(
            sstore_key_expected_result,
            Op.CALL(
                precompile_gas,
                precompile_address,
                0,
                0,
                Op.CALLDATASIZE(),
                0,
                0,
            ),
        )
        + Op.SSTORE(sstore_key_expected_output_length, Op.RETURNDATASIZE())
        + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE())
        + Op.SSTORE(sstore_key_expected_sha3, Op.SHA3(0, Op.RETURNDATASIZE()))
    )


@pytest.fixture
def call_contract_address() -> int:
    """Code of the test contract."""
    return 0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA


@pytest.fixture
def pre(call_contract_address: int, call_contract_code: bytes):
    """Code of the test contract."""
    return {
        call_contract_address: {
            "balance": 0,
            "nonce": 0,
            "code": call_contract_code,
        },
        TestAddress: {
            "balance": 1_000_000_000_000_000,
            "nonce": 0,
        },
    }


@pytest.fixture
def post(call_contract_address: int, expected_output: bytes):
    """Code of the test contract."""
    return {
        call_contract_address: {
            "storage": {
                sstore_key_expected_result: 1,
                sstore_key_expected_output_length: len(expected_output),
                sstore_key_expected_sha3: keccak256(expected_output),
            },
        },
    }


@pytest.fixture
def tx(input: bytes, call_contract_address: int) -> Transaction:
    """Transaction for the test."""
    return Transaction(
        gas_limit=10_000_000,
        input=input,
        to=call_contract_address,
    )


@pytest.mark.parametrize(
    "input,expected_output,precompile_gas", vectors_from_file("add_G1_bls.json")
)
@pytest.mark.parametrize("precompile_address", [Spec.BLS12_G1ADD])
def test_add_g1(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G1ADD precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output,precompile_gas",
    vectors_from_file("add_G2_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.BLS12_G2ADD])
def test_add_g2(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G2ADD precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output,precompile_gas",
    vectors_from_file("mul_G1_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.BLS12_G1MUL])
def test_mul_g1(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G1MUL precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output,precompile_gas",
    vectors_from_file("mul_G2_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.BLS12_G2MUL])
def test_mul_g2(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G2MUL precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output,precompile_gas",
    vectors_from_file("multiexp_G1_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.BLS12_G1MSM])
def test_msm_g1(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G1MSM precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output,precompile_gas",
    vectors_from_file("multiexp_G2_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.BLS12_G2MSM])
def test_msm_g2(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G2MSM precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output,precompile_gas",
    vectors_from_file("map_fp_to_G1_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.BLS12_MAP_FP_TO_G1])
def test_map_fp_to_g1(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_MAP_FP_TO_G1 precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output,precompile_gas",
    vectors_from_file("map_fp2_to_G2_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.BLS12_MAP_FP2_TO_G2])
def test_map_fp2_to_g2(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_MAP_FP2_TO_G2 precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
