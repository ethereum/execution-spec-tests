"""Constantinople Fix fork definition."""

from ethereum_test_forks.forks.constantinople.fork import Constantinople


class ConstantinopleFix(Constantinople, solc_name="constantinople"):
    """Constantinople Fix fork."""

    pass
