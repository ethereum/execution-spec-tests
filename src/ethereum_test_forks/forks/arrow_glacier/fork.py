"""Arrow Glacier fork definition."""

from ethereum_test_forks.forks.london import London


# Glacier forks skipped, unless explicitly specified.
class ArrowGlacier(London, solc_name="london", ignore=True):
    """Arrow Glacier fork."""

    pass
