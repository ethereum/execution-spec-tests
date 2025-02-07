"""Gray Glacier fork definition."""

from ethereum_test_forks.forks.arrow_glacier.fork import ArrowGlacier


# Glacier forks skipped, unless explicitly specified.
class GrayGlacier(ArrowGlacier, solc_name="london", ignore=True):
    """Gray Glacier fork."""

    pass
