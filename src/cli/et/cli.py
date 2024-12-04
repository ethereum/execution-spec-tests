"""
`et` 👽 is a CLI tool that helps with routine tasks.
Invoke using `uv run et`.
"""

import click

from cli.et.commands import clean
from cli.et.make.cli import make


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def et():
    """
    `et` 👽 is a CLI tool that helps with routine tasks.
    """
    pass


"""
################################
||                            ||
||    Command Registration    ||
||                            ||
################################

Register nested commands here. For more information, see Click documentation:
https://click.palletsprojects.com/en/8.0.x/commands/#nested-handling-and-contexts
"""
et.add_command(make)
et.add_command(clean)

# Prevent wrapping behavior:
# See: https://click.palletsprojects.com/en/stable/documentation/#preventing-rewrapping
et(max_content_width=120)
