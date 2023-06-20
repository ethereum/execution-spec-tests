"""
Automatically generate markdown documentation for all test modules
via mkdocstrings.
"""

import logging
import os
import re
import sys
import textwrap
from pathlib import Path
from string import Template

import mkdocs_gen_files

from ethereum_test_forks import get_development_forks

logger = logging.getLogger("mkdocs")

source_directory = "tests"
target_dir = Path("tests")
navigation_file = "navigation.md"


def get_script_relative_path():  # noqa: D103
    script_path = os.path.abspath(__file__)
    current_directory = os.getcwd()
    return os.path.relpath(script_path, current_directory)


"""
The following check that allows deactivation of the Test Case Reference
doc generation is no longer strictly necessary - it was a workaround for
a problem who's root cause has been solved. The code is left, however,
as it could still serve a purpose if we have many more test cases
and test doc gen becomes very time consuming.

If test doc gen is disabled, then it will not appear at all in the
output doc and all incoming links to it will generate a warning.
"""
if os.environ.get("CI") != "true":  # always generate in ci/cd
    enabled_env_var_name = "SPEC_TESTS_AUTO_GENERATE_FILES"
    script_name = get_script_relative_path()
    if os.environ.get(enabled_env_var_name) != "false":
        logger.info(f"{script_name}: generating 'Test Case Reference' doc")
        logger.info(
            f"{script_name}: set env var {enabled_env_var_name} to 'false' and re-run "
            "`mkdocs serve` or `mkdocs build` to  disable 'Test Case Reference' doc generation"
        )
    else:
        logger.warning(
            f"{script_name}: skipping automatic generation of 'Test Case Reference' doc"
        )
        logger.info(
            f"{script_name}: set env var {enabled_env_var_name} to 'true' and re-run"
            "`mkdocs serve` or `mkdocs build` to generate 'Test Case Reference' doc"
        )
        sys.exit(0)

DEV_FORKS = [fork.name() for fork in get_development_forks()]

GENERATE_FIXTURES_DEPLOYED = Template(
    textwrap.dedent(
        """
        !!! example "Generate fixtures for these test cases $additional_title with:"
            ```console
            fill -v $pytest_test_path
            ```

        """
    )
)

GENERATE_FIXTURES_DEVELOPMENT = Template(
    textwrap.dedent(
        """
        !!! example "Generate fixtures for these test cases for '$fork' with:"
            ```console
            fill -v $pytest_test_path --fork=$fork --evm-bin=/path/to/evm-tool-dev-version
            ```

        """
    )
)

# mkdocstrings filter doc:
# https://mkdocstrings.github.io/python/usage/configuration/members/#filters
MARKDOWN_TEMPLATE = Template(
    textwrap.dedent(
        """
        # $title

        $generate_fixtures_deployed
        $generate_fixtures_development
        ::: $package_name
            options:
                filters: ["^[tT]est*"]
        """
    )
)

#            options:
#              filters: ["!^_[^_]", "![A-Z]{2,}", "!pytestmark"]


def apply_name_filters(input_string: str):
    """
    Apply a list of regexes to names used in the nav section to clean
    up nav title names.
    """
    regexes = [
        # (r"^Test ", ""),
        (r"vm", "VM"),
        # TODO: enable standard formatting for all opcodes.
        (r"Dup", "DUP"),
        (r"Chainid", "CHAINID"),
        (r"acl", "ACL"),
        (r"eips", "EIPs"),
        (r"eip-?([1-9]{1,5})", r"EIP-\1"),
    ]

    for pattern, replacement in regexes:
        input_string = re.sub(pattern, replacement, input_string, flags=re.IGNORECASE)

    return input_string


def snake_to_capitalize(s):  # noqa: D103
    return " ".join(word.capitalize() for word in s.split("_"))


def copy_file(source_file, destination_file):
    """
    Copy a file by writing it's contents using mkdocs_gen_files.open()
    """
    with open(source_file, "r") as source:
        with mkdocs_gen_files.open(destination_file, "w") as destination:
            for line in source:
                destination.write(line)


# The nav section for test doc will get built here
nav = mkdocs_gen_files.Nav()

for root, _, files in sorted(os.walk(source_directory)):
    # sorted() is a bit of a hack to order nav content
    if "__pycache__" in root:
        continue

    markdown_files = [filename for filename in files if filename.endswith(".md")]
    python_files = [filename for filename in files if filename.endswith(".py")]

    test_dir_relative_path = Path(root).relative_to("tests")
    output_directory = target_dir / test_dir_relative_path

    # Process Markdown files first, then Python files for nav section ordering
    for file in markdown_files:
        source_file = Path(root) / file
        output_file_path = output_directory / file
        file_no_ext = os.path.splitext(file)[0]
        nav_path = "Test Case Reference" / test_dir_relative_path / file_no_ext
        copy_file(source_file, output_file_path)
        nav_tuple = tuple(snake_to_capitalize(part) for part in nav_path.parts)
        nav_tuple = tuple(apply_name_filters(part) for part in nav_tuple)
        nav[nav_tuple] = str(output_file_path)

    for file in sorted(python_files):
        output_file_path = Path("undefined")
        if file == "__init__.py":
            output_file_path = output_directory / "index.md"
            nav_path = "Test Case Reference" / test_dir_relative_path
            package_name = root.replace(os.sep, ".")
            pytest_test_path = root
        else:
            file_no_ext = os.path.splitext(file)[0]
            output_file_path = output_directory / f"{file_no_ext}.md"
            nav_path = "Test Case Reference" / test_dir_relative_path / file_no_ext
            package_name = os.path.join(root, file_no_ext).replace(os.sep, ".")
            pytest_test_path = os.path.join(root, file)

        nav_tuple = tuple(snake_to_capitalize(part) for part in nav_path.parts)
        nav_tuple = tuple(apply_name_filters(part) for part in nav_tuple)
        nav[nav_tuple] = str(output_file_path)
        markdown_title = nav_tuple[-1]

        if root == "tests":
            generate_fixtures_deployed = GENERATE_FIXTURES_DEPLOYED.substitute(
                pytest_test_path=pytest_test_path,
                additional_title=" for all forks deployed to mainnet",
            )
            generate_fixtures_development = GENERATE_FIXTURES_DEVELOPMENT.substitute(
                pytest_test_path=pytest_test_path, fork=DEV_FORKS[0]
            )
        elif dev_forks := [fork for fork in DEV_FORKS if fork.lower() in root.lower()]:
            assert len(dev_forks) == 1
            generate_fixtures_deployed = ""
            generate_fixtures_development = GENERATE_FIXTURES_DEVELOPMENT.substitute(
                pytest_test_path=pytest_test_path, fork=dev_forks[0]
            )
        else:
            generate_fixtures_deployed = GENERATE_FIXTURES_DEPLOYED.substitute(
                pytest_test_path=pytest_test_path, additional_title=""
            )
            generate_fixtures_development = ""

        with mkdocs_gen_files.open(output_file_path, "w") as f:
            f.write(
                MARKDOWN_TEMPLATE.substitute(
                    title=markdown_title,
                    package_name=package_name,
                    generate_fixtures_deployed=generate_fixtures_deployed,
                    generate_fixtures_development=generate_fixtures_development,
                )
            )
with mkdocs_gen_files.open(navigation_file, "a") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
