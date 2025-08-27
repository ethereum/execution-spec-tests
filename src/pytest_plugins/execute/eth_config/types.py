"""Types used to test `eth_config`."""

from binascii import crc32
from collections import defaultdict
from pathlib import Path
from typing import Annotated, Any, ClassVar, Dict, List, Self, Set

import yaml
from pydantic import BaseModel, Field

from ethereum_test_base_types import (
    Address,
    CamelModel,
    EthereumTestRootModel,
    ForkHash,
    Hash,
    HexNumber,
)
from ethereum_test_forks import Fork
from ethereum_test_rpc import (
    EthConfigResponse,
    ForkConfig,
    ForkConfigBlobSchedule,
)


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

    @property
    def precompiles(self) -> Dict[str, Address]:
        """Get the precompiles."""
        precompiles = {}
        for a in self.fork.precompiles():
            label = a.label
            if a in self.address_overrides.root:
                a = self.address_overrides.root[a]
            precompiles[f"{label}"] = a
        return precompiles

    @property
    def system_contracts(self) -> Dict[str, Address]:
        """Get the system contracts."""
        system_contracts = {}
        for a in self.fork.system_contracts():
            label = a.label
            if a in self.address_overrides.root:
                a = self.address_overrides.root[a]
            system_contracts[f"{label}"] = a
        return system_contracts

    def get_config(self, fork_id: ForkHash) -> ForkConfig:
        """
        Get the current and next fork configurations given the current time and the network
        configuration.
        """
        return ForkConfig(
            activation_time=self.activation_time,
            blob_schedule=self.blob_schedule,
            chain_id=self.chain_id,
            fork_id=fork_id,
            precompiles=self.precompiles,
            system_contracts=self.system_contracts,
        )


def calculate_fork_id(genesis_hash: Hash, activation_times: Set[int]) -> ForkHash:
    """Calculate the fork Id given the genesis hash and each fork activation times."""
    buffer = bytes(genesis_hash)
    for activation_time in sorted(activation_times):
        if activation_time == 0:
            continue
        buffer += activation_time.to_bytes(length=8, byteorder="big")
    return ForkHash(crc32(buffer))


class ForkActivationTimes(EthereumTestRootModel[Dict[Fork, int]]):
    """Fork activation times."""

    root: Dict[Fork, int]

    def forks_by_activation_time(self) -> Dict[int, Set[Fork]]:
        """Get the forks by activation time."""
        forks_by_activation_time = defaultdict(set)
        for fork, activation_time in self.root.items():
            forks_by_activation_time[activation_time].add(fork)
        return forks_by_activation_time

    def active_forks(self, current_time: int) -> List[Fork]:
        """Get the active forks."""
        forks_by_activation_time = self.forks_by_activation_time()
        active_forks = []
        for activation_time in sorted(forks_by_activation_time.keys()):
            if activation_time <= current_time:
                active_forks.extend(sorted(forks_by_activation_time[activation_time]))
        return active_forks

    def next_forks(self, current_time: int) -> List[Fork]:
        """Get the next forks."""
        forks_by_activation_time = self.forks_by_activation_time()
        next_forks = []
        for activation_time in sorted(forks_by_activation_time.keys()):
            if activation_time > current_time:
                next_forks.extend(sorted(forks_by_activation_time[activation_time]))
        return next_forks

    def active_fork(self, current_time: int) -> Fork:
        """Get the active fork."""
        return self.active_forks(current_time)[-1]

    def next_fork(self, current_time: int) -> Fork | None:
        """Get the next fork."""
        next_forks = self.next_forks(current_time)
        if next_forks:
            return next_forks[0]
        return None

    def last_fork(self, current_time: int) -> Fork | None:
        """Get the last fork."""
        next_forks = self.next_forks(current_time)
        if next_forks:
            return next_forks[-1]
        return None

    def __getitem__(self, key: Fork) -> int:
        """Get the activation time for a given fork."""
        return self.root[key]


class NetworkConfig(CamelModel):
    """Ethereum network config."""

    chain_id: HexNumber
    genesis_hash: Hash
    fork_activation_times: ForkActivationTimes
    blob_schedule: Dict[Fork, ForkConfigBlobSchedule] = Field(default_factory=dict)
    address_overrides: AddressOverrideDict = Field(default_factory=lambda: AddressOverrideDict({}))

    def get_eth_config(self, current_time: int) -> EthConfigResponse:
        """Get the current and next forks based on the given time."""
        network_kwargs = {
            "chain_id": self.chain_id,
            "address_overrides": self.address_overrides,
        }

        activation_times = set(self.fork_activation_times.forks_by_activation_time().keys())

        current_activation_times = {
            activation_time
            for activation_time in activation_times
            if activation_time <= current_time
        }
        next_activation_times = {
            activation_time
            for activation_time in activation_times
            if activation_time > current_time
        }
        active_fork = self.fork_activation_times.active_fork(current_time)
        current_config_builder: ForkConfigBuilder = ForkConfigBuilder(
            fork=active_fork,
            activation_time=self.fork_activation_times[active_fork],
            blob_schedule=self.blob_schedule.get(active_fork),
            **network_kwargs,
        )
        current_config = current_config_builder.get_config(
            calculate_fork_id(self.genesis_hash, current_activation_times)
        )
        kwargs = {"current": current_config}

        next_fork = self.fork_activation_times.next_fork(current_time)
        if next_fork:
            next_config_builder: ForkConfigBuilder = ForkConfigBuilder(
                fork=next_fork,
                activation_time=self.fork_activation_times[next_fork],
                blob_schedule=self.blob_schedule.get(next_fork),
                **network_kwargs,
            )
            kwargs["next"] = next_config_builder.get_config(
                calculate_fork_id(
                    self.genesis_hash,
                    current_activation_times | {sorted(next_activation_times)[0]},
                )
            )

        last_fork = self.fork_activation_times.last_fork(current_time)
        if last_fork:
            last_config_builder: ForkConfigBuilder = ForkConfigBuilder(
                fork=last_fork,
                activation_time=self.fork_activation_times[last_fork],
                blob_schedule=self.blob_schedule.get(last_fork),
                **network_kwargs,
            )
            kwargs["last"] = last_config_builder.get_config(
                calculate_fork_id(
                    self.genesis_hash,
                    current_activation_times | next_activation_times,
                )
            )

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
