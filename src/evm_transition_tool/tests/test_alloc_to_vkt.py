"""
Test the verkle tree subcommand from the geth transition tool.
"""

import pytest

from evm_transition_tool import GethTransitionTool


# TODO: Update to use correct types.
@pytest.mark.parametrize(
    "post_alloc, expected_vkt",
    [
        (
            {
                "0x0000000000000000000000000000000000000100": {
                    "nonce": "0x01",
                    "balance": "0x01",
                    "code": "0x60203560003555",
                    "storage": {"0x0a": "0x0b"},
                },
            },
            {
                "0x31b64bbd0b09c1d09afea606bebb70bce80a2909189e513c924a0871bbd36300": "0x0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                "0x31b64bbd0b09c1d09afea606bebb70bce80a2909189e513c924a0871bbd36301": "0x0100000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                "0x31b64bbd0b09c1d09afea606bebb70bce80a2909189e513c924a0871bbd36302": "0x0100000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                "0x31b64bbd0b09c1d09afea606bebb70bce80a2909189e513c924a0871bbd36303": "0x159c5cfa7fab15702c72a4141ef31b26c42827bd74ffc5671d95033227e662e7",  # noqa: E501
                "0x31b64bbd0b09c1d09afea606bebb70bce80a2909189e513c924a0871bbd3634a": "0x000000000000000000000000000000000000000000000000000000000000000b",  # noqa: E501
            },
        ),
    ],
)
def test_post_alloc_to_vkt(post_alloc, expected_vkt):
    """
    Verifies that the `post_alloc_to_vkt` method of the `GethTransitionTool` class.
    """
    t8n = GethTransitionTool()
    result_vkt = t8n.post_alloc_to_vkt(post_alloc)

    assert set(result_vkt.keys()) == set(
        expected_vkt.keys()
    ), "Keys in created verkle tree do not match the expected keys."

    for key, expected_value in expected_vkt.items():
        assert key in result_vkt, f"Key {key} is missing in created verkle tree."
        assert result_vkt[key] == expected_value, (
            f"Value for {key} in the created verkle tree does not match expected. "
            f"Expected {expected_value}, got {result_vkt[key]}."
        )
