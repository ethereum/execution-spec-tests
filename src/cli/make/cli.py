"""
The `make` CLI streamlines the process of scaffolding tasks, such as generating new test files,
enabling developers to concentrate on the core aspects of specification testing.


The module verifies the presence of a valid subcommand and calls the appropriate
function for the subcommand. If an invalid subcommand is present, it throws an error
and shows a list of valid subcommands. If no subcommand is present, it shows a list
of valid subcommands to choose from.
"""

import click

from cli.make.commands import test


@click.group()
def make():
    """
    The `make` CLI command helps you get started with new writing tests.
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
make.add_command(test)
