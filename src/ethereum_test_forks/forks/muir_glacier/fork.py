"""Muir Glacier fork definition."""

from ethereum_test_forks.forks.istanbul.fork import Istanbul


# Glacier forks skipped, unless explicitly specified.
class MuirGlacier(Istanbul, solc_name="istanbul", ignore=True):
    """Muir Glacier fork."""

    pass
