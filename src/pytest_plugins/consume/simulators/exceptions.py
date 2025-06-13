"""Pytest plugin that defines options and fixtures for client exceptions."""

import pprint
from typing import Dict, List, Tuple

import pytest
from hive.client import ClientType

from ethereum_clis.clis.besu import BesuExceptionMapper
from ethereum_clis.clis.erigon import ErigonExceptionMapper
from ethereum_clis.clis.ethereumjs import EthereumJSExceptionMapper
from ethereum_clis.clis.ethrex import EthrexExceptionMapper
from ethereum_clis.clis.geth import GethExceptionMapper
from ethereum_clis.clis.nethermind import NethermindExceptionMapper
from ethereum_clis.clis.nimbus import NimbusExceptionMapper
from ethereum_clis.clis.reth import RethExceptionMapper
from ethereum_test_exceptions import ExceptionMapper
from ethereum_test_fixtures import BlockchainFixtureCommon
from ethereum_test_fixtures.blockchain import FixtureHeader


class GenesisBlockMismatchExceptionError(Exception):
    """Definers a mismatch exception between the client and fixture genesis blockhash."""

    def __init__(self, *, expected_header: FixtureHeader, got_genesis_block: Dict[str, str]):
        """Initialize the exception with the expected and received genesis block headers."""
        message = (
            "Genesis block hash mismatch.\n\n"
            f"Expected: {expected_header.block_hash}\n"
            f"     Got: {got_genesis_block['hash']}."
        )
        differences, unexpected_fields = self.compare_models(
            expected_header, FixtureHeader(**got_genesis_block)
        )
        if differences:
            message += (
                "\n\nGenesis block header field differences:\n"
                f"{pprint.pformat(differences, indent=4)}"
            )
        elif unexpected_fields:
            message += (
                "\n\nUn-expected genesis block header fields from client:\n"
                f"{pprint.pformat(unexpected_fields, indent=4)}"
                "\nIs the fork configuration correct?"
            )
        else:
            message += (
                "There were no differences in the expected and received genesis block headers."
            )
        super().__init__(message)

    @staticmethod
    def compare_models(expected: FixtureHeader, got: FixtureHeader) -> Tuple[Dict, List]:
        """Compare two FixtureHeader model instances and return their differences."""
        differences = {}
        unexpected_fields = []
        for (exp_name, exp_value), (got_name, got_value) in zip(expected, got, strict=False):
            if "rlp" in exp_name or "fork" in exp_name:  # ignore rlp as not verbose enough
                continue
            if exp_value != got_value:
                differences[exp_name] = {
                    "expected     ": str(exp_value),
                    "got (via rpc)": str(got_value),
                }
            if got_value is None:
                unexpected_fields.append(got_name)
        return differences, unexpected_fields


EXCEPTION_MAPPERS: Dict[str, ExceptionMapper] = {
    "go-ethereum": GethExceptionMapper(),
    "nethermind": NethermindExceptionMapper(),
    "erigon": ErigonExceptionMapper(),
    "besu": BesuExceptionMapper(),
    "reth": RethExceptionMapper(),
    "nimbus": NimbusExceptionMapper(),
    "ethereumjs": EthereumJSExceptionMapper(),
    "ethrex": EthrexExceptionMapper(),
}


def pytest_addoption(parser):
    """Hive simulator specific consume command line options."""
    consume_group = parser.getgroup(
        "consume", "Arguments related to consuming fixtures via a client"
    )
    consume_group.addoption(
        "--disable-strict-exception-matching",
        action="store",
        dest="disable_strict_exception_matching",
        default="",
        help=(
            "Comma-separated list of client names and/or forks which should NOT use strict "
            "exception matching."
        ),
    )


@pytest.fixture(scope="session")
def client_exception_mapper_cache():
    """Cache for exception mappers by client type."""
    return {}


@pytest.fixture(scope="function")
def client_exception_mapper(
    client_type: ClientType, client_exception_mapper_cache
) -> ExceptionMapper | None:
    """Return the exception mapper for the client type, with caching."""
    if client_type.name not in client_exception_mapper_cache:
        for client in EXCEPTION_MAPPERS:
            if client in client_type.name:
                client_exception_mapper_cache[client_type.name] = EXCEPTION_MAPPERS[client]
                break
        else:
            client_exception_mapper_cache[client_type.name] = None

    return client_exception_mapper_cache[client_type.name]


@pytest.fixture(scope="session")
def disable_strict_exception_matching(request: pytest.FixtureRequest) -> List[str]:
    """Return the list of clients or forks that should NOT use strict exception matching."""
    config_string = request.config.getoption("disable_strict_exception_matching")
    return config_string.split(",") if config_string else []


@pytest.fixture(scope="function")
def client_strict_exception_matching(
    client_type: ClientType,
    disable_strict_exception_matching: List[str],
) -> bool:
    """Return True if the client type should use strict exception matching."""
    return not any(
        client.lower() in client_type.name.lower() for client in disable_strict_exception_matching
    )


@pytest.fixture(scope="function")
def fork_strict_exception_matching(
    fixture: BlockchainFixtureCommon,
    disable_strict_exception_matching: List[str],
) -> bool:
    """Return True if the fork should use strict exception matching."""
    # NOTE: `in` makes it easier for transition forks ("Prague" in "CancunToPragueAtTime15k")
    return not any(
        s.lower() in str(fixture.fork).lower() for s in disable_strict_exception_matching
    )


@pytest.fixture(scope="function")
def strict_exception_matching(
    client_strict_exception_matching: bool,
    fork_strict_exception_matching: bool,
) -> bool:
    """Return True if the test should use strict exception matching."""
    return client_strict_exception_matching and fork_strict_exception_matching