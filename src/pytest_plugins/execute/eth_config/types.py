"""Types used to test `eth_config`."""

from binascii import crc32
from pathlib import Path
from typing import Dict, Self, Set

import yaml
from pydantic import BaseModel, Field

from ethereum_test_base_types import Address, CamelModel, EthereumTestRootModel, ForkHash, Hash
from ethereum_test_forks import Fork
from ethereum_test_rpc import EthConfigResponse, ForkConfig, ForkConfigBlobSchedule


class AddressOverrideDict(EthereumTestRootModel):
    """
    Dictionary with overrides to the default addresses specified for each fork.
    Required for testnets or devnets which have a different location of precompiles or system
    contracts.
    """

    root: Dict[Address, Address]


class ForkConfigBuilder(BaseModel):
    """Class to describe a current or next fork + bpo configuration."""

    fork: Fork
    activation_time: int
    chain_id: int
    address_overrides: AddressOverrideDict
    blob_schedule: ForkConfigBlobSchedule | None = None

    def add(
        self, fork_or_blob_schedule: Fork | ForkConfigBlobSchedule, activation_time: int
    ) -> Self:
        """Add or change the base fork or blob schedule."""
        if isinstance(fork_or_blob_schedule, ForkConfigBlobSchedule):
            blob_schedule: ForkConfigBlobSchedule = fork_or_blob_schedule
            return self.__class__(
                fork=self.fork,
                activation_time=activation_time,
                chain_id=self.chain_id,
                address_overrides=self.address_overrides,
                blob_schedule=blob_schedule,
            )
        else:
            fork: Fork = fork_or_blob_schedule
            blob_schedule_or_none = (
                ForkConfigBlobSchedule(
                    **fork.blob_schedule()[fork.name()].model_dump(mode="python"),
                )
                if fork.blob_schedule() is not None and fork.name() in fork.blob_schedule()
                else self.blob_schedule
            )
            return self.__class__(
                fork=fork,
                activation_time=activation_time,
                chain_id=self.chain_id,
                address_overrides=self.address_overrides,
                blob_schedule=blob_schedule_or_none,
            )

    def get_config(self) -> ForkConfig:
        """
        Get the current and next fork configurations given the current time and the network
        configuration.
        """
        if self.blob_schedule is None:
            # Get from the fork
            forks_blob_schedules = self.fork.blob_schedule()
            fork_blob_schedule = forks_blob_schedules[self.fork.name()]
            if fork_blob_schedule is not None:
                blob_schedule = ForkConfigBlobSchedule(
                    **fork_blob_schedule.model_dump(mode="python"),
                )

        precompiles = {}
        for a in self.fork.precompiles():
            label = a.label
            if a in self.address_overrides.root:
                a = self.address_overrides.root[a]
            precompiles[a] = f"{label}"

        system_contracts = {}
        for a in self.fork.system_contracts():
            label = a.label
            if a in self.address_overrides.root:
                a = self.address_overrides.root[a]
            system_contracts[a] = f"{label}"

        return ForkConfig(
            activation_time=self.activation_time,
            blob_schedule=blob_schedule,
            chain_id=self.chain_id,
            precompiles=precompiles,
            system_contracts=system_contracts,
        )


def calculate_fork_id(genesis_hash: Hash, activation_times: Set[int]) -> ForkHash:
    """Calculate the fork Id given the genesis hash and each fork activation times."""
    buffer = bytes(genesis_hash)
    for activation_time in sorted(activation_times):
        buffer += activation_time.to_bytes(length=8, byteorder="big")
    return ForkHash(crc32(buffer))


class NetworkConfig(CamelModel):
    """Ethereum network config."""

    chain_id: int
    genesis_hash: Hash
    fork_activation_times: Dict[int, Fork]
    bpo_fork_activation_times: Dict[int, ForkConfigBlobSchedule] = {}
    address_overrides: AddressOverrideDict = Field(default_factory=lambda: AddressOverrideDict({}))

    def get_eth_config(self, current_time: int) -> EthConfigResponse:
        """Get the current and next forks based on the given time."""
        all_activations: Dict[int, Fork | ForkConfigBlobSchedule] = {
            **self.fork_activation_times,
            **self.bpo_fork_activation_times,
        }
        network_kwargs = {
            "chain_id": self.chain_id,
            "address_overrides": self.address_overrides,
        }
        current_config_builder: ForkConfigBuilder = ForkConfigBuilder(
            fork=all_activations[0],
            activation_time=0,
            **network_kwargs,
        )
        current_activation_times: Set[int] = set()
        next_config_builder: ForkConfigBuilder | None = None
        next_activation_times: Set[int] = set()

        for activation_time in all_activations.keys():
            if activation_time == 0:
                continue
            if activation_time <= current_time:
                current_config_builder = current_config_builder.add(
                    all_activations[activation_time], activation_time
                )
                current_activation_times.add(activation_time)
                next_activation_times.add(activation_time)
            else:
                next_config_builder = current_config_builder.add(
                    all_activations[activation_time], activation_time
                )
                next_activation_times.add(activation_time)
                break

        current_config = current_config_builder.get_config()
        kwargs = {
            "current": current_config,
            "currentHash": current_config.get_hash(),
            "currentForkId": calculate_fork_id(self.genesis_hash, current_activation_times),
        }
        if next_config_builder is not None:
            next_config = next_config_builder.get_config()
            kwargs["next"] = next_config
            kwargs["nextHash"] = next_config.get_hash()
            kwargs["nextForkId"] = calculate_fork_id(self.genesis_hash, next_activation_times)

        return EthConfigResponse(**kwargs)


class NetworkConfigFile(EthereumTestRootModel):
    """Root model to describe a file that contains network configurations."""

    root: Dict[str, NetworkConfig]

    @classmethod
    def from_yaml(cls, path: Path) -> Self:
        """Read the network configuration from a yaml file."""
        with path.open("r") as file:
            config_data = yaml.safe_load(file)
            return cls.model_validate(config_data)
