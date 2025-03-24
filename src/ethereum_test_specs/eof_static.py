"""Ethereum EOF static test spec parser."""

from typing import Annotated, Callable, ClassVar, Dict, List

import pytest
from pydantic import BeforeValidator, Field

from ethereum_test_base_types import CamelModel
from ethereum_test_exceptions.exceptions import EOFExceptionInstanceOrList
from ethereum_test_forks import Fork
from ethereum_test_types.eof.v1 import Container

from .base_static import BaseStaticTest, ForkRangeDescriptor, labeled_bytes_from_string
from .eof import EOFTestFiller


class Info(CamelModel):
    """Information about the test contained in the static file."""

    comment: str | None = None


def container_from_string(v: str) -> Container:
    """Parse a container string."""
    label, raw_bytes = labeled_bytes_from_string(v)
    return Container(
        name=label,
        raw_bytes=raw_bytes,
    )


class Vector(CamelModel):
    """Single vector contained in an EOF filler static test."""

    data: Annotated[Container, BeforeValidator(container_from_string)]
    expect_exception: Dict[ForkRangeDescriptor, EOFExceptionInstanceOrList] | None = None


class EOFStaticTest(BaseStaticTest):
    """EOF static filler from ethereum/tests."""

    info: Info = Field(..., alias="_info")

    forks: List[ForkRangeDescriptor]
    vectors: List[Vector]

    format_name: ClassVar[str] = "eof_test"

    def fill_function(self) -> Callable:
        """Return a EOF spec from a static file."""

        @pytest.mark.parametrize(
            "vector",
            self.vectors,
            ids=lambda c: c.data.name,
        )
        def test_eof_vectors(
            eof_test: EOFTestFiller,
            fork: Fork,
            vector: Vector,
        ):
            expect_exception: EOFExceptionInstanceOrList | None = None
            if vector.expect_exception is not None:
                for fork_range, exception in vector.expect_exception.items():
                    if fork_range.fork_in_range(fork):
                        expect_exception = exception
                        break
            return eof_test(
                container=vector.data,
                expect_exception=expect_exception,
            )

        return test_eof_vectors
