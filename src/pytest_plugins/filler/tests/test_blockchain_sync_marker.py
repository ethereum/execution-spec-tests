"""Test blockchain sync fixture generation with verify_sync parameter."""

import textwrap

from ethereum_clis import TransitionTool

test_module_with_sync = textwrap.dedent(
    """\
    import pytest
    from ethereum_test_tools import (
        Account,
        BlockException,
        Block,
        Environment,
        Header,
        TestAddress,
        Transaction,
    )

    TEST_ADDRESS = Account(balance=1_000_000)

    @pytest.mark.valid_at("Cancun")
    def test_sync_default(blockchain_test):
        # verify_sync defaults to False
        blockchain_test(
            pre={TestAddress: TEST_ADDRESS},
            post={},
            blocks=[Block(txs=[Transaction()])]
        )

    @pytest.mark.valid_at("Cancun")
    def test_sync_true(blockchain_test):
        blockchain_test(
            verify_sync=True,
            pre={TestAddress: TEST_ADDRESS},
            post={},
            blocks=[Block(txs=[Transaction()])]
        )

    @pytest.mark.valid_at("Cancun")
    def test_sync_false(blockchain_test):
        blockchain_test(
            verify_sync=False,
            pre={TestAddress: TEST_ADDRESS},
            post={},
            blocks=[Block(txs=[Transaction()])]
        )

    @pytest.mark.valid_at("Cancun")
    @pytest.mark.parametrize("sync", [True, False])
    def test_sync_conditional(blockchain_test, sync):
        blockchain_test(
            pre={TestAddress: TEST_ADDRESS},
            post={},
            blocks=[Block(txs=[Transaction()])],
            verify_sync=sync
        )

    @pytest.mark.valid_at("Cancun")
    @pytest.mark.parametrize(
        "has_exception",
        [
            pytest.param(False, id="no_exception"),
            pytest.param(
                True, id="with_exception", marks=pytest.mark.exception_test
            ),
        ]
    )
    def test_sync_with_exception(blockchain_test, has_exception):
        blockchain_test(
            pre={TestAddress: TEST_ADDRESS},
            post={},
            blocks=[
                Block(
                    txs=[Transaction()],
                    rlp_modifier=Header(gas_limit=0) if has_exception else None,
                    exception=BlockException.INCORRECT_BLOCK_FORMAT if has_exception else None,
                )
            ],
            verify_sync=not has_exception,
        )

    """
)


def test_blockchain_sync_marker(
    pytester,
    default_t8n: TransitionTool,
):
    """
    Test blockchain sync fixture generation with exception_test marker.

    The test module has 5 test functions (7 test cases with parametrization):
    - test_sync_default: generates all formats except sync (verify_sync defaults to False)
    - test_sync_true: generates all formats including sync (verify_sync=True)
    - test_sync_false: generates all formats except sync (verify_sync=False)
    - test_sync_conditional: generates formats based on the sync parameter (2 cases)
    - test_sync_with_exception: tests exception_test marker behavior (2 cases)

    Each test generates fixture formats:
    - BlockchainFixture (always)
    - BlockchainEngineFixture (always)
    - BlockchainEngineSyncFixture (only when verify_sync=True AND not marked with exception_test)

    Expected outcomes:
    - 7 test cases total
    - Each generates BlockchainFixture (7) and BlockchainEngineFixture (7) = 14 fixtures
    - Sync fixtures:
        - test_sync_true: 1 sync fixture ✓
        - test_sync_conditional[True]: 1 sync fixture ✓
        - test_sync_with_exception[no_exception]: 1 sync fixture ✓
        - Total sync fixtures: 3
    - Skipped sync fixtures:
        - test_sync_default: 1 skipped
        - test_sync_false: 1 skipped
        - test_sync_conditional[False]: 1 skipped
        - Total skipped: 3
    - Not generated (due to exception_test marker):
        - test_sync_with_exception[with_exception]: sync fixture not generated at all

    Final counts:
    - Passed: 14 (base fixtures) + 3 (sync fixtures) = 17 passed
    - Skipped: 3 skipped
    - Failed: 0 failed
    """
    # Create proper directory structure for tests
    tests_dir = pytester.mkdir("tests")
    cancun_tests_dir = tests_dir / "cancun"
    cancun_tests_dir.mkdir()
    sync_test_dir = cancun_tests_dir / "sync_test_module"
    sync_test_dir.mkdir()
    test_module = sync_test_dir / "test_sync_marker.py"
    test_module.write_text(test_module_with_sync)

    pytester.copy_example(name="src/cli/pytest_commands/pytest_ini_files/pytest-fill.ini")

    # Add the test directory to the arguments
    args = [
        "-c",
        "pytest-fill.ini",
        "-v",
        "--no-html",
        "--t8n-server-url",
        default_t8n.server_url,
        "tests/cancun/sync_test_module/",
    ]

    expected_outcomes = {"passed": 17, "failed": 0, "skipped": 3, "errors": 0}

    result = pytester.runpytest(*args)
    result.assert_outcomes(**expected_outcomes)
