"""Definitions for configuration tests fixtures."""

import hashlib
import json
from functools import cached_property
from typing import ClassVar

from pydantic import Field, computed_field

from ethereum_test_base_types import (
    Address,
    Alloc,
    Bloom,
    Bytes,
    CamelModel,
    EmptyOmmersRoot,
    Hash,
    Number,
)

from .base import BaseFixture
from .common import FixtureBlobSchedule


class ConfigFixture(BaseFixture):
    """Represents a configuration test fixture."""

    chain_id: Number
    """
    ID of the network this config is for.
    """

    homestead_block: Number | None = None
    dao_fork_block: Number | None = None
    dao_fork_support: bool | None = None

    # EIP150 implements the Gas price changes (https://github.com/ethereum/EIPs/issues/150)
    eip_150_block: Number | None = None
    eip_155_block: Number | None = None
    eip_158_block: Number | None = None

    byzantium_block: Number | None = None
    constantinople_block: Number | None = None
    petersburg_block: Number | None = None
    istanbul_block: Number | None = None
    muir_glacier_block: Number | None = None
    berlin_block: Number | None = None
    london_block: Number | None = None
    arrow_glacier_block: Number | None = None
    gray_glacier_block: Number | None = None
    merge_netsplit_block: Number | None = None

    # Fork scheduling was switched from blocks to timestamps here

    shanghai_time: Number | None = None
    cancun_time: Number | None = None
    prague_time: Number | None = None
    osaka_time: Number | None = None

    terminal_total_difficulty: Number | None = None

    deposit_contract_address: Address | None = None

    blob_schedule: FixtureBlobSchedule | None = None

    network_name: str
    """
    Name of the network the fixture is for:
    - mainnet
    - holesky
    - sepolia

    Must be excluded from the hash computation and it's for reference only.
    """
    fork: str
    """
    Fork of the network the fixture is for.

    Must be excluded from the hash computation and it's for reference only.
    """

    format_name: ClassVar[str] = "config_test"
    description: ClassVar[str] = "Tests that generate a config test fixture."

    @computed_field(alias="hash")  # type: ignore[misc]
    @cached_property
    def config_hash(self) -> Hash:
        """
        Compute the hash of the configuration.

        This hash must be used to validate the configuration for a given network.

        All fields are included in the hash computation except for the `hash` field itself,
        the `network_name` and the `fork`.

        The keys are sorted in lexicographic order before computing the hash.

        If a field's value is `null`, its key and value are excluded from the hash computation.

        The hash used is SHA-256.
        """
        json_obj = self.model_dump(mode="json", by_alias=True, exclude_none=True, exclude={"hash"})
        json_str = json.dumps(json_obj, sort_keys=True, separators=(",", ":"))
        return Hash(hashlib.sha256(json_str.encode("utf-8")).digest())

    def get_fork(self) -> str | None:
        """Return fork of the fixture as a string."""
        return self.fork
