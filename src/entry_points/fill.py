"""
Define an entry point wrapper for pytest.
"""

import os
import sys

import pytest


def main():  # noqa: D103

    # Set FILL_CMD env to be added to fixture info section
    os.environ["FILL_CMD"] = " ".join([os.path.basename(sys.argv[0])] + sys.argv[1:])

    # Run pytest with relevant args
    pytest.main(sys.argv[1:])


if __name__ == "__main__":
    main()
