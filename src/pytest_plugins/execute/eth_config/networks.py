"""
Network configurations to test using `execute eth-config`.

Only post-merge forks are included in this file.
"""

from ethereum_test_forks import Cancun, Prague, Shanghai

from .types import NetworkConfig

NETWORK_CONFIGS = {
    "Mainnet": NetworkConfig(
        chain_id=1,
        fork_activation_times={
            Shanghai: 0,
            Cancun: 0,
        },
    ),
    "Hoodi": NetworkConfig(
        chain_id=0x88BB0,
        fork_activation_times={
            Cancun: 0,
            Prague: 1742999832,
        },
    ),
}
