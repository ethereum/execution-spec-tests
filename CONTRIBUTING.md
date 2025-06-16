# Contributing

Contributions are welcome from anyone, regardless of whether you are just starting your Python journey, a web developer or a seasoned Execution Layer developer!

We appreciate your help and appreciate your contributions!

## Code of Conduct

All contributors are expected to be excellent to each other; other behavior is not tolerated.

## Communication

We encourage questions and discussions about the project. If you need help with the codebase or have questions about implementation details, please don't hesitate to reach out in the `#el-testing` channel in the [Ethereum R&D Discord Server](https://discord.com/invite/qGpsxSA).

For detailed information on how to get help, please see the [Getting Help](https://eest.ethereum.org/main/getting_started/getting_help) page in our documentation, which includes communication channels and contact information for project maintainers.

## Contributions We Welcome

As mentioned in the README's [Contributing section](https://github.com/ethereum/execution-spec-tests#contributing), we welcome earnest contributions that have reasonable substance or resolve existing repository issues.

## Contributions We Don't Accept

We do not accept:

- Contributions that only fix spelling or grammatical errors in documentation, code, or elsewhere.
- Drive-by or vibe code contributions without proper engagement or context.
- Pull requests from airdrop farmers.

I.e., pull requests should have reasonable substance and context.

## Reporting Bugs

We use GitHub Issues to track bugs. To report a bug, please follow these guidelines:

### Before Reporting

1. **Check existing issues**: Search [open issues](https://github.com/ethereum/execution-spec-tests/issues) to see if your problem has already been reported.
2. **Try to reproduce**: Confirm you can reproduce the issue consistently.
3. **Consider security implications**: For security vulnerabilities, please do NOT create a public issue (or PR). Instead, refer to our [Security Policy](SECURITY.md) for responsible disclosure guidelines.

### Creating a Bug Report

When creating a new issue:

1. **Use a clear, descriptive title** that identifies the problem, (see [Commit Messages, Issues and PR Titles](#commit-messages-issue-and-pr-titles)).
2. **Provide detailed reproduction steps**:
    - Include the exact commands you ran.
    - Share relevant console output.
    - Specify your environment (OS, Python version, if relevant, `uv` version from `uv --version`).
3. **Include relevant information and versions**:
    - Run `eest info` to get repo and tool versions and copy the information to the issue:

        ```console
        uv run eest info
        ```

    - Branch of execution-spec-tests you're using, if applicable.
    - For test failures, include the test case and failure details.
    - Screenshots if applicable.

## Pull Requests

We welcome contributions via pull requests! This section will guide you through the process.

### For First-Time Contributors

1. **Fork the repository** by clicking the "Fork" button on the top right of the [GitHub repository page](https://github.com/ethereum/execution-spec-tests).

2. **Clone your fork** to your local machine:

    ```bash
    git clone https://github.com/YOUR-USERNAME/execution-spec-tests.git
    cd execution-spec-tests
    ```

3. **Install `uv`**:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

4. **Set up your environment**:

    ```bash
    uv python install 3.12
    uv python pin 3.12
    uv sync --all-extras
    uv run solc-select use 0.8.24 --always-install
    ```

    See [installation troubleshooting](https://eest.ethereum.org/main/getting_started/installation_troubleshooting) if you encounter issues.

5. **Create a branch** for your changes:

    ```bash
    git checkout -b your-branch-name
    ```

6. **Make your changes** according to our [code standards](https://eest.ethereum.org/main/getting_started/code_standards).

7. **For EVM Tests**: Review the cases in the [EIP checklist template](./docs/writing_tests/checklist_templates/eip_testing_checklist_template.md).

8. **For Porting Tests**: If you're porting tests from ethereum/tests, see the [porting guide](https://eest.ethereum.org/main/dev/porting_legacy_tests) for coverage analysis and using `--skip-coverage-missed-reason` when needed.

9. **Verify your changes** by running the appropriate checks:

    ```bash
    uvx --with=tox-uv tox -e lint,typecheck
    ```

10. **Commit your changes** with meaningful commit messages (see [Commit Messages, Issues and PR Titles](#commit-messages-issue-and-pr-titles)).

11. **Push your branch** to your GitHub fork:

    ```bash
    git push -u origin your-branch-name
    ```

12. **Create a pull request** by navigating to your fork on GitHub and clicking the "New Pull Request" button.

### Branch Naming Conventions

Branch names should follow this format:

```text
<type>/<short-description>
```

Where `<type>` matches the [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/) types:

- `feat/` - For new features.
- `fix/` - For bug fixes.
- `docs/` - For documentation changes.
- `test/` - For adding or modifying tests.
- `refactor/` - For code refactoring.
- `chore/` - For maintenance tasks.

Examples:

```text
feat/add-cancun-blob-tests
fix/prague-consume-genesis
docs/improve-installation-guide
```

### PR Review Process

1. **Initial checks**: When you submit a PR, automated CI checks will run. Make sure all checks pass before requesting a review.

2. **Requesting review**: Feel free to tag a maintainer or ask for review in a PR comment.

3. **Review feedback**: Maintainers will review your code and may suggest changes. Please address all comments and engage in discussion if needed.

4. **Iteration**: Make requested changes, push to your branch, and the PR will update automatically. No need to create a new PR.

5. **Approval**: Once your changes are approved, a maintainer will merge your PR.

### PR Expectations

To increase the chances of your PR being merged quickly:

- **Scope**: Keep PRs focused on a _single issue or feature_.
- **CI checks**: Ensure all CI checks pass before requesting review; but do ask for help if you don't understand the fail!
- **Clean history**: Use meaningful, atomic commits that can be easily understood.
- **Tests**: Include tests for new functionality.
- **Documentation**: Update documentation for new features or changes.
- **Responsiveness**: Try to respond to review feedback within a reasonable time.

### Code Standards and Enforced CI Checks

We enforce lint, code formatting and unit test checks in our CI - for detailed code standards and enforcement checks, see our [Code Standards documentation](https://eest.ethereum.org/main/getting_started/code_standards).

### Commits

It's recommended to keep changes logically grouped into smaller, individual commits to make changes easier to review.

### Commit Messages, Issue and PR Titles

We use [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/) messages and PR titles following the format:

```console
<type>(<scope>): <description>
```

#### Rules

- The format should be lowercase except for object names, which should be back-ticked (e.g., `FixtureCollector`).
- The description should be clear and concise.
- No period at the end of the title/message.
- Use the imperative ("add" not "added" or "adds").
- A breaking change should be indicated by appending `!` directly after the type/scope.

#### Types

The following commit types are used in this repository:

| `<type>`       | Repo Label      | Description                                                  |
| -------------- | --------------- | ------------------------------------------------------------ |
| `feat`         | `type:feat`     | A new feature                                                |
| `bug` or `fix` | `type:bug`      | A bug/bug fix (`bug` in issue; `fix` in commit/PR)           |
| `docs`         | `type:docs`     | Documentation changes                                        |
| `style`        | -               | Formatting changes that don't affect code functionality      |
| `refactor`     | `type:refactor` | Code changes that neither fix bugs nor add features          |
| `test`         | `type:test`     | Add, refactor, modify an EEST library or framework unit test |
| `chore`        | `type:chore`    | Routine tasks, dependency updates, etc.                      |

#### Scopes

The following scopes are used in this repository:

| `<scope>` | Repo Label         | Description                                    |
| --------- | ------------------ | ---------------------------------------------- |
| `fill`    | `scope:fill`       | Changes to `fill` command                      |
| `execute` | `scope:execute`    | Changes to the `execute` command               |
| `consume` | `scope:consume`    | Changes to `consume` command suite             |
| `pytest`  | `scope:pytest`     | Changes that effect all EEST pytest plugins    |
| `evm`     | `scope:evm`        | Changes to the `evm_transition_tool` package   |
| `forks`   | `scope:forks`      | Changes to `ethereum_test_forks` package       |
| `tools`   | `scope:tools`      | Changes to `ethereum_test_tools` package       |
| `fw`      | `scope:fw`         | Framework changes (evm\|tools\|forks\|pytest)  |
| `tests`   | `scope:tests`      | Changes to EL client test cases in `./tests`   |
| `docs`    | `scope:docs`       | Documentation flow changes                     |
| `ci`      | `scope:ci`         | Continuous Integration changes                 |
| `gentest` | `scope:gentest`    | Changes to `gentest` CLI command               |
| `eest`    | `scope:eest`       | Changes to `eest` CLI command                  |
| `make`    | `scope:make`       | Changes to `eest make` command                 |
| `tooling` | `scope:tooling`    | Python tools changes (`uv`, `ruff`, `tox`,...) |
| `deps`    | `scope:deps`       | Updates package dependencies                   |

#### Examples

This repository's main focus are the EL client tests in `./tests/` (`scope:tests`), but it contains many unit/module tests (`type:tests`) for the test generation frameworks and libraries in this repository. This can be a bit confusing, these examples demonstrate how we apply these labels and terms:

```console
# adds new EVM tests to tests/prague/eip7702_set_code_tx/
feat(tests): add test cases for EIP-7702

# a pure EVM test code refactor; no changes to test fixture JSON (at least not to fixture hashes, IDs might change if it's too difficult to preserve them).
refactor(tests): split test setup across several fixtures

# improve EVM test docstrings (these are included in HTML documentation):
docs(tests): improve EIP-7623 docstrings

# fix an EVM test
fix(tests): EIP-7702 test authorization list nonce/gas

# add unit tests for the `execute` command
test(execute): add tests for output dir arguments

# fix a broken unit test
test(fill): fix broken unit test
```

Examples of messages and titles for other types and scopes:

```console
feat(eest): add new test generator command
fix(forks): resolve `Cancun` initialization issue
docs(fill): describe new command-line args
refactor(tools): improve code organization in bytecode helpers
test(pytest): add tests for logging plugin
chore(deps): update dependency versions
```

## Merging PRs

We maintain high standards for our repository history to ensure it's clean, understandable, and properly documented. Maintainers should follow these guidelines when merging PRs:

### Pre-Merge Checklist

1. **Review the PR template checklist**

    - Ensure all applicable items are checked.
    - Items that aren't relevant can be deleted or marked as N/A.

2. **Verify changelog entry**

    - Every PR that impacts functionality should have a changelog entry.
    - The entry should clearly but concisely describe the change.
    - It must include a link to the PR in brackets (e.g., `([#1234](https://github.com/ethereum/execution-spec-tests/pull/1234))`).
    - Add any breaking changes at the top of the upcoming release section.
    - Changelog entries are automatically validated in CI to ensure proper formatting.

3. **Check PR title format**

    - The PR title must follow the [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/) format: `<type>(<scope>): <description>`.
    - This title will be used (suggested automatically by Github) as the squash commit message, so it's essential it's correct.
    - Follow the same rules as commit messages (imperative tense, no period at end, etc.).
    - Example: `feat(tests): add tests for EIP-7702 blob gas calculation`

4. **Review PR description**:

    - Ensure the PR description is accurate and up-to-date.

5. **Add appropriate labels**:

    - Ensure the PR has the appropriate labels matching its type and scope.

6. **Consider other contributors/stakeholders**:

    - Verify the PR has been reviewed and approved by any interested contributors and/or stakeholders.

### Merge Strategy

We **strongly prefer squash merging** over other strategies.

Exceptions to the squash merge policy may include:

- Large PRs with logically separate commits that should be preserved.
- Work that spans multiple distinct features or fixes.

### Squash Commit Details

When performing a squash merge:

1. **Include PR number in the commit title**

    - Leave, respectively add, the PR number in parentheses at the end of the title.
    - Example: `feat(tests): add tests for EIP-7702 gas calculation (#1234)`

2. **Clean up the extended commit message**

    - Delete all content in the extended message section EXCEPT:

        - Any `Co-authored-by:` lines, which must be preserved to properly attribute work.
        - The format should be `Co-authored-by: Full Name <email@example.com>`
