"""Muir Glacier fork definition."""

from ..istanbul.fork import Istanbul


# Glacier forks skipped, unless explicitly specified.
class MuirGlacier(Istanbul, solc_name="istanbul", ignore=True):
    """Muir Glacier fork."""

    pass
