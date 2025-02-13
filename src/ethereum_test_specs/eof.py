"""Ethereum EOF test spec definition and filler."""

import subprocess
import warnings
from pathlib import Path
from shutil import which
from subprocess import CompletedProcess
from typing import Callable, ClassVar, Dict, Generator, List, Optional, Sequence, Type

import pytest
from pydantic import Field

from ethereum_clis import EvmoneExceptionMapper, TransitionTool
from ethereum_test_base_types import Account, Bytes, HexNumber
from ethereum_test_exceptions.exceptions import EOFExceptionInstanceOrList, to_pipe_str
from ethereum_test_execution import (
    BaseExecute,
    ExecuteFormat,
    ExecuteFormatWithPytestID,
    TransactionPost,
)
from ethereum_test_fixtures import (
    BaseFixture,
    EOFFixture,
    FixtureFormat,
    FixtureFormatWithPytestID,
)
from ethereum_test_fixtures.eof import Result, Vector
from ethereum_test_forks import Fork
from ethereum_test_types import EOA, Alloc, Environment, Transaction
from ethereum_test_types.eof.v1 import Container, ContainerKind, Section
from ethereum_test_vm import Opcodes as Op

from .base import BaseTest
from .state import StateTest

existing_tests: Dict[Bytes, str] = {}


class EOFBaseExceptionError(Exception):
    """Base exception class for exceptions raised when verifying EOF code."""

    def __init__(self, message):
        """Initialize the exception with the message."""
        super().__init__(message)

    @staticmethod
    def format_code(code: Bytes, max_length=60) -> str:
        """Avoid printing long bytecode strings in the terminal upon test failure."""
        if len(code) > max_length:
            half_length = max_length // 2 - 5  # Floor; adjust for ellipsis
            return f"{code[:half_length].hex()}...{code[-half_length:].hex()}"
        return code.hex()


class UnexpectedEOFExceptionError(EOFBaseExceptionError):
    """
    Exception used when valid EOF code unexpectedly raises an exception in
    eofparse.
    """

    def __init__(self, *, code: Bytes, got: str):
        """Initialize the exception with the code and the exception message."""
        message = (
            "Expected EOF code to be valid, but an exception occurred:\n"
            f"    Code: {self.format_code(code)}\n"
            f"Expected: No Exception\n"
            f"     Got: {got}"
        )
        super().__init__(message)


class ExpectedEOFExceptionError(EOFBaseExceptionError):
    """
    Exception used when EOF code is expected to raise an exception, but
    eofparse did not raise an exception.
    """

    def __init__(self, *, code: Bytes, expected: str):
        """Initialize the exception with the code and the expected exception message."""
        message = (
            "Expected EOF code to be invalid, but no exception was raised:\n"
            f"    Code: {self.format_code(code)}\n"
            f"Expected: {expected}\n"
            f"     Got: No Exception"
        )
        super().__init__(message)


class EOFExceptionMismatchError(EOFBaseExceptionError):
    """Exception used when the actual EOF exception differs from the expected one."""

    def __init__(self, code: Bytes, expected: str, got: str):
        """Initialize the exception with the code, the expected/actual exception message."""
        message = (
            "EOF code raised a different exception than expected:\n"
            f"    Code: {self.format_code(code)}\n"
            f"Expected: {expected}\n"
            f"     Got: {got}"
        )
        super().__init__(message)


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
        """Initialize the EOF binary."""
        if binary is None:
            which_path = which("evmone-eofparse")
            if which_path is not None:
                binary = Path(which_path)
        if binary is None or not Path(binary).exists():
            raise FileNotFoundError(
                "`evmone-eofparse` binary executable not found/not executable."
            )
        self.binary = Path(binary)

    def run(self, *args: str, input_value: str | None = None) -> CompletedProcess:
        """Run evmone with the given arguments."""
        result = subprocess.run(
            [self.binary, *args],
            capture_output=True,
            text=True,
            input=input_value,
        )
        if result.returncode not in [0, 1]:
            raise Exception(
                f"`{self.binary.name}` call failed with return code {result.returncode}."
            )
        return result


class EOFTest(BaseTest):
    """Filler type that tests EOF containers."""

    container: Container
    expect_exception: EOFExceptionInstanceOrList | None = None
    container_kind: ContainerKind = ContainerKind.RUNTIME
    deployed_container: Container | None = None
    pre: Alloc | None = None
    post: Alloc | None = None
    sender: EOA | None = None

    supported_fixture_formats: ClassVar[Sequence[FixtureFormat | FixtureFormatWithPytestID]] = [
        EOFFixture
    ] + [
        FixtureFormatWithPytestID(
            fixture_format,
            f"{fixture_format.fixture_format_name}_from_eof_test",
        )
        for fixture_format in StateTest.supported_fixture_formats
    ]

    supported_execute_formats: ClassVar[Sequence[ExecuteFormat | ExecuteFormatWithPytestID]] = [
        ExecuteFormatWithPytestID(
            execute_format,
            f"{execute_format.execute_format_name}_from_eof_test",
        )
        for execute_format in StateTest.supported_execute_formats
    ]

    @classmethod
    def pytest_parameter_name(cls) -> str:
        """Workaround for pytest parameter name."""
        return "eof_test"

    def model_post_init(self, __context):
        """Prepare the test exception based on the container."""
        if self.container.validity_error is not None:
            if self.expect_exception is not None:
                assert self.expect_exception == self.container.validity_error, (
                    f"Container validity error {self.container.validity_error} "
                    f"does not match expected exception {self.expect_exception}."
                )
            self.expect_exception = self.container.validity_error
        if "kind" in self.container.model_fields_set or "container_kind" in self.model_fields_set:
            if (
                "kind" in self.container.model_fields_set
                and "container_kind" in self.model_fields_set
            ):
                assert self.container.kind == self.container_kind, (
                    f"Container kind type {str(self.container.kind)} "
                    f"does not match test {self.container_kind}."
                )
            elif "kind" in self.container.model_fields_set:
                self.container_kind = self.container.kind
            elif "container_kind" in self.model_fields_set:
                self.container.kind = self.container_kind

        assert self.pre is not None, "pre must be set to generate a StateTest."
        self.sender = self.pre.fund_eoa()
        if self.post is None:
            self.post = Alloc()

    def make_eof_test_fixture(
        self,
        *,
        request: pytest.FixtureRequest,
        fork: Fork,
        eips: Optional[List[int]],
    ) -> EOFFixture:
        """Generate the EOF test fixture."""
        container_bytes = Bytes(self.container)
        if container_bytes in existing_tests:
            pytest.fail(
                f"Duplicate EOF test: {container_bytes}, "
                f"existing test: {existing_tests[container_bytes]}"
            )
        existing_tests[container_bytes] = request.node.nodeid
        vectors = [
            Vector(
                code=container_bytes,
                container_kind=self.container_kind,
                results={
                    fork.blockchain_test_network_name(): Result(
                        exception=self.expect_exception,
                        valid=self.expect_exception is None,
                    ),
                },
            )
        ]
        fixture = EOFFixture(vectors=dict(enumerate(vectors)))
        try:
            eof_parse = EOFParse()
        except FileNotFoundError as e:
            warnings.warn(
                f"{e} Skipping EOF fixture verification. Fixtures may be invalid!", stacklevel=2
            )
            return fixture

        for _, vector in fixture.vectors.items():
            expected_result = vector.results.get(fork.blockchain_test_network_name())
            if expected_result is None:
                raise Exception(f"EOF Fixture missing vector result for fork: {fork}")
            args = []
            if vector.container_kind == ContainerKind.INITCODE:
                args.append("--initcode")
            result = eof_parse.run(*args, input_value=str(vector.code))
            self.verify_result(result, expected_result, vector.code)

        return fixture

    def verify_result(self, result: CompletedProcess, expected_result: Result, code: Bytes):
        """Check that the reported exception string matches the expected error."""
        parser = EvmoneExceptionMapper()
        actual_message = result.stdout.strip()
        actual_exception = parser.message_to_exception(actual_message)

        if expected_result.exception is None:
            if "OK" in actual_message:
                return
            else:
                raise UnexpectedEOFExceptionError(
                    code=code, got=f"{actual_exception} ({actual_message})"
                )
        else:
            expected_string = to_pipe_str(expected_result.exception)
            print(expected_string)
            print(actual_exception)
            if "OK" in actual_message:
                raise ExpectedEOFExceptionError(
                    code=code,
                    expected=f"{expected_string}",
                )
            elif actual_exception in expected_result.exception:
                return
            else:
                raise EOFExceptionMismatchError(
                    code=code,
                    expected=f"{expected_string}",
                    got=f"{actual_exception} ({actual_message})",
                )

    def generate_eof_contract_create_transaction(self) -> Transaction:
        """Generate a transaction that creates a contract."""
        assert self.sender is not None, "sender must be set to generate a StateTest."
        assert self.post is not None, "post must be set to generate a StateTest."

        initcode: Container
        deployed_container: Container | None
        if self.container_kind == ContainerKind.INITCODE:
            if "deployed_container" in self.model_fields_set:
                # In the case of an initcontainer where we know the deployed container,
                # we can use the initcontainer as-is.
                initcode = self.container
                deployed_container = self.deployed_container
            else:
                # The contract will be deployed as a EOF factory contract.
                deployed_container = Container(
                    sections=[
                        Section.Code(Op.EOFCREATE[0](0, 0, 0, 0) + Op.STOP),
                        Section.Container(self.container),
                    ]
                )
                initcode = Container(
                    sections=[
                        Section.Code(Op.RETURNCONTRACT[0](0, 0)),
                        Section.Container(deployed_container),
                    ]
                )
        else:
            initcode = Container(
                sections=[
                    Section.Code(Op.RETURNCONTRACT[0](0, 0)),
                    Section.Container(self.container),
                ]
            )
            deployed_container = self.container

        tx = Transaction(
            sender=self.sender,
            to=None,
            gas_limit=10_000_000,
            data=initcode,
        )

        if self.expect_exception is not None or deployed_container is None:
            self.post[tx.created_contract] = None
        else:
            self.post[tx.created_contract] = Account(
                code=deployed_container,
            )
        return tx

    def generate_state_test(self, fork: Fork) -> StateTest:
        """Generate the StateTest filler."""
        return StateTest(
            pre=self.pre,
            tx=self.generate_eof_contract_create_transaction(),
            env=Environment(),
            post=self.post,
            t8n_dump_dir=self.t8n_dump_dir,
        )

    def generate(
        self,
        *,
        request: pytest.FixtureRequest,
        t8n: TransitionTool,
        fork: Fork,
        eips: Optional[List[int]] = None,
        fixture_format: FixtureFormat,
        **_,
    ) -> BaseFixture:
        """Generate the BlockchainTest fixture."""
        if fixture_format == EOFFixture:
            return self.make_eof_test_fixture(request=request, fork=fork, eips=eips)
        elif fixture_format in StateTest.supported_fixture_formats:
            return self.generate_state_test(fork).generate(
                request=request, t8n=t8n, fork=fork, fixture_format=fixture_format, eips=eips
            )
        raise Exception(f"Unknown fixture format: {fixture_format}")

    def execute(
        self,
        *,
        fork: Fork,
        execute_format: ExecuteFormat,
        eips: Optional[List[int]] = None,
    ) -> BaseExecute:
        """Generate the list of test fixtures."""
        if execute_format == TransactionPost:
            return self.generate_state_test(fork).execute(
                fork=fork, execute_format=execute_format, eips=eips
            )
        raise Exception(f"Unsupported execute format: {execute_format}")


EOFTestSpec = Callable[[str], Generator[EOFTest, None, None]]
EOFTestFiller = Type[EOFTest]


class EOFTestOnly(EOFTest):
    """Filler type that tests EOF containers but does not generate a state/blockchain test."""

    supported_fixture_formats: ClassVar[Sequence[FixtureFormat | FixtureFormatWithPytestID]] = [
        EOFFixture
    ]

    @classmethod
    def pytest_parameter_name(cls) -> str:
        """Workaround for pytest parameter name."""
        return "eof_test_only"


class EOFStateTest(EOFTest, Transaction):
    """Filler type that tests EOF containers and also generates a state/blockchain test."""

    deploy_tx: bool = False
    gas_limit: HexNumber = Field(HexNumber(10_000_000), serialization_alias="gas")
    tx_sender_funding_amount: int = 1_000_000_000_000_000_000_000
    env: Environment = Field(default_factory=Environment)
    container_post: Account = Field(default_factory=Account)

    supported_fixture_formats: ClassVar[Sequence[FixtureFormat | FixtureFormatWithPytestID]] = [
        EOFFixture
    ] + list(StateTest.supported_fixture_formats)

    supported_execute_formats: ClassVar[Sequence[ExecuteFormat | ExecuteFormatWithPytestID]] = (
        StateTest.supported_execute_formats
    )

    @classmethod
    def pytest_parameter_name(cls) -> str:
        """Workaround for pytest parameter name."""
        return "eof_state_test"

    def model_post_init(self, __context):
        """Prepare the transaction parameters required to fill the test."""
        assert self.pre is not None, "pre must be set to generate a StateTest."

        EOFTest.model_post_init(self, __context)

        if "deploy_tx" not in self.model_fields_set:
            if self.container_kind == ContainerKind.INITCODE:
                self.deploy_tx = True

        self.sender = self.pre.fund_eoa(amount=self.tx_sender_funding_amount)
        if self.post is None:
            self.post = Alloc()

        if self.expect_exception is not None:  # Invalid EOF
            self.to = None  # Make EIP-7698 create transaction
            self.data = Bytes(
                bytes(self.container) + self.data
            )  # by concatenating container and tx data.

            # Run transaction model validation
            Transaction.model_post_init(self, __context)

            self.post[self.created_contract] = None  # Expect failure.
        elif self.deploy_tx:
            self.to = None  # Make EIP-7698 create transaction
            self.data = Bytes(
                bytes(self.container) + self.data
            )  # by concatenating container and tx data.

            # Run transaction model validation
            Transaction.model_post_init(self, __context)

            self.post[self.created_contract] = self.container_post  # Successful.
        else:
            self.to = self.pre.deploy_contract(code=self.container)

            # Run transaction model validation
            Transaction.model_post_init(self, __context)

            self.post[self.to] = self.container_post

    def generate_state_test(self, fork: Fork) -> StateTest:
        """Generate the StateTest filler."""
        assert self.pre is not None, "pre must be set to generate a StateTest."
        assert self.post is not None, "post must be set to generate a StateTest."

        return StateTest(
            pre=self.pre,
            tx=self,
            env=self.env,
            post=self.post,
            t8n_dump_dir=self.t8n_dump_dir,
        )

    def generate(
        self,
        *,
        request: pytest.FixtureRequest,
        t8n: TransitionTool,
        fork: Fork,
        eips: Optional[List[int]] = None,
        fixture_format: FixtureFormat,
        **_,
    ) -> BaseFixture:
        """Generate the BlockchainTest fixture."""
        if fixture_format == EOFFixture:
            if Bytes(self.container) in existing_tests:
                # Gracefully skip duplicate tests because one EOFStateTest can generate multiple
                # state fixtures with the same data.
                pytest.skip(f"Duplicate EOF container on EOFStateTest: {request.node.nodeid}")
            return self.make_eof_test_fixture(request=request, fork=fork, eips=eips)
        elif fixture_format in StateTest.supported_fixture_formats:
            return self.generate_state_test(fork).generate(
                request=request, t8n=t8n, fork=fork, fixture_format=fixture_format, eips=eips
            )

        raise Exception(f"Unknown fixture format: {fixture_format}")


EOFStateTestSpec = Callable[[str], Generator[EOFStateTest, None, None]]
EOFStateTestFiller = Type[EOFStateTest]
