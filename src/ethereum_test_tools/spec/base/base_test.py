"""
Base test class and helper functions for Ethereum state and blockchain tests.
"""

import hashlib
import json
from abc import abstractmethod
from itertools import count
from os import path
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterator, List, Optional, TextIO

from pydantic import BaseModel, Field

from ethereum_test_forks import Fork
from evm_transition_tool import FixtureFormats, TransitionTool

from ...common import Account, Environment, Transaction, withdrawals_root
from ...common.conversions import to_hex
from ...common.json import to_json
from ...common.types import Alloc, Result, SerializationCamelModel
from ...reference_spec.reference_spec import ReferenceSpec


def verify_transactions(txs: List[Transaction] | None, result) -> List[int]:
    """
    Verify rejected transactions (if any) against the expected outcome.
    Raises exception on unexpected rejections or unexpected successful txs.
    """
    rejected_txs: Dict[int, Any] = {}
    if "rejected" in result:
        for rejected_tx in result["rejected"]:
            if "index" not in rejected_tx or "error" not in rejected_tx:
                raise Exception("badly formatted result")
            rejected_txs[rejected_tx["index"]] = rejected_tx["error"]

    if txs is not None:
        for i, tx in enumerate(txs):
            error = rejected_txs[i] if i in rejected_txs else None
            if tx.error and not error:
                raise Exception(f"tx expected to fail succeeded: pos={i}, nonce={tx.nonce}")
            elif not tx.error and error:
                raise Exception(f"tx unexpectedly failed: {error}")

            # TODO: Also we need a way to check we actually got the
            # correct error
    return list(rejected_txs.keys())


def verify_post_alloc(expected_post: Alloc, got_alloc: Alloc):
    """
    Verify that an allocation matches the expected post in the test.
    Raises exception on unexpected values.
    """
    for address, account in expected_post.root.items():
        if account is not None:
            if account == Account.NONEXISTENT:
                if address in got_alloc.root:
                    raise Exception(f"found unexpected account: {address}")
            else:
                if address in got_alloc.root:
                    got_account = got_alloc.root[address]
                    assert isinstance(got_account, Account)
                    assert isinstance(account, Account)
                    account.check_alloc(address, got_account)
                else:
                    raise Exception(f"expected account not found: {address}")


def verify_result(result: Result, env: Environment):
    """
    Verify that values in the t8n result match the expected values.
    Raises exception on unexpected values.
    """
    if env.withdrawals is not None:
        assert result.withdrawals_root == to_hex(withdrawals_root(env.withdrawals))


class BaseFixture(SerializationCamelModel):
    """
    Represents a base Ethereum test fixture of any type.
    """

    info: Dict[str, str] = Field(
        default_factory=dict,
        serialization_alias="_info",
    )

    _json: Optional[Dict[str, Any]] = None

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

        self._json = to_json(self)
        json_str = json.dumps(self._json, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
        self.info["hash"] = f"0x{h}"

    def to_json(self) -> Dict[str, Any]:
        """
        Convert to JSON.
        """
        assert self._json is not None, "Fixture not initialized"
        self._json["_info"] = self.info
        return self._json

    @classmethod
    @abstractmethod
    def format(cls) -> FixtureFormats:
        """
        Returns the fixture format which the evm tool can use to determine how to verify the
        fixture.
        """
        pass

    @classmethod
    @abstractmethod
    def collect_into_file(cls, fd: TextIO, fixtures: Dict[str, "BaseFixture"]):
        """
        Returns the name of the subdirectory where this type of fixture should be dumped to.
        """
        pass

    @classmethod
    @abstractmethod
    def output_base_dir_name(cls) -> Path:
        """
        Returns the name of the subdirectory where this type of fixture should be dumped to.
        """
        pass

    @classmethod
    def output_file_extension(cls) -> str:
        """
        Returns the file extension for this type of fixture.

        By default, fixtures are dumped as JSON files.
        """
        return ".json"


class BaseTest(BaseModel):
    """
    Represents a base Ethereum test which must return a single test fixture.
    """

    pre: Alloc
    tag: str = ""
    # Setting a default here is just for type checking, the correct value is automatically set
    # by pytest.
    fixture_format: FixtureFormats = FixtureFormats.UNSET_TEST_FORMAT

    # Transition tool specific fields
    _t8n_dump_dir: Optional[str] = ""
    _t8n_call_counter: Iterator[int] = count(0)

    @abstractmethod
    def generate(
        self,
        t8n: TransitionTool,
        fork: Fork,
        eips: Optional[List[int]] = None,
    ) -> BaseFixture:
        """
        Generate the list of test fixtures.
        """
        pass

    @classmethod
    @abstractmethod
    def pytest_parameter_name(cls) -> str:
        """
        Must return the name of the parameter used in pytest to select this
        spec type as filler for the test.
        """
        pass

    @classmethod
    @abstractmethod
    def fixture_formats(cls) -> List[FixtureFormats]:
        """
        Returns a list of fixture formats that can be output to the test spec.
        """
        pass

    def __post_init__(self) -> None:
        """
        Validate the fixture format.
        """
        if self.fixture_format not in self.fixture_formats():
            raise ValueError(
                f"Invalid fixture format {self.fixture_format} for {self.__class__.__name__}."
            )

    def get_next_transition_tool_output_path(self) -> str:
        """
        Returns the path to the next transition tool output file.
        """
        if not self._t8n_dump_dir:
            return ""
        return path.join(
            self._t8n_dump_dir,
            str(next(self._t8n_call_counter)),
        )


TestSpec = Callable[[Fork], Generator[BaseTest, None, None]]
