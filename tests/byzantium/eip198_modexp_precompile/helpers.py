"""Helper functions for the EIP-198 ModExp precompile tests."""

from pydantic import Field

from ethereum_test_tools import Bytes, TestParameterGroup


class ModExpInput(TestParameterGroup):
    """
    Helper class that defines the MODEXP precompile inputs and creates the
    call data from them.

    Attributes:
        base (str): The base value for the MODEXP precompile.
        exponent (str): The exponent value for the MODEXP precompile.
        modulus (str): The modulus value for the MODEXP precompile.
        extra_data (str): Defines extra padded data to be added at the end of the calldata
            to the precompile. Defaults to an empty string.

    """

    base: Bytes
    exponent: Bytes
    modulus: Bytes
    extra_data: Bytes = Field(default_factory=Bytes)
    raw_input: Bytes | None = None

    override_base_length: int | None = None
    override_exponent_length: int | None = None
    override_modulus_length: int | None = None

    @property
    def length_base(self) -> Bytes:
        """Return the length of the base."""
        length = (
            self.override_base_length if self.override_base_length is not None else len(self.base)
        )
        return Bytes(length.to_bytes(32, "big"))

    @property
    def length_exponent(self) -> Bytes:
        """Return the length of the exponent."""
        length = (
            self.override_exponent_length
            if self.override_exponent_length is not None
            else len(self.exponent)
        )
        return Bytes(length.to_bytes(32, "big"))

    @property
    def length_modulus(self) -> Bytes:
        """Return the length of the modulus."""
        length = (
            self.override_modulus_length
            if self.override_modulus_length is not None
            else len(self.modulus)
        )
        return Bytes(length.to_bytes(32, "big"))

    @property
    def declared_base_length(self) -> int:
        """Return the declared base length as int."""
        return (
            self.override_base_length if self.override_base_length is not None else len(self.base)
        )

    @property
    def declared_exponent_length(self) -> int:
        """Return the declared exponent length as int."""
        return (
            self.override_exponent_length
            if self.override_exponent_length is not None
            else len(self.exponent)
        )

    @property
    def declared_modulus_length(self) -> int:
        """Return the declared modulus length as int."""
        return (
            self.override_modulus_length
            if self.override_modulus_length is not None
            else len(self.modulus)
        )

    def __bytes__(self):
        """Generate input for the MODEXP precompile."""
        if self.raw_input is not None:
            return self.raw_input
        return (
            self.length_base
            + self.length_exponent
            + self.length_modulus
            + self.base
            + self.exponent
            + self.modulus
            + self.extra_data
        )

    @classmethod
    def from_bytes(cls, input_data: Bytes | str) -> "ModExpInput":
        """
        Create a ModExpInput from a bytes object.

        Assumes correct formatting of the input data.
        """
        if isinstance(input_data, str):
            input_data = Bytes(input_data)
        assert not isinstance(input_data, str)
        padded_input_data = input_data
        if len(padded_input_data) < 96:
            padded_input_data = Bytes(padded_input_data.ljust(96, b"\0"))
        base_length = int.from_bytes(padded_input_data[0:32], byteorder="big")
        exponent_length = int.from_bytes(padded_input_data[32:64], byteorder="big")
        modulus_length = int.from_bytes(padded_input_data[64:96], byteorder="big")

        total_required_length = 96 + base_length + exponent_length + modulus_length
        if len(padded_input_data) < total_required_length:
            padded_input_data = Bytes(padded_input_data.ljust(total_required_length, b"\0"))

        current_index = 96
        base = padded_input_data[current_index : current_index + base_length]
        current_index += base_length

        exponent = padded_input_data[current_index : current_index + exponent_length]
        current_index += exponent_length

        modulus = padded_input_data[current_index : current_index + modulus_length]

        return cls(base=base, exponent=exponent, modulus=modulus, raw_input=input_data)

    @classmethod
    def create_mismatch(
        cls,
        base="",
        exponent="",
        modulus="",
        declared_base_length=None,
        declared_exponent_length=None,
        declared_modulus_length=None,
    ):
        """Create a ModExpInput with mismatched lengths."""
        return cls(
            base=Bytes(base),
            exponent=Bytes(exponent),
            modulus=Bytes(modulus),
            override_base_length=declared_base_length,
            override_exponent_length=declared_exponent_length,
            override_modulus_length=declared_modulus_length,
        )


class ModExpOutput(TestParameterGroup):
    """
    Expected test result.

    Attributes:
        call_success (bool): The return_code from CALL, 0 indicates unsuccessful call
            (out-of-gas), 1 indicates call succeeded.
        returned_data (str): The output returnData is the expected output of the call

    """

    call_success: bool = True
    returned_data: Bytes
