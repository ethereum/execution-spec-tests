import os  # noqa: D100
from pathlib import Path

from evm_transition_tool import EVMTransactionTrace
from evm_transition_tool.traces import EVMCallFrameLine

FIXTURES_ROOT = Path(os.path.join("src", "evm_transition_tool", "tests", "fixtures"))


def test_transaction_trace_parsing():
    """
    Simple transaction test parsing
    """
    alloc_path = Path(FIXTURES_ROOT, "traces_1.jsonl")
    with open(alloc_path, "r") as test_file_lines:
        trace = EVMTransactionTrace.from_file(
            file_handler=test_file_lines, transaction_hash="0x1234"
        )
    assert len(trace.trace) == 6
    assert trace.output.gas_used == 0x53089
    assert trace.trace[1].opcode_name == "PUSH1"
    assert trace.trace[1].gas_left == 0x74F18
    assert trace.trace[1].context_address == "0x0000000000000000000000000000000000000100"
    assert trace.trace[2].opcode_name == "PUSH1"
    assert trace.trace[2].gas_left == 0x74F15
    assert trace.trace[2].context_address == "0x0000000000000000000000000000000000000100"
    assert trace.trace[3].opcode_name == "PUSH1"
    assert trace.trace[3].gas_left == 0x74F12
    assert trace.trace[3].context_address == "0x0000000000000000000000000000000000000100"
    assert trace.trace[5].opcode_name == "PUSH1"
    assert trace.trace[5].context_address == "0x0000000000000000000000000000000000000200"


def test_call_frame_line_parsing():
    """
    Simple call frame line test parsing
    """
    EVMCallFrameLine(
        **{
            "from": "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b",
            "to": "0x0000000000000000000000000000000000000100",
            "gas": "0x74f18",
            "value": "0x0",
        }
    )
