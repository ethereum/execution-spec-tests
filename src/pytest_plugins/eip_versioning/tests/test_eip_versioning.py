"""
Test cases for EIP versioning.
"""

# TODO: Test multiple eip_version_test markers with multiple EIPs and versions.
# TODO: Test warnings for EIPs not reported by client or spec.
# assert result.stdout.fnmatch_lines(["EIP not reported by client binary."])

import pytest


@pytest.mark.parametrize(
    "version_required, version_check_mode, test_is_pass, expected_outcome",
    [
        # check default behavior (mode=off), version checks should not change test outcome
        pytest.param("1.0.0", None, True, {"passed": 1}, id="off_major_version_too_low_pass"),
        pytest.param("1.0.0", None, False, {"failed": 1}, id="off_major_version_too_low_fail"),
        pytest.param("2.0.0", None, True, {"passed": 1}, id="off_major_version_same_pass"),
        pytest.param("2.0.0", None, False, {"failed": 1}, id="off_major_version_same_fail"),
        pytest.param("3.0.0", None, True, {"passed": 1}, id="off_major_version_too_high_pass"),
        pytest.param("3.0.0", None, False, {"failed": 1}, id="off_major_version_too_high_fail"),
        # check normal mode
        pytest.param("1.0.0", "normal", True, {"xpassed": 1}, id="major_version_too_low_pass1"),
        pytest.param("1.1.0", "normal", True, {"xpassed": 1}, id="major_version_too_low_pass2"),
        pytest.param("1.0.1", "normal", True, {"xpassed": 1}, id="major_version_too_low_pass3"),
        pytest.param("1.0.0", "normal", False, {"xfailed": 1}, id="major_version_too_low_fail1"),
        pytest.param("1.1.0", "normal", False, {"xfailed": 1}, id="major_version_too_low_fail2"),
        pytest.param("1.0.1", "normal", False, {"xfailed": 1}, id="major_version_too_low_fail3"),
        pytest.param("2.0.0", "normal", True, {"passed": 1}, id="major_version_same_pass1"),
        pytest.param("2.1.0", "normal", True, {"passed": 1}, id="major_version_same_pass2"),
        pytest.param("2.0.1", "normal", True, {"passed": 1}, id="major_version_same_pass3"),
        pytest.param("2.0.0", "normal", False, {"failed": 1}, id="major_version_same_fail1"),
        pytest.param("2.1.0", "normal", False, {"failed": 1}, id="major_version_same_fail2"),
        pytest.param("2.0.1", "normal", False, {"failed": 1}, id="major_version_same_fail3"),
        pytest.param("3.0.0", "normal", True, {"xpassed": 1}, id="major_version_too_high_pass1"),
        pytest.param("3.1.0", "normal", True, {"xpassed": 1}, id="major_version_too_high_pass2"),
        pytest.param("3.0.1", "normal", True, {"xpassed": 1}, id="major_version_too_high_pass3"),
        pytest.param("3.0.0", "normal", False, {"xfailed": 1}, id="major_version_too_high_fail1"),
        pytest.param("3.1.0", "normal", False, {"xfailed": 1}, id="major_version_too_high_fail2"),
        pytest.param("3.0.1", "normal", False, {"xfailed": 1}, id="major_version_too_high_fail3"),
        # check strict mode; if the major versions are different, the test must fail
        pytest.param(
            "1.0.0", "strict", True, {"failed": 1}, id="strict_major_version_too_low_pass"
        ),
        pytest.param(
            "1.0.0", "strict", False, {"failed": 1}, id="strict_major_version_too_low_fail"
        ),
        pytest.param("2.0.0", "strict", True, {"passed": 1}, id="strict_major_version_same_pass"),
        pytest.param("2.0.0", "strict", False, {"failed": 1}, id="strict_major_version_same_fail"),
        pytest.param(
            "3.0.0", "strict", True, {"failed": 1}, id="strict_major_version_too_high_pass"
        ),
        pytest.param(
            "3.0.0", "strict", False, {"failed": 1}, id="strict_major_version_too_high_fail"
        ),
    ],
)
def test_single_eip_version_test_marker(
    pytester, version_required, version_check_mode, test_is_pass, expected_outcome
):
    """
    Basic test for EIP versioning.
    """
    pytester.makepyfile(
        f"""
        import pytest

        @pytest.mark.eip_version_test("EIP-1559", "{version_required}")
        def test_example(state_test):
            assert {test_is_pass}
        """
    )
    pytester.copy_example(name="pytest.ini")
    pytester.copy_example(
        name="src/pytest_plugins/eip_versioning/tests/resources/eip_versions_spec.json"
    )
    pytester.copy_example(
        name="src/pytest_plugins/eip_versioning/tests/resources/eip_versions_client.json"
    )
    args = [
        "-vv",
        "-m state_test",  # single test: only generate a state test
        "--fork=Cancun",  # single test: only one fork
        "--eip-versions-spec=eip_versions_spec.json",
        "--eip-versions-client=eip_versions_client.json",
        "--no-html",
    ]
    if version_check_mode:
        args.append(f"--eip-version-mode={version_check_mode}")
    result = pytester.runpytest(*args)
    result.assert_outcomes(**expected_outcome)
