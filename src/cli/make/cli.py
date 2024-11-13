"""
CLI interface for generating blockchain test scripts.

It extracts a specified transaction and its required state from a blockchain network
using the transaction hash and generates a Python test script based on that information.
"""

import os

import jinja2

from cli.input import input_select, input_text

template_loader = jinja2.PackageLoader("cli.make")
template_env = jinja2.Environment(loader=template_loader, keep_trailing_newline=True)


def test():
    """
    Scaffold a test file from the command line interface (CLI).

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
    `tests/{fork}/{eip_number}_{eip_name}/test_{eip_name}.py`

    Example:
    If the user selects "State" as the test type, "Prague" as the fork,
    enters "1234" as the EIP number,
    and "Sample EIP" as the EIP name, the generated file will be:
    `tests/prague/1234_sample_eip/test_sample_eip.py`

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

    eip_number = input_text("Enter the EIP number")

    # TODO: Perhaps get the EIP name from the number using an API?
    eip_name = input_text("Enter the EIP name")

    file_name = f"test_{eip_name.lower().replace(' ', '_')}.py"

    directory_path = f"tests/{fork.lower()}/{eip_number}-{eip_name.lower().replace(' ', '_')}"
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

    print(f"Test file created at: {file_path}")
