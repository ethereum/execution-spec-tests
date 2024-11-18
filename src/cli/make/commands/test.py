"""
This module provides a CLI command to scaffold a test file.

The `test` command guides the user through a series of prompts to generate a test file
based on the selected test type, fork, EIP number, and EIP name. The generated test file
is saved in the appropriate directory with a rendered template using Jinja2.
"""

import os

import click
import jinja2

from cli.input import input_select, input_text

from .quotes import get_quote

template_loader = jinja2.PackageLoader("cli.make")
template_env = jinja2.Environment(loader=template_loader, keep_trailing_newline=True)


@click.command()
def test():
    """
    Create a new specification test file for an EIP.

    This function guides the user through a series of prompts to generate a test file
    for Ethereum execution specifications. The user is prompted to select the type of test,
    the fork to use, and to provide the EIP number and name. Based on the inputs, a test file
    is created in the appropriate directory with a rendered template.

    Prompts:
    - Choose the type of test to generate (State or Blockchain)
    - Select the fork to use (Prague or Osaka)
    - Enter the EIP number
    - Enter the EIP name

    The generated test file is saved in the following format:
    `tests/{fork}/eip{eip_number}_{eip_name}/test_{eip_name}.py`

    Example:
    If the user selects "State" as the test type, "Prague" as the fork,
    enters "1234" as the EIP number,
    and "Sample EIP" as the EIP name, the generated file will be:
    `tests/prague/eip1234_sample_eip/test_sample_eip.py`

    The function uses Jinja2 templates to render the content of the test file.

    Raises:
    - FileNotFoundError: If the template file does not exist.
    - IOError: If there is an error writing the file.
    """
    test_type = input_select(
        "Choose the type of test to generate", choices=["State", "Blockchain"]
    )
    # TODO: Get forks from a config called `UPCOMING_FORKS`
    fork = input_select("Select the fork to use", choices=["Prague", "Osaka"])

    eip_number = input_text("Enter the EIP number").strip()

    # TODO: Perhaps get the EIP name from the number using an API?
    eip_name = input_text("Enter the EIP name").strip()

    file_name = f"test_{eip_name.lower().replace(' ', '_')}.py"

    directory_path = f"tests/{fork.lower()}/eip{eip_number}_{eip_name.lower().replace(' ', '_')}"
    file_path = f"{directory_path}/{file_name}"

    # Create directories if they don't exist
    os.makedirs(directory_path, exist_ok=True)

    template = template_env.get_template(f"{test_type.lower()}_test.py.j2")
    rendered_template = template.render(
        fork=fork,
        eip_number=eip_number,
        eip_name=eip_name,
        test_name=eip_name.lower().replace(" ", "_"),
    )

    with open(file_path, "w") as file:
        file.write(rendered_template)

    print(f"\n 🎉 Success! Test file created at: {file_path}")
    print(get_quote())
