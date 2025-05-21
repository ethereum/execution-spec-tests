## 🗒️ Description
<!-- Brief description of the changes introduced by this PR -->

## 🔗 Related Issues
<!-- Reference any related issues using the GitHub issue number (e.g., Fixes #123) -->

## ✅ Checklist

- [ ] All: Set appropriate labels for the changes.
- [ ] All: Considered squashing commits to improve commit history.
- [ ] All: Added an entry to [CHANGELOG.md](/ethereum/execution-spec-tests/blob/main/docs/CHANGELOG.md).
- [ ] All: Considered updating the online docs in the [./docs/](/ethereum/execution-spec-tests/blob/main/docs/) directory.
- [ ] Tests: All converted JSON/YML tests from [ethereum/tests](/ethereum/tests)/[tests/static](/ethereum/execution-spec-tests/blob/main/tests/static) have been assigned @ported_from marker.
- [ ] Tests: A PR with removal of converted JSON/YML blockchain tests from [ethereum/tests](/ethereum/tests) have been opened.
- [ ] Tests: Included the type and version of evm t8n tool used to locally execute test cases:  e.g., ref with commit hash or geth 1.13.1-stable-3f40e65.
- [ ] Tests: Ran `mkdocs serve` locally and verified the auto-generated docs for new tests in the [Test Case Reference](https://eest.ethereum.org/main/tests/) are correctly formatted.
- [ ] Tests: For PRs implementing a missed test case, update the [post-mortem document](/ethereum/execution-spec-tests/blob/main/docs/writing_tests/post_mortems.md) to add an entry the list.
