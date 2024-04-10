"""
abstract: Tests point evaluation precompile for [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Test point evaluation precompile for [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501

import os
from typing import Annotated, List, SupportsBytes, Tuple

import pytest
from ethereum.crypto.hash import keccak256
from pydantic import BaseModel, BeforeValidator, ConfigDict, RootModel, TypeAdapter
from pydantic.alias_generators import to_pascal

from ethereum_test_tools import Environment, StateTestFiller, Storage, TestAddress, Transaction
from ethereum_test_tools.vm import Opcodes as Op

from .spec import (
    FORK,
    GAS_CALCULATION_FUNCTION_MAP,
    PointG1,
    PointG2,
    Spec,
    map_fp_to_g1_format,
    ref_spec_2537,
)

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
        return pytest.param(self.input, self.expected, id=self.name)


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


@pytest.fixture
def precompile_gas(precompile_address: int, input: bytes) -> int:
    """Gas cost for the precompile."""
    return GAS_CALCULATION_FUNCTION_MAP[precompile_address](len(input))


@pytest.fixture
def precompile_gas_modifier() -> int:
    """Used to modify the gas passed to the precompile, for testing purposes."""
    return 0


@pytest.fixture
def call_contract_code_storage(
    precompile_address: int,
    precompile_gas: int,
    precompile_gas_modifier: int,
    expected_output: bytes | SupportsBytes,
) -> Tuple[bytes, Storage]:
    """Code of the test contract."""
    storage = Storage()
    # Depending on the expected output, we can deduce if the call is expected to succeed or fail.
    expected_output = bytes(expected_output)
    call_succeeds = len(expected_output) > 0
    code = (
        Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
        + Op.SSTORE(
            storage.store_next(call_succeeds),
            Op.CALL(
                precompile_gas + precompile_gas_modifier,
                precompile_address,
                0,
                0,
                Op.CALLDATASIZE(),
                0,
                0,
            ),
        )
        + Op.SSTORE(
            storage.store_next(len(expected_output)),
            Op.RETURNDATASIZE(),
        )
        + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE())
        + Op.SSTORE(
            storage.store_next(keccak256(expected_output)),
            Op.SHA3(0, Op.RETURNDATASIZE()),
        )
    )
    return code, storage


@pytest.fixture
def call_contract_address() -> int:
    """Code of the test contract."""
    return 0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA


@pytest.fixture
def pre(call_contract_address: int, call_contract_code_storage: Tuple[bytes, Storage]):
    """Code of the test contract."""
    return {
        call_contract_address: {
            "balance": 0,
            "nonce": 0,
            "code": call_contract_code_storage[0],
        },
        TestAddress: {
            "balance": 1_000_000_000_000_000,
            "nonce": 0,
        },
    }


@pytest.fixture
def post(call_contract_address: int, call_contract_code_storage: Tuple[bytes, Storage]):
    """Code of the test contract."""
    return {
        call_contract_address: {
            "storage": call_contract_code_storage[1],
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
    "input,expected_output",
    vectors_from_file("add_G1_bls.json")
    + [
        pytest.param(
            Spec.ZERO_G1 + Spec.ZERO_G1,
            Spec.ZERO_G1,
            id="zero_plus_zero",
        ),
    ],
)
@pytest.mark.parametrize("precompile_address", [Spec.G1ADD], ids=[""])
def test_add_g1(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the G1ADD precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input",
    [
        pytest.param(
            PointG1(0, 1) + Spec.ZERO_G1,
            id="invalid_point_a_1",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.y - 1) + Spec.ZERO_G1,
            id="invalid_point_a_2",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.y + 1) + Spec.ZERO_G1,
            id="invalid_point_a_3",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.x) + Spec.ZERO_G1,
            id="invalid_point_a_4",
        ),
        pytest.param(
            Spec.ZERO_G1 + PointG1(0, 1),
            id="invalid_point_b_1",
        ),
        pytest.param(
            Spec.ZERO_G1 + PointG1(Spec.P1.x, Spec.P1.y - 1),
            id="invalid_point_b_2",
        ),
        pytest.param(
            Spec.ZERO_G1 + PointG1(Spec.P1.x, Spec.P1.y + 1),
            id="invalid_point_b_3",
        ),
        pytest.param(
            Spec.ZERO_G1 + PointG1(Spec.P1.x, Spec.P1.x),
            id="invalid_point_b_4",
        ),
        pytest.param(
            PointG1(Spec.P, 0) + Spec.ZERO_G1,
            id="a_x_equal_to_p",
        ),
        pytest.param(
            Spec.ZERO_G1 + PointG1(Spec.P, 0),
            id="b_x_equal_to_p",
        ),
        pytest.param(
            PointG1(0, Spec.P) + Spec.ZERO_G1,
            id="a_y_equal_to_p",
        ),
        pytest.param(
            Spec.ZERO_G1 + PointG1(0, Spec.P),
            id="b_y_equal_to_p",
        ),
        pytest.param(
            (Spec.ZERO_G1 + PointG1(Spec.P1.x, Spec.P1.x))[:-1],
            id="input_too_short",
        ),
        pytest.param(
            b"\x00" + (Spec.ZERO_G1 + PointG1(Spec.P1.x, Spec.P1.x)),
            id="input_too_long",
        ),
        pytest.param(
            b"",
            id="zero_length_input",
        ),
    ],
)
@pytest.mark.parametrize("expected_output", [b""], ids=[""])
@pytest.mark.parametrize("precompile_address", [Spec.G1ADD], ids=[""])
def test_add_g1_negative(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the G1ADD precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("add_G2_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.G2ADD], ids=[""])
def test_add_g2(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the G2ADD precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input",
    [
        pytest.param(
            PointG2((1, 0), (0, 0)) + Spec.ZERO_G2,
            id="invalid_point_a_1",
        ),
        pytest.param(
            PointG2((0, 0), (1, 0)) + Spec.ZERO_G2,
            id="invalid_point_a_2",
        ),
        pytest.param(
            PointG2((0, 1), (0, 0)) + Spec.ZERO_G2,
            id="invalid_point_a_3",
        ),
        pytest.param(
            PointG2((0, 0), (0, 1)) + Spec.ZERO_G2,
            id="invalid_point_a_4",
        ),
    ],
)
@pytest.mark.parametrize("expected_output", [b""], ids=[""])
@pytest.mark.parametrize("precompile_address", [Spec.G2ADD], ids=[""])
def test_add_g2_negative(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the G2ADD precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("mul_G1_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.G1MUL], ids=[""])
def test_mul_g1(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the G1MUL precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("mul_G2_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.G2MUL], ids=[""])
def test_mul_g2(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the G2MUL precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("multiexp_G1_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.G1MSM], ids=[""])
def test_msm_g1(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the G1MSM precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("multiexp_G2_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.G2MSM], ids=[""])
def test_msm_g2(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the G2MSM precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("map_fp_to_G1_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.MAP_FP_TO_G1], ids=[""])
def test_map_fp_to_g1(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the MAP_FP_TO_G1 precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input",
    [
        pytest.param(map_fp_to_g1_format(0)[1:], id="input_too_short"),
        pytest.param(b"\x00" + map_fp_to_g1_format(0), id="input_too_long"),
        pytest.param(b"", id="zero_lenght_input"),
        pytest.param(map_fp_to_g1_format(Spec.P), id="fq_eq_q"),
        pytest.param(map_fp_to_g1_format(2**381), id="fq_eq_2_381"),
        pytest.param(map_fp_to_g1_format(2**381 - 1), id="fq_eq_2_381_minus_1"),
        pytest.param(map_fp_to_g1_format(2**382), id="fq_eq_2_382"),
        pytest.param(map_fp_to_g1_format(2**382 - 1), id="fq_eq_2_382_minus_1"),
        pytest.param(map_fp_to_g1_format(2**383), id="fq_eq_2_383"),
        pytest.param(map_fp_to_g1_format(2**383 - 1), id="fq_eq_2_383_minus_1"),
        pytest.param(map_fp_to_g1_format(2**512 - 1), id="fq_eq_2_512_minus_1"),
    ],
)
@pytest.mark.parametrize("expected_output", [b""], ids=[""])
@pytest.mark.parametrize("precompile_address", [Spec.MAP_FP_TO_G1], ids=[""])
def test_map_fp_to_g1_negative(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the MAP_FP_TO_G1 precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("map_fp2_to_G2_bls.json"),
)
@pytest.mark.parametrize("precompile_address", [Spec.MAP_FP2_TO_G2], ids=[""])
def test_map_fp2_to_g2(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the MAP_FP2_TO_G2 precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
