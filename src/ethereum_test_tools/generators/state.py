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
