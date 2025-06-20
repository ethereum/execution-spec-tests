"""Helpers used to return fork-specific values."""


def ceiling_division(a: int, b: int) -> int:
    """
    Calculate the ceil without using floating point.
    Used by many of the EVM's formulas.
    """
    return -(a // -b)


def fake_exponential(factor: int, numerator: int, denominator: int) -> int:
    """Calculate the blob gas cost."""
    i = 1
    output = 0
    numerator_accumulator = factor * denominator
    while numerator_accumulator > 0:
        output += numerator_accumulator
        numerator_accumulator = (numerator_accumulator * numerator) // (denominator * i)
        i += 1
    return output // denominator


def ceil32(value: int) -> int:
    """Convert a unsigned integer to the next closest multiple of 32."""
    ceiling = 32
    remainder = value % ceiling
    if remainder == 0:
        return value
    else:
        return value + ceiling - remainder
