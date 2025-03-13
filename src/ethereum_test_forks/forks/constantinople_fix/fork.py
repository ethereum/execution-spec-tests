"""Constantinople Fix fork definition."""

from ..constantinople.fork import Constantinople


class ConstantinopleFix(Constantinople, solc_name="constantinople"):
    """Constantinople Fix fork."""

    pass
