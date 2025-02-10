"""Arrow Glacier fork definition."""

from ..london.fork import London


# Glacier forks skipped, unless explicitly specified.
class ArrowGlacier(London, solc_name="london", ignore=True):
    """Arrow Glacier fork."""

    pass
