"""
Defines EIP-2537 specification constants and functions.
"""
from dataclasses import dataclass
from typing import Callable, SupportsBytes, Tuple

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


class BytesConcatenation(SupportsBytes):
    """
    A class that can be concatenated with bytes.
    """

    def __add__(self, other: bytes | SupportsBytes) -> bytes:
        """Concatenates the object with another bytes object."""
        return bytes(self) + bytes(other)

    def __radd__(self, other: bytes | SupportsBytes) -> bytes:
        """Concatenates the object with another bytes object."""
        return bytes(other) + bytes(self)


@dataclass(frozen=True)
class PointG1(BytesConcatenation):
    """Dataclass that defines a single point in G1."""

    x: int
    y: int

    def __bytes__(self) -> bytes:
        """Converts the point to bytes."""
        return self.x.to_bytes(64, byteorder="big") + self.y.to_bytes(64, byteorder="big")

    def __neg__(self):
        """Negates the point."""
        return PointG1(self.x, Spec.P - self.y)


@dataclass(frozen=True)
class PointG2(BytesConcatenation):
    """Dataclass that defines a single point in G2."""

    x: Tuple[int, int]
    y: Tuple[int, int]

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

    x: int

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
        2642749686785829596817345696055666872043783053155481581788492942917249902143862050648544313423577373440886627275814,  # noqa: E501
        3758365293065836235831663685357329573226673833426684174336991792633405517674721205716466791757730149346109800483361,  # noqa: E501
    )
    G1 = PointG1(
        3685416753713387016781088315183077757961620795782546409894578378688607592378376318836054947676345821548104185464507,  # noqa: E501
        1339506544944476473020471379941921221584933875938349620426543736416511423956333506472724655353366534992391756441569,  # noqa: E501
    )
    # point at infinity in G1
    INF_G1 = PointG1(0, 0)
    # random point in G2
    P2 = PointG2(
        (
            2492164500931426079025163640852824812322867633561487327988861767918782925114618691347698906331033143057488152854311,  # noqa: E501
            1296003438898513467811811427923539448251934100547963606575856033955925534446513985696904241181481649924224027073384,  # noqa: E501
        ),
        (
            2403995578136121235978187296860525416643018865432935587266433984437673369013628886898228883216954086902460896225150,  # noqa: E501
            2021783735792747140008634321371188179203707822883609206755922036803500907979420976539856007028648957203721805595729,  # noqa: E501
        ),
    )
    G2 = PointG2(
        (
            352701069587466618187139116011060144890029952792775240219908644239793785735715026873347600343865175952761926303160,  # noqa: E501
            3059144344244213709971259814753781636986470325476647558659373206291635324768958432433509563104347017837885763365758,  # noqa: E501
        ),
        (
            1985150602287291935568054521177171638300868978215655730859378665066344726373823718423869104263333984641494340347905,  # noqa: E501
            927553665492332455747201965776037880757740193453592970025027978793976877002675564980949289727957565575433344219582,  # noqa: E501
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
