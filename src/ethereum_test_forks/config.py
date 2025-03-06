"""Definition for the configuration of a client in a given fork."""

from ethereum_test_base_types import Address, CamelModel, ForkBlobSchedule


class ForkConfig(CamelModel):
    """Represents a configuration test fixture."""

    chain_id: int
    """
    ID of the network this config is for.
    """

    homestead_block: int | None = None
    dao_fork_block: int | None = None
    dao_fork_support: bool | None = None

    # EIP150 implements the Gas price changes (https://github.com/ethereum/EIPs/issues/150)
    eip_150_block: int | None = None
    eip_155_block: int | None = None
    eip_158_block: int | None = None

    byzantium_block: int | None = None
    constantinople_block: int | None = None
    petersburg_block: int | None = None
    istanbul_block: int | None = None
    muir_glacier_block: int | None = None
    berlin_block: int | None = None
    london_block: int | None = None
    arrow_glacier_block: int | None = None
    gray_glacier_block: int | None = None
    merge_netsplit_block: int | None = None

    # Fork scheduling was switched from blocks to timestamps here

    shanghai_time: int | None = None
    cancun_time: int | None = None
    prague_time: int | None = None
    osaka_time: int | None = None

    terminal_total_difficulty: int | None = None

    deposit_contract_address: Address | None = None

    blob_schedule: ForkBlobSchedule | None = None
