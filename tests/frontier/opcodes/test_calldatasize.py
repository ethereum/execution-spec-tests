"""test `CALLDATASIZE` opcode."""

import pytest

from ethereum_test_forks import Byzantium, Fork
from ethereum_test_tools import Account, Alloc, Bytecode, StateTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op
