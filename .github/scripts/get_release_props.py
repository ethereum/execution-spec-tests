# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml",
#     "click",
# ]
# ///

import sys

import click
import yaml

RELEASE_PROPS_FILE = './.github/configs/feature.yaml'


@click.command()
@click.argument('release', required=True)
def get_release_props(release):
    """Extracts a specific property from the YAML file for a given release."""
    with open(RELEASE_PROPS_FILE) as f:
        data = yaml.safe_load(f)
    if release not in data:
        print(f"Error: Release {release} not found in {RELEASE_PROPS_FILE}.")
        sys.exit(1)
    print("\n".join(f"{key}={value}" for key, value in data[release].items()))

if __name__ == "__main__":
    get_release_props()
