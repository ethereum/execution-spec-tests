"""
Defines EIP-2537 specification constants and functions.
"""
from dataclasses import dataclass
from typing import Callable, Sized, SupportsBytes, Tuple

from ethereum_test_forks import Prague


@dataclass(frozen=True)
class ReferenceSpec:
    """
    Defines the reference spec version and git path.
    """

    git_path: str
    version: str


ref_spec_2537 = ReferenceSpec("EIPS/eip-2537.md", "2bba479052f7901c1a981df09ba60cc409e0f3eb")

FORK = Prague


class BytesConcatenation(SupportsBytes, Sized):
    """
    A class that can be concatenated with bytes.
    """

    def __len__(self) -> int:
        """Returns the length of the object when converted to bytes."""
        return len(bytes(self))

    def __add__(self, other: bytes | SupportsBytes) -> bytes:
        """Concatenates the object with another bytes object."""
        return bytes(self) + bytes(other)

    def __radd__(self, other: bytes | SupportsBytes) -> bytes:
        """Concatenates the object with another bytes object."""
        return bytes(other) + bytes(self)


@dataclass(frozen=True)
class FP(BytesConcatenation):
    """Dataclass that defines a single element of Fp."""

    x: int = 0

    def __bytes__(self) -> bytes:
        """Converts the field element to bytes."""
        return self.x.to_bytes(64, byteorder="big")


@dataclass(frozen=True)
class PointG1(BytesConcatenation):
    """Dataclass that defines a single point in G1."""

    x: int = 0
    y: int = 0

    def __bytes__(self) -> bytes:
        """Converts the point to bytes."""
        return self.x.to_bytes(64, byteorder="big") + self.y.to_bytes(64, byteorder="big")

    def __neg__(self):
        """Negates the point."""
        return PointG1(self.x, Spec.P - self.y)


@dataclass(frozen=True)
class FP2(BytesConcatenation):
    """Dataclass that defines a single element of Fp2."""

    x: Tuple[int, int] = (0, 0)

    def __bytes__(self) -> bytes:
        """Converts the field element to bytes."""
        return self.x[0].to_bytes(64, byteorder="big") + self.x[1].to_bytes(64, byteorder="big")


@dataclass(frozen=True)
class PointG2(BytesConcatenation):
    """Dataclass that defines a single point in G2."""

    x: Tuple[int, int] = (0, 0)
    y: Tuple[int, int] = (0, 0)

    def __bytes__(self) -> bytes:
        """Converts the point to bytes."""
        return (
            self.x[0].to_bytes(64, byteorder="big")
            + self.x[1].to_bytes(64, byteorder="big")
            + self.y[0].to_bytes(64, byteorder="big")
            + self.y[1].to_bytes(64, byteorder="big")
        )

    def __neg__(self):
        """Negates the point."""
        return PointG2(self.x, (Spec.P - self.y[0], Spec.P - self.y[1]))


@dataclass(frozen=True)
class Scalar(BytesConcatenation):
    """Dataclass that defines a single scalar."""

    x: int = 0

    def __bytes__(self) -> bytes:
        """Converts the scalar to bytes."""
        return self.x.to_bytes(32, byteorder="big")


@dataclass(frozen=True)
class Spec:
    """
    Parameters from the EIP-2537 specifications as defined at
    https://eips.ethereum.org/EIPS/eip-2537
    """

    # Addresses
    G1ADD = 0x0B
    G1MUL = 0x0C
    G1MSM = 0x0D
    G2ADD = 0x0E
    G2MUL = 0x0F
    G2MSM = 0x10
    PAIRING = 0x11
    MAP_FP_TO_G1 = 0x12
    MAP_FP2_TO_G2 = 0x13

    # Gas constants
    G1ADD_GAS = 500
    G1MUL_GAS = 12_000
    G2ADD_GAS = 800
    G2MUL_GAS = 45_000
    MAP_FP_TO_G1_GAS = 5_500
    MAP_FP2_TO_G2_GAS = 75_000

    # Other constants
    B_COEFFICIENT = 0x04
    X = -0xD201000000010000
    Q = X**4 - X**2 + 1
    P = (X - 1) ** 2 * Q // 3 + X
    LEN_PER_PAIR = 384
    MSM_MULTIPLIER = 1_000
    MSM_DISCOUNT_TABLE = [
        0,
        1200,
        888,
        764,
        641,
        594,
        547,
        500,
        453,
        438,
        423,
        408,
        394,
        379,
        364,
        349,
        334,
        330,
        326,
        322,
        318,
        314,
        310,
        306,
        302,
        298,
        294,
        289,
        285,
        281,
        277,
        273,
        269,
        268,
        266,
        265,
        263,
        262,
        260,
        259,
        257,
        256,
        254,
        253,
        251,
        250,
        248,
        247,
        245,
        244,
        242,
        241,
        239,
        238,
        236,
        235,
        233,
        232,
        231,
        229,
        228,
        226,
        225,
        223,
        222,
        221,
        220,
        219,
        219,
        218,
        217,
        216,
        216,
        215,
        214,
        213,
        213,
        212,
        211,
        211,
        210,
        209,
        208,
        208,
        207,
        206,
        205,
        205,
        204,
        203,
        202,
        202,
        201,
        200,
        199,
        199,
        198,
        197,
        196,
        196,
        195,
        194,
        193,
        193,
        192,
        191,
        191,
        190,
        189,
        188,
        188,
        187,
        186,
        185,
        185,
        184,
        183,
        182,
        182,
        181,
        180,
        179,
        179,
        178,
        177,
        176,
        176,
        175,
        174,
    ]

    # Test constants (from https://github.com/ethereum/bls12-381-tests/tree/eip-2537)
    P1 = PointG1(  # random point in G1
        0x112B98340EEE2777CC3C14163DEA3EC97977AC3DC5C70DA32E6E87578F44912E902CCEF9EFE28D4A78B8999DFBCA9426,  # noqa: E501
        0x186B28D92356C4DFEC4B5201AD099DBDEDE3781F8998DDF929B4CD7756192185CA7B8F4EF7088F813270AC3D48868A21,  # noqa: E501
    )
    G1 = PointG1(
        0x17F1D3A73197D7942695638C4FA9AC0FC3688C4F9774B905A14E3A3F171BAC586C55E83FF97A1AEFFB3AF00ADB22C6BB,  # noqa: E501
        0x8B3F481E3AAA0F1A09E30ED741D8AE4FCF5E095D5D00AF600DB18CB2C04B3EDD03CC744A2888AE40CAA232946C5E7E1,  # noqa: E501
    )
    # point at infinity in G1
    INF_G1 = PointG1(0, 0)
    # random point in G2
    P2 = PointG2(
        (
            0x103121A2CEAAE586D240843A398967325F8EB5A93E8FEA99B62B9F88D8556C80DD726A4B30E84A36EEABAF3592937F27,  # noqa: E501
            0x86B990F3DA2AEAC0A36143B7D7C824428215140DB1BB859338764CB58458F081D92664F9053B50B3FBD2E4723121B68,  # noqa: E501
        ),
        (
            0xF9E7BA9A86A8F7624AA2B42DCC8772E1AF4AE115685E60ABC2C9B90242167ACEF3D0BE4050BF935EED7C3B6FC7BA77E,  # noqa: E501
            0xD22C3652D0DC6F0FC9316E14268477C2049EF772E852108D269D9C38DBA1D4802E8DAE479818184C08F9A569D878451,  # noqa: E501
        ),
    )
    G2 = PointG2(
        (
            0x24AA2B2F08F0A91260805272DC51051C6E47AD4FA403B02B4510B647AE3D1770BAC0326A805BBEFD48056C8C121BDB8,  # noqa: E501
            0x13E02B6052719F607DACD3A088274F65596BD0D09920B61AB5DA61BBDC7F5049334CF11213945D57E5AC7D055D042B7E,  # noqa: E501
        ),
        (
            0xCE5D527727D6E118CC9CDC6DA2E351AADFD9BAA8CBDD3A76D429A695160D12C923AC9CC3BACA289E193548608B82801,  # noqa: E501
            0x606C4A02EA734CC32ACD2B02BC28B99CB3E287E85A763AF267492AB572E99AB3F370D275CEC1DA1AAA9075FF05F79BE,  # noqa: E501
        ),
    )
    # point at infinity in G2
    INF_G2 = PointG2((0, 0), (0, 0))


def g1_multiplication_format(x: int, s: int) -> bytes:
    """
    Formats the input for the G1MUL precompile.
    """
    return x.to_bytes(128, byteorder="big") + s.to_bytes(32, byteorder="big")


def g1_multi_scalar_multiplication_format(*args: int) -> bytes:
    """
    Formats the input for the G1MSM precompile.
    """
    return b"".join(
        x.to_bytes(128 if i % 2 == 0 else 32, byteorder="big") for i, x in enumerate(args)
    )


def g2_addition_format(x: int, y: int) -> bytes:
    """
    Formats the input for the G2ADD precompile.
    """
    return x.to_bytes(256, byteorder="big") + y.to_bytes(256, byteorder="big")


def g2_multiplication_format(x: int, s: int) -> bytes:
    """
    Formats the input for the G2MUL precompile.
    """
    return x.to_bytes(256, byteorder="big") + s.to_bytes(32, byteorder="big")


def g2_multi_scalar_multiplication_format(*args: int) -> bytes:
    """
    Formats the input for the G2MSM precompile.
    """
    return b"".join(
        x.to_bytes(256 if i % 2 == 0 else 32, byteorder="big") for i, x in enumerate(args)
    )


def pairing_format(*args: int) -> bytes:
    """
    Formats the input for the PAIRING precompile.
    """
    return b"".join(
        x.to_bytes(128 if i % 2 == 0 else 256, byteorder="big") for i, x in enumerate(args)
    )


def map_fp_to_g1_format(x: int) -> bytes:
    """
    Formats the input for the MAP_FP_TO_G1 precompile.
    """
    return x.to_bytes(64, byteorder="big")


def map_fp2_to_g2_format(x: int) -> bytes:
    """
    Formats the input for the MAP_FP2_TO_G2 precompile.
    """
    return x.to_bytes(128, byteorder="big")


def msm_discount(k: int) -> int:
    """
    Returns the discount for the G1MSM and G2MSM precompiles.
    """
    return Spec.MSM_DISCOUNT_TABLE[min(k, 128)]


def msm_gas_func_gen(len_per_pair: int, multiplication_cost: int) -> Callable[[int], int]:
    """
    Generates a function that calculates the gas cost for the G1MSM and G2MSM
    precompiles.
    """

    def msm_gas(input_length: int) -> int:
        """
        Calculates the gas cost for the G1MSM and G2MSM precompiles.
        """
        k = input_length // len_per_pair
        if k == 0:
            return 0

        gas_cost = k * multiplication_cost * msm_discount(k) // Spec.MSM_MULTIPLIER

        return gas_cost

    return msm_gas


def pairing_gas(input_length: int) -> int:
    """
    Calculates the gas cost for the PAIRING precompile.
    """
    k = input_length // Spec.LEN_PER_PAIR
    return (23_000 * k) + 115_000


GAS_CALCULATION_FUNCTION_MAP = {
    Spec.G1ADD: lambda _: Spec.G1ADD_GAS,
    Spec.G1MUL: lambda _: Spec.G1MUL_GAS,
    Spec.G1MSM: msm_gas_func_gen(160, Spec.G1MUL_GAS),
    Spec.G2ADD: lambda _: Spec.G2ADD_GAS,
    Spec.G2MUL: lambda _: Spec.G2MUL_GAS,
    Spec.G2MSM: msm_gas_func_gen(288, Spec.G2MUL_GAS),
    Spec.PAIRING: pairing_gas,
    Spec.MAP_FP_TO_G1: lambda _: Spec.MAP_FP_TO_G1_GAS,
    Spec.MAP_FP2_TO_G2: lambda _: Spec.MAP_FP2_TO_G2_GAS,
}
