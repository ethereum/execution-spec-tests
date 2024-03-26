"""
Base test class and helper functions for Ethereum state and blockchain tests.
"""

import hashlib
import json
from abc import abstractmethod
from functools import reduce
from itertools import count
from os import path
from pathlib import Path
from typing import Any, Callable, ClassVar, Dict, Generator, Iterator, List, Optional, TextIO

from pydantic import BaseModel, Field

from ethereum_test_forks import Fork
from evm_transition_tool import FixtureFormats, TransitionTool

from ...common import Environment, Transaction, Withdrawal
from ...common.conversions import to_hex
from ...common.json import to_json
from ...common.types import CamelModel, Result
from ...reference_spec.reference_spec import ReferenceSpec


class HashMismatchException(Exception):
    """Exception raised when the expected and actual hashes don't match."""

    def __init__(self, expected_hash, actual_hash, message="Hashes do not match"):
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        self.message = message
        super().__init__(self.message)

    def __str__(self):  # noqa: D105
        return f"{self.message}: Expected {self.expected_hash}, got {self.actual_hash}"


def verify_transactions(txs: List[Transaction], result: Result) -> List[int]:
    """
    Verify rejected transactions (if any) against the expected outcome.
    Raises exception on unexpected rejections or unexpected successful txs.
    """
    rejected_txs: Dict[int, str] = {
        rejected_tx.index: rejected_tx.error for rejected_tx in result.rejected_transactions
    }

    for i, tx in enumerate(txs):
        error = rejected_txs[i] if i in rejected_txs else None
        if tx.error and not error:
            raise Exception(f"tx expected to fail succeeded: pos={i}, nonce={tx.nonce}")
        elif not tx.error and error:
            raise Exception(f"tx unexpectedly failed: {error}")

        # TODO: Also we need a way to check we actually got the
        # correct error
    return list(rejected_txs.keys())


def verify_result(result: Result, env: Environment):
    """
    Verify that values in the t8n result match the expected values.
    Raises exception on unexpected values.
    """
    if env.withdrawals is not None:
        assert result.withdrawals_root == to_hex(Withdrawal.list_root(env.withdrawals))


class BaseFixture(CamelModel):
    """
    Represents a base Ethereum test fixture of any type.
    """

    info: Dict[str, str] = Field(default_factory=dict, alias="_info")

    _json: Optional[Dict[str, Any]] = None

    format: ClassVar[FixtureFormats] = FixtureFormats.UNSET_TEST_FORMAT

    def fill_info(
        self,
        t8n: TransitionTool,
        ref_spec: ReferenceSpec | None,
    ):
        """
        Fill the info field for this fixture
        """
        if "comment" not in self.info:
            self.info["comment"] = "`execution-spec-tests` generated test"
        self.info["filling-transition-tool"] = t8n.version()
        if ref_spec is not None:
            ref_spec.write_info(self.info)

    def model_post_init(self, __context):
        """
        Post init hook to convert to JSON after instantiation.
        """
        super().model_post_init(__context)
        previous_hash = None
        if "hash" in self.info:  # e.g., we're loading an existing fixture from file
            previous_hash = self.info["hash"]
        self._json = to_json(self)
        self.add_hash()
        if previous_hash and previous_hash != self.info["hash"]:
            raise HashMismatchException(previous_hash, self.info["hash"])

    def to_json(self) -> Dict[str, Any]:
        """
        Convert to JSON.
        """
        assert self._json is not None, "Fixture not initialized"
        self._json["_info"] = self.info
        return self._json

    def add_hash(self) -> None:
        """
        Calculate the hash of the fixture and add it to the fixture and fixture's
        json.
        """
        assert self._json is not None, "Fixture not initialized"
        self._json["_info"] = {}
        json_str = json.dumps(self._json, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
        self.info["hash"] = f"0x{h}"
        self._json["_info"] = self.info

    @classmethod
    def collect_into_file(cls, fd: TextIO, fixtures: Dict[str, "BaseFixture"]):
        """
        For all formats, we simply join the json fixtures into a single file.
        """
        json_fixtures: Dict[str, Dict[str, Any]] = {}
        for name, fixture in fixtures.items():
            assert isinstance(fixture, cls), f"Invalid fixture type: {type(fixture)}"
            json_fixtures[name] = fixture.to_json()
        json.dump(json_fixtures, fd, indent=4)


class BaseTest(BaseModel):
    """
    Represents a base Ethereum test which must return a single test fixture.
    """

    tag: str = ""

    # Transition tool specific fields
    t8n_dump_dir: Path | None = Field(None, exclude=True)
    _t8n_call_counter: Iterator[int] = count(0)

    supported_fixture_formats: ClassVar[List[FixtureFormats]] = []

    @abstractmethod
    def generate(
        self,
        *,
        t8n: TransitionTool,
        fork: Fork,
        fixture_format: FixtureFormats,
        eips: Optional[List[int]] = None,
    ) -> BaseFixture:
        """
        Generate the list of test fixtures.
        """
        pass

    @classmethod
    def pytest_parameter_name(cls) -> str:
        """
        Must return the name of the parameter used in pytest to select this
        spec type as filler for the test.

        By default, it returns the underscore separated name of the class.
        """
        return reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, cls.__name__).lower()

    def get_next_transition_tool_output_path(self) -> str:
        """
        Returns the path to the next transition tool output file.
        """
        if not self.t8n_dump_dir:
            return ""
        return path.join(
            self.t8n_dump_dir,
            str(next(self._t8n_call_counter)),
        )


TestSpec = Callable[[Fork], Generator[BaseTest, None, None]]
