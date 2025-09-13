"""
abstract: Test [EIP-7823: Set upper bounds for MODEXP](https://eips.ethereum.org/EIPS/eip-7823)
    Tests upper bounds of the MODEXP precompile.
"""

from typing import Dict

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Bytes,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ...byzantium.eip198_modexp_precompile.helpers import ModExpInput, ModExpOutput
from .spec import Spec, ref_spec_7823

REFERENCE_SPEC_GIT_PATH = ref_spec_7823.git_path
REFERENCE_SPEC_VERSION = ref_spec_7823.version


@pytest.mark.valid_from("Osaka")
@pytest.mark.parametrize(
    "modexp_input,modexp_expected,call_succeeds",
    [
        pytest.param(
            ModExpInput(
                base=b"\0" * (Spec.MAX_LENGTH_BYTES + 1),
                exponent=b"\0",
                modulus=b"\2",
            ),
            Spec.modexp_error,
            False,
            id="excess_length_base",
        ),
        pytest.param(
            ModExpInput(
                base=b"\0",
                exponent=b"\0" * (Spec.MAX_LENGTH_BYTES + 1),
                modulus=b"\2",
            ),
            Spec.modexp_error,
            False,
            id="excess_length_exponent",
        ),
        pytest.param(
            ModExpInput(
                base=b"\0",
                exponent=b"\0",
                modulus=b"\0" * (Spec.MAX_LENGTH_BYTES) + b"\2",
            ),
            Spec.modexp_error,
            False,
            id="excess_length_modulus",
        ),
        pytest.param(
            ModExpInput(
                base=b"",
                exponent=b"\0" * (Spec.MAX_LENGTH_BYTES + 1),
                modulus=b"",
            ),
            Spec.modexp_error,
            False,
            id="exp_1025_base_0_mod_0",
        ),
        pytest.param(
            ModExpInput(
                base=b"",
                # Non-zero exponent is cancelled with zero multiplication complexity pre EIP-7823.
                exponent=b"\xff" * (Spec.MAX_LENGTH_BYTES + 1),
                modulus=b"",
            ),
            Spec.modexp_error,
            False,
            id="expFF_1025_base_0_mod_0",
        ),
        pytest.param(
            ModExpInput(
                base=b"\0" * Spec.MAX_LENGTH_BYTES,
                exponent=b"\xff" * (Spec.MAX_LENGTH_BYTES + 1),
                modulus=b"",
            ),
            Spec.modexp_error,
            False,
            id="expFF_1025_base_1024_mod_0",
        ),
        pytest.param(
            ModExpInput(
                base=b"\0" * (Spec.MAX_LENGTH_BYTES + 1),
                exponent=b"\xff" * (Spec.MAX_LENGTH_BYTES + 1),
                modulus=b"",
            ),
            Spec.modexp_error,
            False,
            id="expFF_1025_base_1025_mod_0",
        ),
        pytest.param(
            ModExpInput(
                base=b"\0" * (Spec.MAX_LENGTH_BYTES + 1),
                exponent=b"",
                modulus=b"",
            ),
            Spec.modexp_error,
            False,
            id="exp_0_base_1025_mod_0",
        ),
        pytest.param(
            ModExpInput(
                base=b"\0" * (Spec.MAX_LENGTH_BYTES + 1),
                exponent=b"",
                modulus=b"\2",
            ),
            Spec.modexp_error,
            False,
            id="exp_0_base_1025_mod_1",
        ),
        pytest.param(
            ModExpInput(
                base=b"",
                exponent=b"",
                modulus=b"\0" * (Spec.MAX_LENGTH_BYTES + 1),
            ),
            Spec.modexp_error,
            False,
            id="exp_0_base_0_mod_1025",
        ),
        pytest.param(
            ModExpInput(
                base=b"\1",
                exponent=b"",
                modulus=b"\0" * (Spec.MAX_LENGTH_BYTES + 1),
            ),
            Spec.modexp_error,
            False,
            id="exp_0_base_1_mod_1025",
        ),
        pytest.param(
            ModExpInput(
                base=b"",
                exponent=Bytes("80"),
                modulus=b"",
                declared_exponent_length=2**64,
            ),
            Spec.modexp_error,
            False,
            id="exp_2_pow_64_base_0_mod_0",
        ),
        # Implementation coverage tests
        pytest.param(
            ModExpInput(
                base=b"\xff" * (MAX_LENGTH_BYTES + 1),
                exponent=b"\xff" * (MAX_LENGTH_BYTES + 1),
                modulus=b"\xff" * (MAX_LENGTH_BYTES + 1),
            ),
            id="all_exceed_check_ordering",
        ),
        pytest.param(
            ModExpInput(
                base=b"\x00" * MAX_LENGTH_BYTES,
                exponent=b"\xff" * (MAX_LENGTH_BYTES + 1),
                modulus=b"\xff" * (MAX_LENGTH_BYTES + 1),
            ),
            id="exp_mod_exceed_base_ok",
        ),
        pytest.param(
            ModExpInput(
                # Bitwise pattern for Nethermind optimization
                base=b"\xaa" * (MAX_LENGTH_BYTES + 1),
                exponent=b"\x55" * MAX_LENGTH_BYTES,
                modulus=b"\xff" * MAX_LENGTH_BYTES,
            ),
            id="bitwise_pattern_base_exceed",
        ),
        pytest.param(
            ModExpInput(
                base=b"",
                exponent=b"",
                modulus=b"",
                # Near max uint64 for revm conversion test
                declared_base_length=2**63 - 1,
                declared_exponent_length=1,
                declared_modulus_length=1,
            ),
            id="near_uint64_max_base",
        ),
        pytest.param(
            ModExpInput(
                base=b"\x01" * MAX_LENGTH_BYTES,
                exponent=b"",
                modulus=b"\x02" * (MAX_LENGTH_BYTES + 1),
                declared_exponent_length=0,
            ),
            id="zero_exp_mod_exceed",
        ),
    ],
)
def test_modexp_input_bounds(
    state_test: StateTestFiller,
    modexp_input: ModExpInput,
    modexp_expected: ModExpOutput,
    precompile_gas: int,
    fork: Fork,
    tx: Transaction,
    post: Dict,
    pre: Alloc,
):
    """Test the MODEXP precompile input bounds."""
    state_test(pre=pre, tx=tx, post=post)


@pytest.mark.parametrize(
    "modexp_input,modexp_expected",
    [
        pytest.param(
            ModExpInput(
                base=b"\1" * (Spec.MAX_LENGTH_BYTES + 1),
                exponent=b"\0",
                modulus=b"\2",
            ),
            b"\1",
            id="base_1_exp_0_mod_2",
        ),
    ],
)
@pytest.mark.valid_at_transition_to("Osaka", subsequent_forks=True)
def test_modexp_upper_bounds_fork_transition(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    modexp_input: ModExpInput,
    modexp_expected: ModExpOutput,
):
    """Test MODEXP upper bounds enforcement transition from before to after Osaka hard fork."""
    call_code = Op.CALL(
        address=Spec.MODEXP_ADDRESS,
        args_size=Op.CALLDATASIZE,
    )
    gas_costs = fork.gas_costs()
    extra_gas = (
        gas_costs.G_WARM_ACCOUNT_ACCESS
        + (gas_costs.G_VERY_LOW * (len(Op.CALL.kwargs) - 2))  # type: ignore
        + (gas_costs.G_BASE * 3)
    )

    code = (
        Op.CALLDATACOPY(dest_offset=0, offset=0, size=Op.CALLDATASIZE)
        + Op.GAS  # [gas_start]
        + call_code  # [gas_start, call_result]
        + Op.GAS  # [gas_start, call_result, gas_end]
        + Op.SWAP1  # [gas_start, gas_end, call_result]
        + Op.POP  # [gas_start, gas_end]
        + Op.PUSH2[extra_gas]  # [gas_start, gas_end, extra_gas]
        + Op.ADD  # [gas_start, gas_end + extra_gas]
        + Op.SWAP1  # [gas_end + extra_gas, gas_start]
        + Op.SUB  # [gas_start - (gas_end + extra_gas)]
        + Op.TIMESTAMP  # [gas_start - (gas_end + extra_gas), TIMESTAMP]
        + Op.SSTORE  # []
    )

    # Verification the precompile call result
    code += Op.RETURNDATACOPY(dest_offset=0, offset=0, size=Op.RETURNDATASIZE()) + Op.SSTORE(
        Op.AND(Op.TIMESTAMP, 0xFF),
        Op.SHA3(0, Op.RETURNDATASIZE()),
    )

    senders = [pre.fund_eoa() for _ in range(3)]
    contracts = [pre.deploy_contract(code) for _ in range(3)]
    timestamps = [14_999, 15_000, 15_001]  # Before, at, and after transition
    expected_results = [True, False, False]

    blocks = [
        Block(
            timestamp=ts,
            txs=[
                Transaction(
                    to=contract,
                    data=bytes(modexp_input),
                    sender=sender,
                    gas_limit=6_000_000,
                )
            ],
        )
        for ts, contract, sender in zip(timestamps, contracts, senders, strict=False)
    ]

    post = {
        contract: Account(storage={ts: 1 if expected else 0})
        for contract, ts, expected in zip(contracts, timestamps, expected_results, strict=False)
    }

    blockchain_test(
        pre=pre,
        blocks=blocks,
        post=post,
    )
