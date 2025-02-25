"""Definitions for configuration tests fixtures."""

import hashlib
import json
from functools import cached_property
from typing import ClassVar

from pydantic import computed_field

from ethereum_test_base_types import Hash
from ethereum_test_forks import ForkConfig

from .base import BaseFixture


class ConfigFixture(BaseFixture, ForkConfig):
    """Represents a configuration test fixture."""

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
