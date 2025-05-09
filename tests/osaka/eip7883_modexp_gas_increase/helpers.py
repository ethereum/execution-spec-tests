"""Helper functions for the EIP-7883 ModExp gas cost increase tests."""

import json
import os
from typing import List, Tuple

import pytest


def current_python_script_directory(*args: str) -> str:
    """Get the current Python script directory."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), *args)


def vectors_from_file(filename: str) -> List[Tuple]:
    """Load test vectors from a file."""
    with open(current_python_script_directory(filename), "r") as f:
        vectors_json = json.load(f)
        result = []
        for vector in vectors_json:
            input_hex = vector["Input"]
            name = vector["Name"]
            gas_new = vector["GasNew"]
            param = pytest.param(
                bytes.fromhex(input_hex),
                gas_new,
                id=name,
            )
            result.append(param)
        return result


def parse_modexp_input(input_data: bytes) -> Tuple[bytes, bytes, bytes, int]:
    """Parse ModExp input data into base, exponent bytes, modulus, and exponent value."""
    base_length = int.from_bytes(input_data[0:32], byteorder="big")
    exponent_length = int.from_bytes(input_data[32:64], byteorder="big")
    modulus_length = int.from_bytes(input_data[64:96], byteorder="big")

    base_start = 96
    base_end = base_start + base_length
    base = input_data[base_start:base_end]

    exponent_start = base_end
    exponent_end = exponent_start + exponent_length
    exponent_bytes = input_data[exponent_start:exponent_end]
    exponent_value = int.from_bytes(exponent_bytes, byteorder="big")

    modulus_start = exponent_end
    modulus_end = modulus_start + modulus_length
    modulus = input_data[modulus_start:modulus_end]

    return base, exponent_bytes, modulus, exponent_value
