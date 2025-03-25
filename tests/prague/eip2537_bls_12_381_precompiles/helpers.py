"""Helper functions for the EIP-2537 BLS12-381 precompiles tests."""

import os
import random
from typing import Annotated, Any, List, Optional

import pytest
from py_ecc.bls12_381 import FQ, FQ2, add, field_modulus, multiply
from pydantic import BaseModel, BeforeValidator, ConfigDict, RootModel, TypeAdapter
from pydantic.alias_generators import to_pascal

from .spec import PointG1, PointG2, Spec


def current_python_script_directory(*args: str) -> str:
    """Get the current Python script directory, optionally appending additional path components."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), *args)


class Vector(BaseModel):
    """Test vector for the BLS12-381 precompiles."""

    input: Annotated[bytes, BeforeValidator(bytes.fromhex)]
    expected: Annotated[bytes, BeforeValidator(bytes.fromhex)]
    gas: int
    name: str

    model_config = ConfigDict(alias_generator=to_pascal)

    def to_pytest_param(self):
        """Convert the test vector to a tuple that can be used as a parameter in a pytest test."""
        return pytest.param(self.input, self.expected, self.gas, id=self.name)


class FailVector(BaseModel):
    """Test vector for the BLS12-381 precompiles."""

    input: Annotated[bytes, BeforeValidator(bytes.fromhex)]
    expected_error: str
    name: str

    model_config = ConfigDict(alias_generator=to_pascal)

    def to_pytest_param(self):
        """Convert the test vector to a tuple that can be used as a parameter in a pytest test."""
        return pytest.param(self.input, id=self.name)


class VectorList(RootModel):
    """List of test vectors for the BLS12-381 precompiles."""

    root: List[Vector | FailVector]


VectorListAdapter = TypeAdapter(VectorList)


def vectors_from_file(filename: str) -> List:
    """Load test vectors from a file."""
    with open(
        current_python_script_directory(
            "vectors",
            filename,
        ),
        "rb",
    ) as f:
        return [v.to_pytest_param() for v in VectorListAdapter.validate_json(f.read()).root]


@staticmethod
def add_points_g1(point_a: PointG1, point_b: PointG1) -> PointG1:
    """
    Add two points in G1 using standard formulas.
    For points P = (x, y) and Q = (u, v), compute R = P + Q.
    """
    if point_a.x == 0 and point_a.y == 0:
        return point_b
    if point_b.x == 0 and point_b.y == 0:
        return point_a
    py_ecc_point_a = (FQ(point_a.x), FQ(point_a.y))
    py_ecc_point_b = (FQ(point_b.x), FQ(point_b.y))
    result = add(py_ecc_point_a, py_ecc_point_b)
    if result is None:
        return Spec.INF_G1
    return PointG1(int(result[0]), int(result[1]))


@staticmethod
def add_points_g2(point_a: PointG2, point_b: PointG2) -> PointG2:
    """
    Add two points in G2 using standard formulas.
    For points P = ((x_0, x_1), (y_0, y_1)) and Q = ((u_0, u_1), (v_0, v_1)), compute R = P + Q.
    """
    if point_a.x == (0, 0) and point_a.y == (0, 0):
        return point_b
    if point_b.x == (0, 0) and point_b.y == (0, 0):
        return point_a
    py_ecc_point_a = (FQ2(point_a.x), FQ2(point_a.y))
    py_ecc_point_b = (FQ2(point_b.x), FQ2(point_b.y))
    result = add(py_ecc_point_a, py_ecc_point_b)
    if result is None:
        return Spec.INF_G2
    new_x = (int(result[0].coeffs[0]), int(result[0].coeffs[1]))
    new_y = (int(result[1].coeffs[0]), int(result[1].coeffs[1]))
    return PointG2(new_x, new_y)


class BLSPointGenerator:
    """
    Generator for points on the BLS12-381 curve with various properties.

    Provides methods to generate points with specific properties:
        - on the standard curve
        - in the correct r-order subgroup or not
        - on the curve or not
        - on an isomorphic curve (not standard curve) but in the correct r-order subgroup

    Additional resource that helped the class implementation:
        https://hackmd.io/@benjaminion/bls12-381
    """

    # Base random seed for generating deterministic points within the random functions
    BASE_SEED = 0x5EEDED_BEEF

    # Constants for G1 curve equations
    # The b-coefficient in the elliptic curve equation y^2 = x^3 + b

    # Standard BLS12-381 G1 curve uses b=4
    # This is a known parameter of the BLS12-381 curve specification
    STANDARD_B_G1 = Spec.B_COEFFICIENT

    # Isomorphic G1 curve uses b=24 (can be any b value for an isomorphic curve)
    ISOMORPHIC_B_G1 = 24  # Isomorphic curve: y^2 = x^3 + 24

    # Constants for G2 curve equations
    # Standard BLS12-381 G2 curve uses b=(4,4)
    STANDARD_B_G2 = (Spec.B_COEFFICIENT, Spec.B_COEFFICIENT)

    # Isomorphic G2 curve uses b=(24,24)
    ISOMORPHIC_B_G2 = (24, 24)

    # Cofactors for G1 and G2
    # These are known constants for the BLS12-381 curve.

    # G1 cofactor h₁: (x-1)²/3 where x is the BLS parameter
    G1_COFACTOR = 0x396C8C005555E1568C00AAAB0000AAAB

    # G2 cofactor h₂: (x⁸ - 4x⁷ + 5x⁶ - 4x⁴ + 6x³ - 4x² - 4x + 13)/9
    G2_COFACTOR = 0x5D543A95414E7F1091D50792876A202CD91DE4547085ABAA68A205B2E5A7DDFA628F1CB4D9E82EF21537E293A6691AE1616EC6E786F0C70CF1C38E31C7238E5  # noqa: E501

    @staticmethod
    def is_on_curve_g1(x: int, y: int) -> bool:
        """Check if point (x,y) is on the BLS12-381 G1 curve."""
        x_fq = FQ(x)
        y_fq = FQ(y)
        return y_fq * y_fq == x_fq * x_fq * x_fq + FQ(Spec.B_COEFFICIENT)

    @staticmethod
    def is_on_curve_g2(x: tuple, y: tuple) -> bool:
        """Check if point (x,y) is on the BLS12-381 G2 curve."""
        x_fq2 = FQ2(x)
        y_fq2 = FQ2(y)
        return y_fq2 * y_fq2 == x_fq2 * x_fq2 * x_fq2 + FQ2(
            (Spec.B_COEFFICIENT, Spec.B_COEFFICIENT)
        )

    @staticmethod
    def check_in_g1_subgroup(point: PointG1) -> bool:
        """Check if a G1 point is in the correct r-order subgroup."""
        try:
            # Check q*P = O where q is the subgroup order
            x = FQ(point.x)
            y = FQ(point.y)
            result = multiply((x, y), Spec.Q)
            # If point is in the subgroup, q*P should be infinity
            return result is None
        except Exception:
            return False

    @staticmethod
    def check_in_g2_subgroup(point: PointG2) -> bool:
        """Check if a G2 point is in the correct r-order subgroup."""
        try:
            # Check q*P = O where q is the subgroup order
            x = FQ2(point.x)
            y = FQ2(point.y)
            result = multiply((x, y), Spec.Q)
            # If point is in the subgroup, q*P should be infinity
            return result is None
        except Exception:
            return False

    @staticmethod
    def sqrt_fq(a: FQ) -> Optional[FQ]:
        """
        Compute smallest square root of FQ element (if it exists). Used when finding valid
        y-coordinates for a given x-coordinate on the G1 curve.
        """
        assert field_modulus % 4 == 3, "This sqrt method requires p % 4 == 3"
        candidate = a ** ((field_modulus + 1) // 4)
        if candidate * candidate == a:
            if int(candidate) > field_modulus // 2:
                return -candidate
            return candidate
        return None

    @staticmethod
    def sqrt_fq2(a: FQ2) -> Optional[FQ2]:
        """
        Compute square root of FQ2 element (if it exists). Used when finding valid
        y-coordinates for a given x-coordinate on the G2 curve.
        """
        if a == FQ2([0, 0]):
            return FQ2([0, 0])
        candidate = a ** ((field_modulus**2 + 7) // 16)
        if candidate * candidate == a:
            int_c0, int_c1 = int(candidate.coeffs[0]), int(candidate.coeffs[1])
            if int_c1 > 0 or (int_c1 == 0 and int_c0 > field_modulus // 2):
                return -candidate
            return candidate
        return None

    @classmethod
    def multiply_by_cofactor(cls, point: Any, is_g2: bool = False):
        """
        Multiply a point by the cofactor to ensure it's in the correct r-order subgroup.
        Used for creating points in the correct r-order subgroup when using isomorphic curves.
        """
        cofactor = cls.G2_COFACTOR if is_g2 else cls.G1_COFACTOR
        try:
            if is_g2:
                # For G2, the point is given in this form: ((x0, x1), (y0, y1))
                x = FQ2([point[0][0], point[0][1]])
                y = FQ2([point[1][0], point[1][1]])
                base_point = (x, y)
                result = multiply(base_point, cofactor)
                return (
                    (int(result[0].coeffs[0]), int(result[0].coeffs[1])),
                    (int(result[1].coeffs[0]), int(result[1].coeffs[1])),
                )
            else:
                # For G1, the point is given as (x, y).
                x = FQ(point[0])
                y = FQ(point[1])
                base_point = (x, y)
                result = multiply(base_point, cofactor)
                return (int(result[0]), int(result[1]))
        except Exception as e:
            raise ValueError("Failed to multiply point by cofactor") from e

    @classmethod
    def find_g1_point_by_x(cls, x_value: int, in_subgroup: bool, on_curve: bool = True) -> PointG1:
        """
        Find a G1 point with x-coordinate at or near the given value,
        with the specified subgroup membership and curve membership.
        """
        max_offset = 5000
        isomorphic_b = cls.ISOMORPHIC_B_G1

        for offset in range(max_offset + 1):
            for direction in [1, -1]:
                if offset == 0 and direction == -1:
                    continue

                try_x = (x_value + direction * offset) % Spec.P

                try:
                    x = FQ(try_x)

                    # Calculate y² = x³ + b (standard curve or isomorphic curve)
                    b_value = cls.STANDARD_B_G1 if on_curve else isomorphic_b
                    y_squared = x**3 + FQ(b_value)

                    # Try to find y such that y² = x³ + b
                    y = cls.sqrt_fq(y_squared)
                    if y is None:
                        continue  # No valid y exists for this x

                    # Create the initial points on either curve
                    raw_point = (int(x), int(y))
                    raw_point2 = (int(x), Spec.P - int(y))

                    # For isomorphic curve points in subgroup, apply cofactor multiplication
                    if not on_curve and in_subgroup:
                        try:
                            subgroup_point = cls.multiply_by_cofactor(raw_point, is_g2=False)
                            point1 = PointG1(subgroup_point[0], subgroup_point[1])
                        except ValueError:
                            continue  # Skip if fails
                    else:
                        point1 = PointG1(int(x), int(y))
                    if not on_curve and in_subgroup:
                        try:
                            subgroup_point2 = cls.multiply_by_cofactor(raw_point2, is_g2=False)
                            point2 = PointG1(subgroup_point2[0], subgroup_point2[1])
                        except ValueError:
                            continue  # Skip if fails
                    else:
                        point2 = PointG1(int(x), Spec.P - int(y))

                    # Verify points have the required properties
                    point1_on_curve = cls.is_on_curve_g1(point1.x, point1.y)
                    point2_on_curve = cls.is_on_curve_g1(point2.x, point2.y)
                    point1_in_subgroup = cls.check_in_g1_subgroup(point1)
                    point2_in_subgroup = cls.check_in_g1_subgroup(point2)

                    # Return required point if found based on properties
                    if on_curve == point1_on_curve and in_subgroup == point1_in_subgroup:
                        return point1
                    if on_curve == point2_on_curve and in_subgroup == point2_in_subgroup:
                        return point2

                except Exception:
                    continue

        raise ValueError(
            (
                f"Failed to find G1 point by x={x_value},",
                "in_subgroup={in_subgroup},",
                "on_curve={on_curve}",
            )
        )

    @classmethod
    def find_g2_point_by_x(
        cls, x_value: tuple, in_subgroup: bool, on_curve: bool = True
    ) -> PointG2:
        """
        Find a G2 point with x-coordinate at or near the given value,
        with the specified subgroup membership and curve membership.
        """
        max_offset = 5000
        isomorphic_b = cls.ISOMORPHIC_B_G2

        for offset in range(max_offset + 1):
            for direction in [1, -1]:
                if offset == 0 and direction == -1:
                    continue

                try_x0 = (x_value[0] + direction * offset) % Spec.P
                try_x = (try_x0, x_value[1])  # Keep x1 the same

                try:
                    x = FQ2(try_x)

                    # Calculate y² = x³ + b (standard curve or isomorphic curve)
                    b_value = cls.STANDARD_B_G2 if on_curve else isomorphic_b
                    y_squared = x**3 + FQ2(b_value)

                    # Try to find y such that y² = x³ + b
                    y = cls.sqrt_fq2(y_squared)
                    if y is None:
                        continue  # No valid y exists for this x

                    # Create the initial points on either curve
                    raw_point = (
                        (int(x.coeffs[0]), int(x.coeffs[1])),
                        (int(y.coeffs[0]), int(y.coeffs[1])),
                    )
                    raw_point2 = (
                        (int(x.coeffs[0]), int(x.coeffs[1])),
                        (Spec.P - int(y.coeffs[0]), Spec.P - int(y.coeffs[1])),
                    )

                    # For isomorphic curve points in subgroup, apply cofactor multiplication
                    if not on_curve and in_subgroup:
                        try:
                            subgroup_point = cls.multiply_by_cofactor(raw_point, is_g2=True)
                            point1 = PointG2(subgroup_point[0], subgroup_point[1])
                        except ValueError:
                            continue  # Skip if fails
                    else:
                        point1 = PointG2(
                            (int(x.coeffs[0]), int(x.coeffs[1])),
                            (int(y.coeffs[0]), int(y.coeffs[1])),
                        )
                    if not on_curve and in_subgroup:
                        try:
                            subgroup_point2 = cls.multiply_by_cofactor(raw_point2, is_g2=True)
                            point2 = PointG2(subgroup_point2[0], subgroup_point2[1])
                        except ValueError:
                            continue  # Skip if fails
                    else:
                        point2 = PointG2(
                            (int(x.coeffs[0]), int(x.coeffs[1])),
                            (Spec.P - int(y.coeffs[0]), Spec.P - int(y.coeffs[1])),
                        )

                    # Verify points have the required properties
                    point1_on_curve = cls.is_on_curve_g2(point1.x, point1.y)
                    point2_on_curve = cls.is_on_curve_g2(point2.x, point2.y)
                    point1_in_subgroup = cls.check_in_g2_subgroup(point1)
                    point2_in_subgroup = cls.check_in_g2_subgroup(point2)

                    # Return required point if found based on properties
                    if on_curve == point1_on_curve and in_subgroup == point1_in_subgroup:
                        return point1
                    if on_curve == point2_on_curve and in_subgroup == point2_in_subgroup:
                        return point2

                except Exception:
                    continue

        raise ValueError(
            (
                f"Failed to find G2 point by x={x_value},",
                "in_subgroup={in_subgroup},",
                "on_curve={on_curve}",
            )
        )

    # G1 points by x coordinate (near or on the x value)
    @classmethod
    def generate_g1_point_in_subgroup_by_x(cls, x_value: int) -> PointG1:
        """G1 point that is in the r-order subgroup with x-coordinate by/on the given value."""
        return cls.find_g1_point_by_x(x_value, in_subgroup=True, on_curve=True)

    @classmethod
    def generate_g1_point_not_in_subgroup_by_x(cls, x_value: int) -> PointG1:
        """G1 point that is NOT in the r-order subgroup with x-coordinate by/on the given value."""
        return cls.find_g1_point_by_x(x_value, in_subgroup=False, on_curve=True)

    @classmethod
    def generate_g1_point_not_on_curve_by_x(cls, x_value: int) -> PointG1:
        """G1 point that is NOT on the curve with x-coordinate by/on the given value."""
        return cls.find_g1_point_by_x(x_value, in_subgroup=False, on_curve=False)

    @classmethod
    def generate_g1_point_on_isomorphic_curve_by_x(cls, x_value: int) -> PointG1:
        """
        G1 point that is on an isomorphic curve (not standard curve)
        but in the r-order subgroup with x-coordinate by/on the given value.

        Uses cofactor multiplication to ensure the point is in the correct subgroup.
        """
        return cls.find_g1_point_by_x(x_value, in_subgroup=True, on_curve=False)

    # G1 random points (deterministic based on seed)
    @classmethod
    def generate_random_g1_point_in_subgroup(cls) -> PointG1:
        """Generate a random G1 point that is in the r-order subgroup."""
        random.seed(cls.BASE_SEED)
        x = random.randrange(Spec.P)  # Random field element in Fp
        return cls.generate_g1_point_in_subgroup_by_x(x)

    @classmethod
    def generate_random_g1_point_not_in_subgroup(cls) -> PointG1:
        """Generate a random G1 point that is NOT in the r-order subgroup."""
        random.seed(cls.BASE_SEED + 1)  # Different seed for different point type
        x = random.randrange(Spec.P)
        return cls.generate_g1_point_not_in_subgroup_by_x(x)

    @classmethod
    def generate_random_g1_point_not_on_curve(cls) -> PointG1:
        """Generate a random G1 point that is NOT on the curve."""
        random.seed(cls.BASE_SEED + 2)
        x = random.randrange(Spec.P)
        return cls.generate_g1_point_not_on_curve_by_x(x)

    @classmethod
    def generate_random_g1_point_on_isomorphic_curve(cls) -> PointG1:
        """
        Generate a random G1 point that is on an isomorphic curve (not standard curve)
        but in the r-order subgroup.

        Uses cofactor multiplication to ensure the point is in the correct subgroup.
        """
        random.seed(cls.BASE_SEED + 3)
        x = random.randrange(Spec.P)
        return cls.generate_g1_point_on_isomorphic_curve_by_x(x)

    # G2 point generators - by x coordinate (near or on the x value)
    @classmethod
    def generate_g2_point_in_subgroup_by_x(cls, x_value: tuple) -> PointG2:
        """G2 point that is in the r-order subgroup with x-coordinate by/on the given value."""
        return cls.find_g2_point_by_x(x_value, in_subgroup=True, on_curve=True)

    @classmethod
    def generate_g2_point_not_in_subgroup_by_x(cls, x_value: tuple) -> PointG2:
        """G2 point that is NOT in the r-order subgroup with x-coordinate by/on the given value."""
        return cls.find_g2_point_by_x(x_value, in_subgroup=False, on_curve=True)

    @classmethod
    def generate_g2_point_not_on_curve_by_x(cls, x_value: tuple) -> PointG2:
        """G2 point that is NOT on the curve with x-coordinate by/on the given value."""
        return cls.find_g2_point_by_x(x_value, in_subgroup=False, on_curve=False)

    @classmethod
    def generate_g2_point_on_isomorphic_curve_by_x(cls, x_value: tuple) -> PointG2:
        """
        G2 point that is on an isomorphic curve (not standard curve)
        but in the r-order subgroup with x-coordinate near the given value.

        Uses cofactor multiplication to ensure the point is in the correct subgroup.
        """
        return cls.find_g2_point_by_x(x_value, in_subgroup=True, on_curve=False)

    # G2 random points (deterministic based on seed)
    @classmethod
    def generate_random_g2_point_in_subgroup(cls) -> PointG2:
        """Generate a random G2 point that is in the r-order subgroup."""
        random.seed(cls.BASE_SEED + 4)
        x0 = random.randrange(Spec.P)  # Real part of x-coordinate in Fp
        x1 = random.randrange(Spec.P)  # Imaginary part of x-coordinate in Fp
        return cls.generate_g2_point_in_subgroup_by_x((x0, x1))

    @classmethod
    def generate_random_g2_point_not_in_subgroup(cls) -> PointG2:
        """Generate a random G2 point that is NOT in the r-order subgroup."""
        random.seed(cls.BASE_SEED + 5)
        x0 = random.randrange(Spec.P)
        x1 = random.randrange(Spec.P)
        return cls.generate_g2_point_not_in_subgroup_by_x((x0, x1))

    @classmethod
    def generate_random_g2_point_not_on_curve(cls) -> PointG2:
        """Generate a random G2 point that is NOT on the curve."""
        random.seed(cls.BASE_SEED + 6)
        x0 = random.randrange(Spec.P)
        x1 = random.randrange(Spec.P)
        return cls.generate_g2_point_not_on_curve_by_x((x0, x1))

    @classmethod
    def generate_random_g2_point_on_isomorphic_curve(cls) -> PointG2:
        """
        Generate a random G2 point that is on an isomorphic curve (not standard curve)
        but in the r-order subgroup.

        Uses cofactor multiplication to ensure the point is in the correct subgroup.
        """
        random.seed(cls.BASE_SEED + 7)
        x0 = random.randrange(Spec.P)
        x1 = random.randrange(Spec.P)
        return cls.generate_g2_point_on_isomorphic_curve_by_x((x0, x1))
