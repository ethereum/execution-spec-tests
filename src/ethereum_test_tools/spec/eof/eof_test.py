"""
Ethereum EOF test spec definition and filler.
"""

import warnings
from pathlib import Path
from shutil import which
from subprocess import CompletedProcess, run
from typing import Callable, ClassVar, Generator, List, Optional, Type

from ethereum_test_forks import Fork
from evm_transition_tool import FixtureFormats

from ...common.base_types import Bytes
from ...exceptions import EOFException, EvmoneExceptionParser
from ..base.base_test import BaseFixture, BaseTest
from .types import Fixture, Result


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
            raise FileNotFoundError(
                "`evmone-eofparse` binary executable not found/not executable."
            )
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
        try:
            eof_parse = EOFParse()
        except FileNotFoundError as e:
            warnings.warn(f"{e}, skipping EOF fixture verification. Fixtures may be invalid!")
            return fixture

        for _, vector in fixture.vectors.items():
            expected_result = vector.results.get(str(fork))
            if expected_result is None:
                raise Exception(f"EOF Fixture missing vector result for fork: {fork}")
            result = eof_parse.run(input=str(vector.code))
            self.verify_result(result, expected_result, vector.code)

        return fixture

    def verify_result(self, result: CompletedProcess, expected_result: Result, code: Bytes):
        """
        Checks that the actual reported exception string matches our expected error ENUM
        """
        parser = EvmoneExceptionParser()
        res_error = result.stdout.replace("\n", "")
        if expected_result.exception is None:
            if "OK" not in result.stdout:
                msg = "Expected eof code to be valid, but got an exception:"
                formatted_message = (
                    f"{msg} \n"
                    f"{code} \n"
                    f"Expected: No Exception \n"
                    f"     Got: {parser.rev_parse_exception(res_error)} ({res_error})"
                )
                raise Exception(formatted_message)
        else:
            if "OK" in res_error:
                expRes = expected_result.exception
                msg = "Expected eof code to be invalid, but got no exception from eof tool:"
                formatted_message = (
                    f"{msg} \n"
                    f"{code} \n"
                    f"Expected: {expRes} ({parser.parse_exception(expRes)}) \n"
                    f"     Got: No Exception"
                )
                raise Exception(formatted_message)
            else:
                expRes = expected_result.exception
                if expRes == parser.rev_parse_exception(res_error):
                    return

                msg = "EOF code expected to fail with a different exception, than reported:"
                formatted_message = (
                    f"{msg} \n"
                    f"{code} \n"
                    f"Expected: {expRes} ({parser.parse_exception(expRes)}) \n"
                    f"     Got: {parser.rev_parse_exception(res_error)} ({res_error})"
                )
                raise Exception(formatted_message)

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
