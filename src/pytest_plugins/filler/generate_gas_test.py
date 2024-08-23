"""
Includes state test generators to use in Ethereum tests.
"""
from enum import Enum
from typing import Any, Callable, Mapping

import pytest

from ethereum_test_base_types import Account, Address
from ethereum_test_types import Alloc, Transaction, eip_2028_transaction_data_cost
from ethereum_test_vm import Bytecode
from ethereum_test_vm import Opcodes as Op

Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]


class GasTestType(str, Enum):
    """
    Enum to list the types of gas tests that can be generated.
    """

    EXACT_GAS = "exact_gas"
    OOG = "oog"


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """
    Hook to check if the test is marked with 'exact_gas_cost' and ensure that the required
    fixtures are present.
    """
    if item.get_closest_marker("generate_gas_test"):
        # TODO: This isn't hit yet.
        if "exact_gas_cost" not in item.fixturenames:
            pytest.error(
                "Tests marked with 'generate_gas_test' must define an `exact_gas_cost` fixture."
            )
        # TODO: Add a similar check for the 'data' fixture.


@pytest.fixture()
def data_checked(data: bytes) -> bytes:
    """
    Fixture to provide the data or an empty bytes array.
    """
    if data:
        return data
    return b""


@pytest.fixture
def total_gas(exact_gas_cost: int, data_checked: bytes) -> int:
    """
    Fixture to provide the exact gas cost required to execute the bytecode.
    """
    total_gas = (
        21_000  # Intrinsic tx cost
        + 2_100  # Cold account access cost
        + eip_2028_transaction_data_cost(data_checked)
        + 20_000  # Op.SSTORE
        + 3  # Op.PUSH2
        + 3  # Op.PUSH1(1)
        + exact_gas_cost
    )
    return total_gas


@pytest.fixture
def test_code_address(pre: Alloc, bytecode: Bytecode) -> Address:  # noqa: D103
    test_code = Op.SSTORE(0xBA5E, 1) + bytecode + Op.STOP()
    test_code_address = pre.deploy_contract(code=test_code)
    return test_code_address


@pytest.fixture()
def tx(
    pre: Alloc,
    gas_test_type: GasTestType,
    total_gas: int,
    test_code_address: Address,
    data_checked: bytes,
) -> Transaction:
    """
    Fixture to provide the transaction with the exact gas cost required to execute the bytecode.
    """
    return Transaction(
        sender=pre.fund_eoa(),
        to=test_code_address,
        data=data_checked,
        gas_limit=total_gas if gas_test_type == GasTestType.EXACT_GAS else total_gas - 1,
    )


@pytest.fixture()
def post(gas_test_type: GasTestType, test_code_address: Address) -> Mapping:
    """
    Return the post condition.
    """
    post = {
        test_code_address: Account(
            storage={0xBA5E: 1} if gas_test_type == GasTestType.EXACT_GAS else {}
        )
    }
    return post


def pytest_configure(config):
    """
    Register the 'exact_gas_cost' and 'with_data' markers.
    """
    config.addinivalue_line(
        "markers", "generate_gas_test(gas_test_types, with_data=False): Apply exact gas cost test"
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """
    Automatically use the `exact_gas_cost` fixture if the test is marked with `generate_gas_test`.
    """
    if item.get_closest_marker("generate_gas_test"):
        item.funcargs["exact_gas_cost"] = item._request.getfixturevalue("exact_gas_cost")
    yield


def pytest_generate_tests(metafunc):
    """
    This hook is used to parametrize tests based on the 'generate_gas_test' marker.
    """
    marker = metafunc.definition.get_closest_marker("generate_gas_test")
    if marker:
        gas_test_types = marker.kwargs.get("gas_test_types", list(GasTestType))

        if isinstance(gas_test_types, GasTestType):
            gas_test_types = [gas_test_types]

        metafunc.parametrize("gas_test_type", gas_test_types)
