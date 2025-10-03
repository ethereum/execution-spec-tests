"""
abstract: Tests that benchmark EVMs in worst-case compute scenarios.
    Tests that benchmark EVMs in worst-case compute scenarios.

Tests that benchmark EVMs when running worst-case compute opcodes and precompile scenarios.
"""

import csv
import pathlib

import pytest

from ethereum_test_tools import (
    Alloc,
    StateTestFiller,
    Transaction,
)

BASE_DIR = pathlib.Path(__file__).parent
input_dir = BASE_DIR / "data"

entries = []

for csv_file in input_dir.glob("*.csv"):
    print(csv_file)
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            program_id = row["program_id"]
            opcode = row["opcode"]
            op_count = row["op_count"]
            bytecode = row["bytecode"]
            entries.append((program_id + " opcode: " + opcode + " count: " + op_count, bytecode))


@pytest.mark.parametrize("name,bytecode", entries, ids=[e[0] for e in entries])
def test_opcode(state_test: StateTestFiller, pre: Alloc, name, bytecode):
    """Tests the provided benchmarks from the imapp-gas-cost-estimator."""
    tx = Transaction(
        to=None,
        gas_limit=10_000_000,
        data=bytecode,
        sender=pre.fund_eoa(),
    )
    state_test(
        pre=pre,
        post={},
        tx=tx,
    )
