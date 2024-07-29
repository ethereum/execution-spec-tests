"""
Includes state test generators to use in Ethereum tests.
"""
from enum import Enum
from typing import Any, Callable, List

import pytest

from ethereum_test_base_types import Account
from ethereum_test_specs import StateTestFiller
from ethereum_test_types import Alloc, Environment, Transaction, eip_2028_transaction_data_cost
from ethereum_test_vm import Bytecode
from ethereum_test_vm import Opcodes as Op

Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]


class GasTestType(str, Enum):
    """
    Enum to list the types of gas tests that can be generated.
    """

    EXACT_GAS = "exact_gas"
    OOG = "oog"


def bytecode_gas_test(
    *,
    gas_test_types: List[GasTestType] | GasTestType = list(GasTestType),
    with_data: bool = False,
) -> Decorator:
    """
    Used to generate a parametrized test that checks that specified gas is
    exactly the same as the gas used by the EVM.

    Automatically generates an exact-gas test, where the transaction is sent
    with the exact amount of gas required, and an out-of-gas test, where the
    transaction is sent with one less gas than required.

    Body of the decorated test is ignored.

    Required fixtures:
      pre: Alloc - Automatically provided by filler.
      state_test: StateTestFiller - Automatically provided by filler.
      exact_gas_cost: int - Exact gas cost required to execute the bytecode.
      bytecode: Bytecode, the bytecode to be tested.

    Optional fixtures:
      data: bytes - if `with_data` is True, is the transaction calldata.

    Args:
      gas_test_types: List[GasTestType] | GasTestType = list(GasTestType) - List of gas test types
        to generate.
      with_data: bool = False - If True, a `data` fixture needs to be defined and will be
        included.
    """
    if type(gas_test_types) is GasTestType:
        gas_test_types = [gas_test_types]

    assert type(gas_test_types) is list

    def generator(
        pre: Alloc,
        state_test: StateTestFiller,
        exact_gas_cost: int,
        gas_test_type: GasTestType,
        bytecode: Bytecode,
        data: bytes = b"",
        env: Environment = Environment(),
    ):
        """
        Generate a test case that can be further parametrized to verify gas comsumption of a
        specific EVM bytecode.
        """
        test_code = Op.SSTORE(0xBA5E, 1) + bytecode + Op.STOP()
        test_code_address = pre.deploy_contract(code=test_code)
        total_gas = (
            # Intrinsic tx cost
            21_000
            + 2_100  # Cold account access cost
            + eip_2028_transaction_data_cost(data)
            + 20_000  # Op.SSTORE
            + 3  # Op.PUSH2
            + 3  # Op.PUSH1(1)
            + exact_gas_cost
        )
        tx = Transaction(
            sender=pre.fund_eoa(),
            to=test_code_address,
            data=data,
            gas_limit=total_gas if gas_test_type == GasTestType.EXACT_GAS else total_gas - 1,
        )
        post = {
            test_code_address: Account(
                storage={0xBA5E: 1} if gas_test_type == GasTestType.EXACT_GAS else {}
            )
        }
        state_test(
            env=env,
            pre=pre,
            post=post,
            tx=tx,
        )

    if with_data:

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @pytest.mark.parametrize(
                "gas_test_type",
                gas_test_types,
                ids=lambda x: x.value,
            )
            def generated_gas_test(
                pre: Alloc,
                state_test: StateTestFiller,
                exact_gas_cost: int,
                gas_test_type: GasTestType,
                bytecode: Bytecode,
                data: bytes,
            ):
                generator(
                    pre=pre,
                    state_test=state_test,
                    exact_gas_cost=exact_gas_cost,
                    gas_test_type=gas_test_type,
                    bytecode=bytecode,
                    data=data,
                )

            generated_gas_test.__name__ = func.__name__
            generated_gas_test.__doc__ = func.__doc__

            return generated_gas_test

    else:

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @pytest.mark.parametrize(
                "gas_test_type",
                gas_test_types,
                ids=lambda x: x.value,
            )
            def generated_gas_test(
                pre: Alloc,
                state_test: StateTestFiller,
                exact_gas_cost: int,
                gas_test_type: GasTestType,
                bytecode: Bytecode,
            ):
                generator(
                    pre=pre,
                    state_test=state_test,
                    exact_gas_cost=exact_gas_cost,
                    gas_test_type=gas_test_type,
                    bytecode=bytecode,
                )

            generated_gas_test.__name__ = func.__name__
            generated_gas_test.__doc__ = func.__doc__

            return generated_gas_test

    return decorator
