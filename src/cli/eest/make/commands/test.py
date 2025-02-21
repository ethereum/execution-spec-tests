"""
Provides a CLI command to scaffold a test file.

The `test` command guides the user through a series of prompts to generate a test file
based on the selected test type, fork, EIP number, and EIP name. The generated test file
is saved in the appropriate directory with a rendered template using Jinja2.
"""

import os
import sys
from pathlib import Path

import click
import jinja2

from cli.input import input_select, input_text
from config.docs import DocsConfig
from ethereum_test_forks import get_development_forks, get_forks

template_loader = jinja2.PackageLoader("cli.eest.make")
template_env = jinja2.Environment(
    loader=template_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True
)


@click.command(
    short_help="Generate a new test file for an EIP.",
    epilog=f"Further help: {DocsConfig().DOCS_URL__WRITING_TESTS}",
)
def test():
    """Generate a new test file for an EIP."""
    test_type = input_select(
        "Choose the type of test to generate", choices=["State", "Blockchain"]
    )

    fork_choices = [str(fork) for fork in get_forks()]
    fork = input_select("Select the fork", choices=fork_choices)

    base_path = Path("tests") / fork.lower()
    existing_dirs = [d.name for d in base_path.iterdir() if d.is_dir()]

    location_choice = input_select(
        "Select test directory",
        choices=[
            {"name": "Use current location", "value": "current"},
            *existing_dirs,
            {"name": "Create new sub-directory", "value": "new"},
        ],
    )

    if location_choice == "new":
        eip_number = input_text("Enter the EIP number").strip()
        eip_name = input_text("Enter the EIP name").strip()
        test_name = eip_name.lower().replace(" ", "_")
        dir_name = f"eip{eip_number}_{test_name}"
        directory_path = base_path / dir_name
    elif location_choice == "current":
        eip_number = input_text("Enter the EIP number").strip()
        eip_name = input_text("Enter the EIP name").strip()
        test_name = input_text("Enter feature name (snake_case)").strip()
        directory_path = base_path
    else:
        dir_parts = location_choice.split("_")
        eip_number = dir_parts[0][3:]
        eip_name = " ".join(dir_parts[1:]).title()
        test_name = "_".join(dir_parts[1:])
        directory_path = base_path / location_choice

    file_name = f"test_{test_name}.py"

    if (directory_path / file_name).exists():
        click.echo(
            click.style(
                f"\n 🛑 The target test module {directory_path / file_name} already exists!",
                fg="red",
            ),
            err=True,
        )
        sys.exit(1)

    os.makedirs(directory_path, exist_ok=True)

    template = template_env.get_template(f"{test_type.lower()}_test.py.j2")
    rendered_template = template.render(
        fork=fork,
        eip_number=eip_number,
        eip_name=eip_name,
        test_name=test_name,
    )

    with open(directory_path / file_name, "w") as file:
        file.write(rendered_template)

    click.echo(
        click.style(
            f"\n 🎉 Success! Test file created at: {directory_path / file_name}",
            fg="green",
        )
    )

    fork_option = ""
    if fork in [dev_fork.name() for dev_fork in get_development_forks()]:
        fork_option = f" --until={fork}"

    click.echo(
        click.style(
            f"\n 📝 Get started with tests:  {DocsConfig().DOCS_URL__WRITING_TESTS}"
            f"\n ⛽ To fill this test, run: `uv run fill {directory_path / file_name}{fork_option}`",
            fg="cyan",
        )
    )
