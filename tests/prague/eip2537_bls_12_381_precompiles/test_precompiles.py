"""
abstract: Tests point evaluation precompile for [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Test point evaluation precompile for [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501

import os
from typing import Annotated, List, SupportsBytes

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
    Scalar,
    Spec,
    map_fp_to_g1_format,
    ref_spec_2537,
)

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = pytest.mark.valid_from(str(FORK))


###
# Helpers
###


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


###
# Fixtures
###


@pytest.fixture
def precompile_gas(precompile_address: int, input: bytes) -> int:
    """Gas cost for the precompile."""
    return GAS_CALCULATION_FUNCTION_MAP[precompile_address](len(input))


@pytest.fixture
def precompile_gas_modifier() -> int:
    """
    Used to modify the gas passed to the precompile, for testing purposes.

    By default the call is made with the exact gas amount required for the given opcode,
    but when this fixture is overridden, the gas amount can be modified to, e.g., test
    a lower amount and test if the precompile call fails.
    """
    return 0


@pytest.fixture
def call_opcode() -> Op:
    """
    Type of call used to call the precompile.

    By default it is Op.CALL, but it can be overridden in the test.
    """
    return Op.CALL


@pytest.fixture
def call_contract_post_storage() -> Storage:
    """
    Storage of the test contract after the transaction is executed.
    Note: Fixture `call_contract_code` fills the actual expected storage values.
    """
    return Storage()


@pytest.fixture
def call_contract_code(
    precompile_address: int,
    precompile_gas: int,
    precompile_gas_modifier: int,
    expected_output: bytes | SupportsBytes,
    call_opcode: Op,
    call_contract_post_storage: Storage,
) -> bytes:
    """Code of the test contract."""
    expected_output = bytes(expected_output)

    # Depending on the expected output, we can deduce if the call is expected to succeed or fail.
    call_succeeds = len(expected_output) > 0

    assert call_opcode in [Op.CALL, Op.CALLCODE, Op.DELEGATECALL, Op.STATICCALL]
    value = [0] if call_opcode in [Op.CALL, Op.CALLCODE] else []

    code = (
        Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
        + Op.SSTORE(
            call_contract_post_storage.store_next(call_succeeds),
            call_opcode(
                precompile_gas + precompile_gas_modifier,
                precompile_address,
                *value,  # Optional, only used for CALL and CALLCODE.
                0,
                Op.CALLDATASIZE(),
                0,
                0,
            ),
        )
        + Op.SSTORE(
            call_contract_post_storage.store_next(len(expected_output)),
            Op.RETURNDATASIZE(),
        )
        + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE())
        + Op.SSTORE(
            call_contract_post_storage.store_next(keccak256(expected_output)),
            Op.SHA3(0, Op.RETURNDATASIZE()),
        )
    )
    return code


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
            "nonce": 1,
            "code": call_contract_code,
        },
        TestAddress: {
            "balance": 1_000_000_000_000_000,
            "nonce": 0,
        },
    }


@pytest.fixture
def post(call_contract_address: int, call_contract_post_storage: Storage):
    """Test expected post outcome."""
    return {
        call_contract_address: {
            "storage": call_contract_post_storage,
        },
    }


@pytest.fixture
def tx_gas_limit() -> int:
    """
    Transaction gas limit used for the test (Can be overridden in the test).
    """
    return 10_000_000


@pytest.fixture
def tx(input: bytes, tx_gas_limit: int, call_contract_address: int) -> Transaction:
    """Transaction for the test."""
    return Transaction(
        gas_limit=tx_gas_limit,
        input=input,
        to=call_contract_address,
    )


###
# Test cases
###


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("add_G1_bls.json")
    + [
        pytest.param(
            Spec.INF_G1 + Spec.INF_G1,
            Spec.INF_G1,
            id="inf_plus_inf",
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
    Test the BLS12_G1ADD precompile.
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
            PointG1(0, 1) + Spec.INF_G1,
            id="invalid_point_a_1",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.y - 1) + Spec.INF_G1,
            id="invalid_point_a_2",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.y + 1) + Spec.INF_G1,
            id="invalid_point_a_3",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.x) + Spec.INF_G1,
            id="invalid_point_a_4",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(0, 1),
            id="invalid_point_b_1",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(Spec.P1.x, Spec.P1.y - 1),
            id="invalid_point_b_2",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(Spec.P1.x, Spec.P1.y + 1),
            id="invalid_point_b_3",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(Spec.P1.x, Spec.P1.x),
            id="invalid_point_b_4",
        ),
        pytest.param(
            PointG1(Spec.P, 0) + Spec.INF_G1,
            id="a_x_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(Spec.P, 0),
            id="b_x_equal_to_p",
        ),
        pytest.param(
            PointG1(0, Spec.P) + Spec.INF_G1,
            id="a_y_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(0, Spec.P),
            id="b_y_equal_to_p",
        ),
        pytest.param(
            (Spec.INF_G1 + PointG1(Spec.P1.x, Spec.P1.x))[:-1],
            id="input_too_short",
        ),
        pytest.param(
            b"\x00" + (Spec.INF_G1 + PointG1(Spec.P1.x, Spec.P1.x)),
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
    Negative tests for the BLS12_G1ADD precompile.
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
    Test the BLS12_G2ADD precompile.
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
            PointG2((1, 0), (0, 0)) + Spec.INF_G2,
            id="invalid_point_a_1",
        ),
        pytest.param(
            PointG2((0, 0), (1, 0)) + Spec.INF_G2,
            id="invalid_point_a_2",
        ),
        pytest.param(
            PointG2((0, 1), (0, 0)) + Spec.INF_G2,
            id="invalid_point_a_3",
        ),
        pytest.param(
            PointG2((0, 0), (0, 1)) + Spec.INF_G2,
            id="invalid_point_a_4",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((1, 0), (0, 0)),
            id="invalid_point_b_1",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, 0), (1, 0)),
            id="invalid_point_b_2",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, 1), (0, 0)),
            id="invalid_point_b_3",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, 0), (0, 1)),
            id="invalid_point_b_4",
        ),
        pytest.param(
            PointG2((Spec.P, 0), (0, 0)) + Spec.INF_G2,
            id="a_x_1_equal_to_p",
        ),
        pytest.param(
            PointG2((0, Spec.P), (0, 0)) + Spec.INF_G2,
            id="a_x_2_equal_to_p",
        ),
        pytest.param(
            PointG2((0, 0), (Spec.P, 0)) + Spec.INF_G2,
            id="a_y_1_equal_to_p",
        ),
        pytest.param(
            PointG2((0, 0), (0, Spec.P)) + Spec.INF_G2,
            id="a_y_2_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((Spec.P, 0), (0, 0)),
            id="b_x_1_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, Spec.P), (0, 0)),
            id="b_x_2_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, 0), (Spec.P, 0)),
            id="b_y_1_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, 0), (0, Spec.P)),
            id="b_y_2_equal_to_p",
        ),
        pytest.param(
            (Spec.INF_G2 + Spec.INF_G2)[:-1],
            id="input_too_short",
        ),
        pytest.param(
            b"\x00" + (Spec.INF_G2 + Spec.INF_G2),
            id="input_too_long",
        ),
        pytest.param(
            b"",
            id="zero_length_input",
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
    Negative tests for the BLS12_G2ADD precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("mul_G1_bls.json")
    + [
        pytest.param(
            Spec.INF_G1 + Scalar(0),
            Spec.INF_G1,
            id="bls_g1mul_(0*inf=inf)",
        ),
        pytest.param(
            Spec.INF_G1 + Scalar(2**256 - 1),
            Spec.INF_G1,
            id="bls_g1mul_(2**256-1*inf=inf)",
        ),
        pytest.param(
            Spec.P1 + Scalar(2**256 - 1),
            PointG1(
                0x3DA1F13DDEF2B8B5A46CD543CE56C0A90B8B3B0D6D43DEC95836A5FD2BACD6AA8F692601F870CF22E05DDA5E83F460B,  # noqa: E501
                0x18D64F3C0E9785365CBDB375795454A8A4FA26F30B9C4F6E33CA078EB5C29B7AEA478B076C619BC1ED22B14C95569B2D,  # noqa: E501
            ),
            id="bls_g1mul_(2**256-1*P1)",
        ),
        pytest.param(
            Spec.P1 + Scalar(Spec.Q - 1),
            -Spec.P1,  # negated P1
            id="bls_g1mul_(q-1*P1)",
        ),
        pytest.param(
            Spec.P1 + Scalar(Spec.Q),
            Spec.INF_G1,
            id="bls_g1mul_(q*P1)",
        ),
        pytest.param(
            Spec.P1 + Scalar(Spec.Q + 1),
            Spec.P1,
            id="bls_g1mul_(q+1*P1)",
        ),
        pytest.param(
            Spec.P1 + Scalar(2 * Spec.Q),
            Spec.INF_G1,
            id="bls_g1mul_(2q*P1)",
        ),
        pytest.param(
            Spec.P1 + Scalar((2**256 // Spec.Q) * Spec.Q),
            Spec.INF_G1,
            id="bls_g1mul_(Nq*P1)",
        ),
    ],
)
@pytest.mark.parametrize("precompile_address", [Spec.G1MUL], ids=[""])
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
    "input",
    [
        pytest.param(
            PointG1(0, 1) + Scalar(0),
            id="invalid_point_1",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.y - 1) + Scalar(0),
            id="invalid_point_2",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.y + 1) + Scalar(0),
            id="invalid_point_3",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.x) + Scalar(0),
            id="invalid_point_4",
        ),
        pytest.param(
            (Spec.INF_G1 + Scalar(0))[:-1],
            id="input_too_short",
        ),
        pytest.param(
            b"\x00" + (Spec.INF_G1 + Scalar(0)),
            id="input_too_long",
        ),
        pytest.param(
            b"",
            id="zero_length_input",
        ),
    ],
)
@pytest.mark.parametrize("expected_output", [b""], ids=[""])
@pytest.mark.parametrize("precompile_address", [Spec.G1MUL], ids=[""])
def test_mul_g1_negative(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Negative tests for the BLS12_G1MUL precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("mul_G2_bls.json")
    + [
        pytest.param(
            Spec.INF_G2 + Scalar(0),
            Spec.INF_G2,
            id="bls_g2mul_(0*inf=inf)",
        ),
        pytest.param(
            Spec.INF_G2 + Scalar(2**256 - 1),
            Spec.INF_G2,
            id="bls_g2mul_(2**256-1*inf=inf)",
        ),
        pytest.param(
            Spec.P2 + Scalar(2**256 - 1),
            PointG2(
                (
                    0x2663E1C3431E174CA80E5A84489569462E13B52DA27E7720AF5567941603475F1F9BC0102E13B92A0A21D96B94E9B22,  # noqa: E501
                    0x6A80D056486365020A6B53E2680B2D72D8A93561FC2F72B960936BB16F509C1A39C4E4174A7C9219E3D7EF130317C05,  # noqa: E501
                ),
                (
                    0xC49EAD39E9EB7E36E8BC25824299661D5B6D0E200BBC527ECCB946134726BF5DBD861E8E6EC946260B82ED26AFE15FB,  # noqa: E501
                    0x5397DAD1357CF8333189821B737172B18099ECF7EE8BDB4B3F05EBCCDF40E1782A6C71436D5ACE0843D7F361CBC6DB2,  # noqa: E501
                ),
            ),
            id="bls_g2mul_(2**256-1*P2)",
        ),
        pytest.param(
            Spec.P2 + Scalar(Spec.Q - 1),
            -Spec.P2,  # negated P2
            id="bls_g2mul_(q-1*P2)",
        ),
        pytest.param(
            Spec.P2 + Scalar(Spec.Q),
            Spec.INF_G2,
            id="bls_g2mul_(q*P2)",
        ),
        pytest.param(
            Spec.P2 + Scalar(Spec.Q + 1),
            Spec.P2,
            id="bls_g2mul_(q+1*P2)",
        ),
        pytest.param(
            Spec.P2 + Scalar(2 * Spec.Q),
            Spec.INF_G2,
            id="bls_g2mul_(2q*P2)",
        ),
        pytest.param(
            Spec.P2 + Scalar((2**256 // Spec.Q) * Spec.Q),
            Spec.INF_G2,
            id="bls_g2mul_(Nq*P2)",
        ),
    ],
)
@pytest.mark.parametrize("precompile_address", [Spec.G2MUL], ids=[""])
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
    "input",
    [
        pytest.param(
            PointG2((1, 0), (0, 0)) + Scalar(0),
            id="invalid_point_a_1",
        ),
        pytest.param(
            PointG2((0, 1), (0, 0)) + Scalar(0),
            id="invalid_point_a_2",
        ),
        pytest.param(
            PointG2((0, 0), (1, 0)) + Scalar(0),
            id="invalid_point_a_3",
        ),
        pytest.param(
            PointG2((0, 0), (0, 1)) + Scalar(0),
            id="invalid_point_a_4",
        ),
        pytest.param(
            PointG2((Spec.P, 0), (0, 0)) + Scalar(0),
            id="x_1_equal_to_p",
        ),
        pytest.param(
            PointG2((0, Spec.P), (0, 0)) + Scalar(0),
            id="x_2_equal_to_p",
        ),
        pytest.param(
            PointG2((0, 0), (Spec.P, 0)) + Scalar(0),
            id="y_1_equal_to_p",
        ),
        pytest.param(
            PointG2((0, 0), (0, Spec.P)) + Scalar(0),
            id="y_2_equal_to_p",
        ),
        pytest.param(
            (Spec.INF_G2 + Scalar(0))[:-1],
            id="input_too_short",
        ),
        pytest.param(
            b"\x00" + (Spec.INF_G2 + Scalar(0)),
            id="input_too_long",
        ),
        pytest.param(
            b"",
            id="zero_length_input",
        ),
    ],
)
@pytest.mark.parametrize("expected_output", [b""], ids=[""])
@pytest.mark.parametrize("precompile_address", [Spec.G2MUL], ids=[""])
def test_mul_g2_negative(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Negative tests for the BLS12_G2MUL precompile.
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
    Test the BLS12_G1MSM precompile.
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
    Test the BLS12_G2MSM precompile.
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
    Test the BLS12_MAP_FP_TO_G1 precompile.
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
    Test the BLS12_MAP_FP_TO_G1 precompile.
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
    Test the BLS12_MAP_FP2_TO_G2 precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
