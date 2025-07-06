"""Types used to test `eth_config`."""

from typing import Dict, Tuple

from pydantic import BaseModel, Field

from ethereum_test_base_types import Address, EthereumTestRootModel
from ethereum_test_forks import Fork
from ethereum_test_rpc import ForkConfig, ForkConfigBlobSchedule


class AddressOverrideDict(EthereumTestRootModel):
    """
    Dictionary with overrides to the default addresses specified for each fork.
    Required for testnets or devnets which have a different location of precompiles or system
    contracts.
    """

    root: Dict[Address, Address]


class Config(BaseModel):
    """Class to describe a current or next fork + bpo configuration."""

    fork: Fork
    activation_time: int
    chain_id: int
    address_overrides: AddressOverrideDict
    blob_schedule: ForkConfigBlobSchedule | None = None

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
            system_contracts[f"{label}"] = a

        return ForkConfig(
            activation_time=self.activation_time,
            blob_schedule=blob_schedule,
            chain_id=self.chain_id,
            precompiles=precompiles,
            system_contracts=system_contracts,
        )


class NetworkConfig(BaseModel):
    """Ethereum network config."""

    chain_id: int
    fork_activation_times: Dict[Fork, int]
    blob_parameter_only_forks: Dict[int, ForkConfigBlobSchedule] = {}
    address_overrides: AddressOverrideDict = Field(default_factory=lambda: AddressOverrideDict({}))

    def get_current_next_forks(self, current_time: int) -> Tuple[ForkConfig, ForkConfig | None]:
        """Get the current and next forks based on the given time."""
        current_config: Config | None = None
        next_config: Config | None = None
        network_kwargs = {
            "chain_id": self.chain_id,
            "address_overrides": self.address_overrides,
        }
        for fork in reversed(self.fork_activation_times.keys()):
            fork_activation_time = self.fork_activation_times[fork]
            if fork_activation_time > current_time:
                next_config = Config(
                    fork=fork,
                    activation_time=fork_activation_time,
                    **network_kwargs,
                )
            else:
                current_config = Config(
                    fork=fork,
                    activation_time=fork_activation_time,
                    **network_kwargs,
                )
                break
        assert current_config is not None, f"Unable to determine current fork at {current_time}"
        for bpo_activation_time in reversed(self.blob_parameter_only_forks.keys()):
            blob_schedule = self.blob_parameter_only_forks[bpo_activation_time]
            if bpo_activation_time > current_time:
                # The BPO activates at some point in the future.
                if next_config is None:
                    # The BPO is activated in the future and there's no other fork planned.
                    # BPO is next.
                    next_config = Config(
                        fork=current_config.fork,
                        activation_time=bpo_activation_time,
                        **network_kwargs,
                        blob_schedule=blob_schedule,
                    )
                else:
                    # The BPO is acttivated in the future but there's already a fork (or other BPO)
                    # scheduled.
                    if bpo_activation_time > next_config.activation_time:
                        # The BPO happens after the next scheduled fork, next fork happens first
                        # so this BPO does not appear until next becomes current.
                        pass
                    elif bpo_activation_time == next_config.activation_time:
                        # The BPO happens at the same time as the next scheduled fork,
                        # so this blob configuration overrides the fork's one.
                        next_config = Config(
                            fork=next_config.fork,
                            activation_time=bpo_activation_time,
                            **network_kwargs,
                            blob_schedule=blob_schedule,
                        )
                    else:
                        # This BPO happens before the next fork, this BPO is next
                        next_config = Config(
                            fork=current_config.fork,
                            activation_time=bpo_activation_time,
                            **network_kwargs,
                            blob_schedule=blob_schedule,
                        )
            else:
                # The BPO is currently active
                if bpo_activation_time >= current_config.activation_time:
                    current_config.blob_schedule = blob_schedule
                else:
                    break

        return (
            current_config.get_config(),
            next_config.get_config() if next_config is not None else None,
        )
