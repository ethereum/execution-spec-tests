"""
Ethereum EOF test spec definition and filler.
"""

from pathlib import Path
from shutil import which
from subprocess import CompletedProcess, run
from typing import Callable, ClassVar, Generator, List, Optional, Type

from ethereum_test_forks import Fork
from evm_transition_tool import FixtureFormats

from ...common.base_types import Bytes
from ...exceptions import EOFException
from ..base.base_test import BaseFixture, BaseTest
from .types import Fixture


class EOFParse:
    """evmone-eofparse binary."""

    binary: Path

    def __new__(cls):
        """Make EOF binary a singleton."""
        if not hasattr(cls, "instance"):
            cls.instance = super(EOFParse, cls).__new__(cls)
        return cls.instance

    def __init__(
        self,
        binary: Optional[Path | str] = None,
    ):
        if binary is None:
            which_path = which("evmone-eofparse")
            if which_path is not None:
                binary = Path(which_path)
        if binary is None or not Path(binary).exists():
            raise Exception("""`evmone-eofparse` binary executable not found""")
        self.binary = Path(binary)

    def run(self, *args: str, input: str | None = None) -> CompletedProcess:
        """Run evmone with the given arguments"""
        return run(
            [self.binary, *args],
            capture_output=True,
            text=True,
            input=input,
        )


class EOFTest(BaseTest):
    """
    Filler type that tests EOF containers.
    """

    data: Bytes
    expect_exception: EOFException | None = None

    supported_fixture_formats: ClassVar[List[FixtureFormats]] = [
        # TODO: Potentially generate a state test and blockchain test too.
        FixtureFormats.EOF_TEST,
    ]

    def make_eof_test_fixture(
        self,
        *,
        fork: Fork,
        eips: Optional[List[int]],
    ) -> Fixture:
        """
        Generate the EOF test fixture.
        """
        fixture = Fixture(
            vectors={
                "0": {
                    "code": self.data,
                    "results": {
                        fork.blockchain_test_network_name(): {
                            "exception": self.expect_exception,
                            "valid": self.expect_exception is None,
                        }
                    },
                }
            }
        )
        eof_parse = EOFParse()
        result = eof_parse.run(input=fixture.model_dump_json(exclude_none=True))
        if result.returncode != 0:
            raise Exception(result.stderr)
        return fixture

    def generate(
        self,
        *,
        fork: Fork,
        eips: Optional[List[int]] = None,
        fixture_format: FixtureFormats,
        **_,
    ) -> BaseFixture:
        """
        Generate the BlockchainTest fixture.
        """
        if fixture_format == FixtureFormats.EOF_TEST:
            return self.make_eof_test_fixture(fork=fork, eips=eips)

        raise Exception(f"Unknown fixture format: {fixture_format}")


EOFTestSpec = Callable[[str], Generator[EOFTest, None, None]]
EOFTestFiller = Type[EOFTest]
