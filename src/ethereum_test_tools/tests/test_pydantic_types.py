"""
Types experiment
"""

import json
from typing import Any, Dict

import pytest
from pydantic import TypeAdapter

from ethereum_test_forks import Cancun, Shanghai
from ethereum_test_tools.common import (
    Address,
    Environment,
    Hash,
    HexNumber,
    Number,
    ZeroPaddedHexNumber,
)
from ethereum_test_tools.common.json import to_json
from ethereum_test_tools.common.types import Result
from ethereum_test_tools.spec.blockchain.types import FixtureExecutionPayload, FixtureHeader


@pytest.mark.parametrize(
    "test_type,expected_serialization",
    [
        pytest.param(Number, '"1"', id="Number"),
        pytest.param(HexNumber, '"0x1"', id="HexNumber"),
        pytest.param(ZeroPaddedHexNumber, '"0x01"', id="ZeroPaddedHexNumber"),
        pytest.param(Address, '"0x0000000000000000000000000000000000000001"', id="Address"),
        pytest.param(
            Hash, '"0x0000000000000000000000000000000000000000000000000000000000000001"', id="Hash"
        ),
    ],
)
@pytest.mark.parametrize(
    "validate_python",
    [
        pytest.param(1, id="int"),
        pytest.param("1", id="str"),
        pytest.param("0x1", id="hex"),
    ],
)
def test_base_types(test_type: type, validate_python: Any, expected_serialization: str):
    """
    Test pydantic aspect of base types
    """
    adapter = TypeAdapter(test_type)  # type: ignore
    validated = adapter.validate_python(validate_python)
    assert isinstance(validated, test_type)
    assert adapter.dump_json(validated).decode(encoding="utf-8") == expected_serialization


def model_dump(model: Any, **kwargs) -> Dict:
    """
    Dump the model
    """
    return json.loads(model.model_dump_json(**kwargs).encode(encoding="utf-8"))


def test_sanity():
    """
    Sanity test
    """
    env = Environment(
        prev_randao=0,
        base_fee_per_gas=7,
        withdrawals=[],
        difficulty="0",
    )
    assert (
        env.fee_recipient
        == b"\x2a\xdc\x25\x66\x50\x18\xaa\x1f\xe0\xe6\xbc\x66\x6d\xac\x8f\xc2\x69\x7f\xf9\xba"
    )
    assert env.base_fee_per_gas == 7

    # We send the environment to the t8n
    assert to_json(env) == {
        "currentCoinbase": "0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        "currentGasLimit": "100000000000000000",
        "currentNumber": "1",
        "currentTimestamp": "1000",
        "currentRandom": "0",
        "currentDifficulty": "0",
        "blockHashes": {},
        "ommers": [],
        "withdrawals": [],
        "currentBaseFee": "7",
        "parentUncleHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    }

    assert "fee_recipient" in dict(env)

    result_dump = {
        "stateRoot": "0xf2e5f99c03e64ce121cb0f6e60f51d77d041010a2994dfa477a7f3a69a378ec7",
        "txRoot": "0xeb73a3f9c75d464ce0e4f1e793f7a82e85adf5037b15b898018e5de05790ebd7",
        "receiptsRoot": "0xeea4432237eee3d73482f5a674f165ebb4cabd2d612e18167c4ebfdcaad7b18a",
        "logsHash": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
        "logsBloom": "0x" + "00" * 256,
        "receipts": [
            {
                "root": "0x",
                "status": "0x1",
                "cumulativeGasUsed": "0x8e751",
                "logsBloom": "0x" + "00" * 256,
                "transactionHash": (
                    "0xa6657bfa5bcc143ebf2a425572c5a26c51b43563b15542b1c1039c301571ea36"
                ),
                "contractAddress": "0x6295ee1b4f6dd65047762f924ecd367c17eabf8f",
                "gasUsed": "0x8e751",
                "blockHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "transactionIndex": "0x0",
            }
        ],
        "rejected": [],
        "gasUsed": "0x8e751",
        "currentBaseFee": "0x7",
        "withdrawalsRoot": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",
    }
    result = Result(**result_dump)
    assert to_json(result) == result_dump

    # We combine the environment and the result to create a FixtureHeader
    fixture_header = FixtureHeader(
        **(env.model_dump(exclude_none=True) | result.model_dump(exclude_none=True)),
        parent_hash=0,
        extra_data=b"",
        fork=Shanghai,
    )
    assert fixture_header.fee_recipient == env.fee_recipient
    assert fixture_header.state_root == result.state_root
    assert isinstance(fixture_header.fee_recipient, bytes)
    assert isinstance(fixture_header.state_root, bytes)

    # Assert that the same fixture header would fail on Cancun because of the missing fields
    with pytest.raises(ValueError):
        FixtureHeader(
            **(env.model_dump(exclude_none=True) | result.model_dump(exclude_none=True)),
            fork=Cancun,
        )

    # We create a FixtureExecutionPayload
    transactions = []  # Obtained during block creation
    fixture_execution_payload = FixtureExecutionPayload(
        **fixture_header.model_dump(exclude={"rlp"}, exclude_none=True), transactions=transactions
    )
    assert fixture_execution_payload.fee_recipient == fixture_header.fee_recipient
    assert fixture_execution_payload.state_root == fixture_header.state_root
    assert isinstance(fixture_execution_payload.fee_recipient, bytes)
    assert isinstance(fixture_execution_payload.state_root, bytes)
