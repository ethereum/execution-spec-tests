"""Gray Glacier fork definition."""

from ..arrow_glacier.fork import ArrowGlacier


# Glacier forks skipped, unless explicitly specified.
class GrayGlacier(ArrowGlacier, solc_name="london", ignore=True):
    """Gray Glacier fork."""

    pass
