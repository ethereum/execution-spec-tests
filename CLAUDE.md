# CLAUDE.md - Ethereum Execution Spec Tests

> **CRITICAL**: This repository aims to provide world-class tooling for generating and working with JSON test vectors (aka test fixtures) that test Ethereum execution layer clients. Correctness of the tooling and tests is an absolute must. Additionally, ease-of-use and accessibility to the repository and its tools are a priority; it is important that we maintain a contributor-first mindset.

The contents of this file should be kept up-to-date with the following important repository resources:

- README.md.
- CONTRIBUTING.md.
- docs/getting_started/installation.md.
- docs/getting_started/code_standards.md.
- docs/getting_started/code_standards_details.md.

## ⚠️ Main repository contents and purpose

- `./tests/`: test cases for Ethereum execution-layer clients expressed as Python. These are used to **generate JSON test vectors (fixtures)** using the `fill` command and a reference EVM implementation. The resulting vectors can then be used to test Ethereum execution-layer clients. Generating the test cases is also known as "filling" the test cases. Filling alone is not actually testing; the vectors must be then executed against a client as this is differential test against a reference implementation.
- `./src/pytest_plugins/filler/`: Defines `fill` command behavior, which is implemented as a customization to pytest. This command generates the JSON test fixtures from the `./tests/` with the help of other framework libraries under `./src/`.
- `./src/cli/`: Defines commands/entry-points as `click`-based commands to generate (`fill`) and use (`consume`) the generated test vectors. It also contains other auxiliary tooling for tasks related to test fixtures and testing EL clients.
- `./src/ethereum_test_*`: Various helper libraries that provide the data structures and routines used to generate the JSON test fixtures. In particular, the data types and pydantic models used to serialize/deserialize their JSON.
- `./src/pytest_plugins/consume/`: Defines `consume` command, implemented as pytest plugins, that helps with the execution of test fixtures against client implementations either using a direct interfaces `./src/pytest_plugins/consume/direct/` (module tests) or as ethereum/hive simulators `./src/pytest_plugins/consume/hive_simulators/` (system test).
- `./src/pytest_plugins/execute`: Defines `execute` command behavior, implemented as pytest plugins, that helps run the Python test cases directly against a fully-instantiated client's JSON RPC endpoint.

### Clarification of Potentially Confusing Terminology

#### Two distinct types of tests exist

1. **Ethereum Client Tests** - Primary purpose: Python tests that generate JSON test vectors to verify Ethereum execution layer client consensus.
2. **Framework Unit Tests** - Secondary purpose: Unit tests that verify the testing framework itself works correctly.

#### Fixture Terminology (IMPORTANT - Two Different Meanings)

**"Fixtures" has two completely different meanings in this codebase:**

1. **Test Fixtures** (JSON files) - Historical term for the JSON test vectors that this framework generates. These are the actual inputs fed to Ethereum clients for consensus testing (via consume).

2. **Pytest Fixtures** - Standard pytest setup/teardown mechanisms used in both the Ethereum client tests and framework unit tests. Examples: `pre`, `state_test`, `blockchain_test`.

**Key Point**: When someone says "fixture" they could mean either JSON test vectors OR pytest fixtures. Context determines which.

### Core Framework Architecture

Fill/consume:

```text
Python Tests → Fill Command → JSON Test Fixtures → Consume → Client Verification
```

Execute:

```text
Python Tests → Execute Command → Client Verification via JSON RPC
```

## 🏗️ Core Components Overview

### `fill` - Test Vector Generator

- **Standalone CLI command** and **pytest-based tool**.
- Entry point: `uv run fill`, runnable independently.
- Composed of multiple pytest plugins, most notably `pytest_plugins.filler.filler`.
- **Generates fixtures** (JSON test vectors) based on Python test logic.
- Heavily uses **Pydantic** for serialization/deserialization of fixtures.
- **Example**: `uv run fill --fork=Cancun path/to/test_file.py --clean -v`.

### `consume` - Test Executor

- **Pytest-based command** that consumes previously generated test vectors.
- **Executes test vectors against clients** in two modes:
    1. **Direct client interface** (calling client APIs directly).
    2. **Hive simulators** (containerized test orchestration environments).
- **Example**: `uv run consume --client=geth fixtures/`.

### `execute` - Live JSON-RPC Testing

- **Pytest-based command** for real-world client testing.
- Executes tests **against running clients** via **JSON-RPC endpoints**.
- Useful for verifying client behavior in production-like configurations.
- **Example**: `uv run execute --endpoint=http://localhost:8545`.

### Auxiliary Tools & Plugins

- **Documentation generation**: `pytest_plugins.docgen.*` creates reference docs from test cases.
- **Mainnet test generation**: `gen-test` creates Python tests from transaction hashes on live networks.
- **Utility plugins**: Shared logic across commands for validation, reporting, and orchestration.

## 🚀 Quick Start Commands

All tools MUST be run using `uv run` prefix. Use `pre` fixture for dynamic addresses. Never hardcode addresses in new tests.

**Requirements**: Python 3.10, 3.11, 3.12, or 3.13 (recommended: 3.12) and `uv>=0.5.22`.

### Essential Setup (Use These First)

```bash
# Clone and setup (recommended: Python 3.12)
git clone https://github.com/ethereum/execution-spec-tests
cd execution-spec-tests
uv python install 3.12
uv python pin 3.12

# Install dependencies
uv sync --all-extras
uv run solc-select use 0.8.24 --always-install

# Install pre-commit hooks (strongly recommended)
uvx pre-commit install

# Run all checks (comprehensive validation)
uvx --with=tox-uv tox run-parallel
```

### Core Workflow Commands

```bash
# 1. Create new test
uv run eest make test

# 2. Generate JSON test fixtures from Python tests (PRIMARY WORKFLOW)
uv run fill --fork=Cancun path/to/test_file.py --clean -v

# 3. Execute fixtures against client (if you have one running)
uv run consume --client=geth fixtures/

# 4. OR execute against live JSON-RPC endpoint
uv run execute --endpoint=http://localhost:8545 path/to/test_file.py
```

### Claude Automation Commands

```bash
# Format documentation (check only)
uv run python .claude/commands/format_docs.py

# Format documentation (apply fixes)
uv run python .claude/commands/format_docs.py --fix

# Format specific files only
uv run python .claude/commands/format_docs.py --fix CLAUDE.md HUMANS.md
```

**Quick reference**: Use `/formatdocs` as shorthand when instructing Claude.

See `.claude/README.md` for complete command reference and adding new automation commands.

### Development & Quality Commands

```bash
# Test single function during development
uv run pytest -c pytest-framework.ini path/to/test_file.py::test_function

# Generate detailed EVM traces for debugging
uv run fill --fork=Cancun --evm-dump-dir=debug_output/ path/to/test_file.py

# Validate fixture integrity
uv run hasher --root fixtures/

# Fix all lint issues
uv run ruff check --fix

# Full testing suite
uvx --with=tox-uv tox run-parallel

# Build documentation locally (see Documentation section for details)
export FAST_DOCS=true && export GEN_TEST_DOC_VERSION="tox" && uv run mkdocs serve

# Generate test from mainnet transaction (reverse engineering)
uv run gen-test --tx-hash 0x123... --output tests/new_test.py
```

## 🎯 Core Framework Concepts

### Dynamic Address Allocation (`pre` Fixture)

**NEVER use hardcoded addresses in new tests.** Always use the `pre` fixture:

```python
def test_example(pre: Alloc, state_test: StateTestFiller):
    # Create funded EOA
    sender = pre.fund_eoa(10**18)  # 1 ETH
    
    # Deploy contracts (dependencies first)
    storage_contract = pre.deploy_contract(
        code=Op.SSTORE(1, 1),
        balance=7000000000000000000,
    )
    
    main_contract = pre.deploy_contract(
        code=Op.CALL(100000, storage_contract, 0, 0, 0, 0, 0) + Op.RETURN(0, 0),
        storage={0: 42},
    )
    
    # Execute transaction
    tx = Transaction(sender=sender, to=main_contract, gas_limit=5_000_000)
    state_test(pre=pre, tx=tx, post={main_contract: Account(storage={1: 1})})
```

**Key Methods:**

- `pre.deploy_contract(code, **kwargs) -> Address` - Deploy contract, get dynamic address.
- `pre.fund_eoa(amount=None, **kwargs) -> EOA` - Create funded account with private key.
- `pre.fund_address(address, amount)` - Add balance to existing address.

## 🔧 Complete Tool Reference

### Primary Pipeline Commands

- **`fill`** (`phil`) - Generate JSON test fixtures from Python tests using Pydantic serialization.
- **`consume`** (`protec`) - Execute generated fixtures against clients (direct API or Hive simulators).
- **`execute`** (`attac`) - Execute tests against live clients via JSON-RPC endpoints.
- **`eest`** - Main test creation and management tool.

### Development & Analysis Tools

- **`gen-test`** - Generate Python test from mainnet transaction hash (reverse engineering).
- **`hasher`** - Generate and verify fixture checksums for integrity validation.
- **`genindex`** - Generate fixtures index for test discovery and organization.
- **`checklist`** - Generate EIP testing coverage checklists for compliance tracking.
- **`groupstats`** - Show pre-allocation group performance statistics.
- **`order_fixtures`** - Ensure consistent fixture file ordering across environments.

### Specialized Utilities

- **`eofwrap`** - EOF (Ethereum Object Format) wrapper utilities for EOF testing.
- **`fillerconvert`** - Convert between different filler formats for compatibility.
- **`evm_bytes`** - EVM bytecode analysis utilities for debugging.
- **`check_eip_versions`** - Validate EIP version consistency across test suite.

### Build & Quality Commands

**All CI checks that must pass:**

```bash
# Full testing suite (all CI checks in parallel)
uvx --with=tox-uv tox run-parallel

# Individual CI environments
uvx --with=tox-uv tox -e lint           # Python lint, format and module import check (ruff)
uvx --with=tox-uv tox -e typecheck      # Type checking (mypy)
uvx --with=tox-uv tox -e pytest        # Framework unit tests
uvx --with=tox-uv tox -e tests-deployed # EL client test cases (deployed forks)
uvx --with=tox-uv tox -e mkdocs         # HTML documentation build
uvx --with=tox-uv tox -e spellcheck     # Code and documentation spell-check
uvx --with=tox-uv tox -e markdownlint   # Markdown linting
uvx --with=tox-uv tox -e changelog      # Changelog validation

# Fast quality fixes
uv run ruff check --fix                 # Fix lint issues automatically
uv run codespell *.md *.ini .github/ src/ tests/ docs/ --write-changes  # Fix spelling

# pytest commands are detailed in Project Architecture > Testing Configurations
```

## 📁 Project Architecture

### Directory Structure

```text
src/
├── ethereum_test_forks/     # Fork definitions (Cancun, Prague, etc.)
├── ethereum_test_tools/     # Core testing framework
├── ethereum_test_types/     # Type definitions 
├── ethereum_test_specs/     # EIP specifications
├── ethereum_test_vm/        # Virtual machine implementations
└── pytest_plugins/         # Extensive plugin system
    ├── filler/             # Test generation plugins
    ├── consume/            # Test execution plugins
    ├── logging/            # Enhanced logging system
    └── [others]/           # Specialized testing features

tests/                       # Test cases by fork
├── frontier/               # Frontier fork tests
├── cancun/                 # Cancun fork tests  
├── prague/                 # Prague fork tests
├── static/                 # Legacy static tests
└── [other-forks]/          # Additional Ethereum forks

docs/                       # Auto-generated documentation
fixtures/                   # Generated test fixtures
stubs/                      # Type stubs for dependencies
```

### Testing Configurations

Multiple pytest configurations for different contexts:

- `pytest.ini` - Main test configuration.
- `pytest-framework.ini` - Framework testing (use this for framework tests).
- `pytest-consume.ini` - Consumer testing.
- `pytest-execute.ini` - Execution testing.
- `pytest-execute-hive.ini` - Hive execution.
- `pytest-check-eip-versions.ini` - EIP validation.

**Common pytest usage patterns:**

```bash
# Framework tests (preferred for framework development)
uv run pytest -c pytest-framework.ini -xvs path/to/test

# Parallel execution for test suites
pytest -c ./pytest-framework.ini -n auto -m "not run_in_serial"

# Test specific function
uv run pytest -c pytest-framework.ini path/to/test_file.py::test_function

# Clean fixture regeneration
uv run fill --fork=<fork> <test_file> --clean -v
```

## 📝 Code Standards

### Formatting & Style

- **Line length**: 100 characters (enforced by ruff).
- **Import style**:
    - Explicit imports only, no `import *`.
    - All imports must be at the top of the file - no local imports within function bodies.
    - Use relative imports within the same package.
    - Properly organize imports (automatically with ruff or VS Code settings).
- **Naming conventions**:
    - `snake_case` for variables, functions, modules.
    - `PascalCase` for classes.
    - `UPPER_CASE` for constants.
- **Type annotations**: Required for all functions.
- **Path handling**: Use `pathlib` over `os.path`.

### Code Quality Rules

- **Error handling**: Use explicit exception types and meaningful messages.
- **Documentation**: Docstrings required for classes and functions.
- **Comments**: Only when necessary - avoid restating obvious code.
- **Testing**: Write tests for all new functionality using pytest features.

### Anti-Patterns to Avoid

- ❌ **Hardcoded addresses** (use `pre` fixture).
- ❌ **`TestAddress` in new tests** (use `pre.fund_eoa()`).
- ❌ **Manual nonce management** (let framework handle it).
- ❌ **Missing type annotations**.
- ❌ **Missing `sender` parameter** in transactions.
- ❌ **Ignoring fork compatibility** (use `@pytest.mark.valid_from()`).

## 🐍 Code Quality and Python Style

### Python Style Requirements

Python code in this repository should be **idiomatic**, **clear**, and **easy to read**.

- Code should **not be overly clever or over-complicated** just to show off language features.
- Prefer **explicitness over brevity** when it helps comprehension.
- Use standard tooling to enforce consistency:
    - **Ruff** for linting and formatting (99-character line length).
    - **Mypy** for type checking.
    - **Codespell** for spell checking.
- Favor **modern Python features** (3.10+), such as structural pattern matching and `match` statements, where appropriate.
- Write code that is **maintainable** by future contributors.

### 🤖 LLMs Reviewing Pull Requests

When reviewing Python code, LLMs should prioritize **clarity**, **simplicity**, and **maintainability**:

- **Avoid praising unnecessarily complex or overly generic code**.
- Use your judgment to **flag convoluted or misleading logic**, even if it passes tests.
- Suggest alternatives that are **easier to read and understand**, especially for long-term contributors who need to maintain the code.
- Your role is not just to verify correctness, but to **help improve the overall quality** of the codebase.
- Focus on:
    - **Idiomatic Python patterns** over clever tricks.
    - **Clear variable and function names** over abbreviated ones.
    - **Explicit error handling** over implicit assumptions.
    - **Testable code structure** over monolithic functions.
    - **Consistent style** with the existing codebase.

## 🔀 Git Workflow

### Commit Message Format

```text
<type>(<scope>): <description>

# Types
feat, fix, docs, style, refactor, test, chore, new

# Scopes  
evm, forks, tools, pytest, tests, docs, ci, consume, fw, tooling, gentest, fill, eest, deps, execute

# Examples
feat(eest): add new test generator command
fix(forks): resolve Cancun initialization issue  
docs(fill): describe new command-line args
new(tests): add blob transaction edge cases
```

### Branch Management

- **Main branch**: `main` (use for PRs).
- **Feature branches**: `feat/description`.
- **Fix branches**: `fix/description`.
- **Always create PRs** - never push directly to main.

## 🧪 Testing Patterns

### Test Organization by Fork

Tests are organized by Ethereum fork with specific patterns:

```python
# Mark minimum fork requirement
@pytest.mark.valid_from("Cancun") 
def test_blob_transactions(pre: Alloc, state_test: StateTestFiller):
    # Test implementation

# Fork-specific logic
if fork >= Fork.Cancun:
    post[address] = Account(storage={0: cancun_value})
else:
    post[address] = Account(storage={0: pre_cancun_value})
```

### Common Patterns

**Setting the Gas Limit/Gas Calculation**:

Use a fork class's intrinsic gas calculation method:

```python
    access_lists: List[AccessList] = [
        AccessList(
            address=access_list_address,
            storage_keys=[access_list_storage_key],
        ),
    ]

    sender = pre.fund_eoa()

    contract_creation = False
    tx_data = b""

    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()

    tx_gas_limit = (
        intrinsic_gas_calculator(
            calldata=tx_data,
            contract_creation=contract_creation,
            access_list=access_lists,
        )
        + 100_000
    )
```

**Blockchain Tests**:

State tests are generally preferred (a test in blockchain format, i.e., a 1-tx, 1-block test, always get generated from a state test).

However, blockchain tests can be used to verify block header fields or simply if it is necessary to execute multiple transactions in one or across many blocks:

```python
blocks = [
    Block(txs=[
        Transaction(sender=sender, to=contract1, ...),
        Transaction(sender=sender, to=contract2, ...),
    ])
]
blockchain_test(pre=pre, blocks=blocks, post=post)
```

**Gas Measurement**:

```python
gas_measure_code = CodeGasMeasure(
    code=Op.BLOBHASH(index),
    overhead_cost=3,
    extra_stack_items=1,
)
```

**Conditional Execution**:

```python
code = Conditional(
    condition=Op.EQ(Op.SLOAD(0), 0),
    if_true=first_execution_path,
    if_false=second_execution_path,
)
```

**Parameterized Tests**:

```python
@pytest.mark.parametrize("value", [0, 1, 2**256-1])
@pytest.mark.parametrize("fork", [Fork.Shanghai, Fork.Cancun])
def test_with_parameters(value: int, fork: Fork):
```

### Test Development Workflow

1. **Create new test module**: `uv run eest make test`.
2. **Implement**: Write test using `pre` fixture and proper patterns.
3. **Fill**: `uv run fill --fork=<fork> <test_file> --clean -v`.
4. **Debug**: Check debug_output/ for traces if needed.
5. **Validate**: Run lint and type checks.
6. **Commit**: Follow semantic commit format.

## 🐛 Debugging & Troubleshooting

### EVM Trace Analysis & Debugging

**Generate and analyze EVM execution traces:**

```bash
# Generate detailed traces for debugging
uv run fill --fork=Cancun --evm-dump-dir=debug_output/ path/to/test.py

# Extract opcode sequences for comparison
jq -r '.opName' debug_output/test_name.jsonl

# Compare traces between versions
diff <(jq -r '.opName' old.jsonl) <(jq -r '.opName' new.jsonl)

# Analyze gas consumption patterns
jq -r '.gas' debug_output/test_name.jsonl

# Check stack operations and memory changes
jq -r '.stack, .memory' debug_output/test_name.jsonl
```

**Key debugging workflow:**

1. **Generate traces** with `--evm-dump-dir=debug_output/ --traces` flags.
2. **Check debug_output/** directory for `.jsonl` files.
3. **Compare execution** between test versions to verify behavior.
4. **Analyze gas costs** and opcode sequences for optimization.

### Common Issues & Solutions

**Fill failures**:

- Check EVM binary path and fork compatibility.
- Verify bytecode syntax with `--clean` flag.
- Ensure proper gas limits (try 5_000_000+).

**Import errors**:

- Verify all imports from `ethereum_test_tools`.
- Check relative imports within packages.
- Match typing imports to actual usage.

**Address conflicts**:

- Always use `pre` fixture for new tests.
- Deploy dependencies before consumers.
- Check dependency ordering in contract deployment.

**Test collection failures**:

- Verify pytest marker syntax: `@pytest.mark.valid_from("Fork")`.
- Ensure test functions start with `test_`.
- Check proper import structure.

**Fixture validation errors**:

- Use `uv run hasher --root fixtures/` to verify integrity.
- Compare fixtures: `diff <(hasher --files fixtures/) <(hasher --files fixtures_new/)`.
- Regenerate with `--clean` flag if corrupted.

### Performance Optimization

- **Shared clients**: Use `--use-shared-clients` for test suites with common pre-state (see Advanced Features > Shared Pre-Allocation Groups).
- **Parallel execution**: Use `-n auto` with pytest-xdist for faster test runs.
- **Fixture caching**: Framework automatically caches compatible fixtures.
- **Group statistics**: Check `uv run groupstats` for pre-allocation efficiency analysis.
- **Clean regeneration**: Use `--clean` flag to ensure fresh fixture generation without cache issues.

## 🏗️ Advanced Features

### Shared Pre-Allocation Groups

For test performance, the framework groups tests by pre-state hash:

- **Enable**: Use `--use-shared-clients` flag.
- **Groups by**: Fork, genesis, and pre-allocation state.
- **Benefits**: Single client per group, reused across tests.
- **Log handling**: Captures logs per test, not per group.
- **Location**: `src/pytest_plugins/consume/hive_simulators/shared_client.py`.

### Custom Logging System

Enhanced logging with additional levels:

- **Location**: `src/pytest_plugins/logging/`.
- **Custom levels**: `VERBOSE` (15), `FAIL` (35).
- **Usage**: `get_logger(__name__)` for proper typing.
- **Contexts**: Works in both pytest and non-pytest environments.

### Auto-Generated Documentation

- **Command help pages**: Generated from actual CLI output.
- **Test references**: Auto-discovered from test cases.
- **EIP checklists**: Automated coverage verification.
- **Scripts**: Located in `docs/scripts/`, registered in `mkdocs.yml`.

### EIP Integration

- **Version checking**: `uv run check_eip_versions` validates EIP references.
- **Checklist generation**: `uv run checklist` creates testing coverage reports.
- **Fork compatibility**: Automatic fork requirement detection.

## 📚 Documentation

### Overview

The project uses **MkDocs Material** for documentation generation. Test case reference documentation is automatically generated for each test case, which makes building the full documentation **slow**.


### Building Documentation

For **faster local builds**, you can skip test case reference generation:

=== "Bash"

    ```bash
    export FAST_DOCS=true
    export GEN_TEST_DOC_VERSION="tox"
    uv run mkdocs serve
    ```

=== "Fish"

    ```fish
    set -x FAST_DOCS true
    set -x GEN_TEST_DOC_VERSION "tox"
    uv run mkdocs serve
    ```

### Environment Variables

The following environment variables are required to build the docs:

- `GEN_TEST_DOC_VERSION="tox"` - Required for documentation generation.
- `FAST_DOCS=true` - Optional: Skip test case reference generation for faster builds.

### CLI Examples in Documentation

When adding CLI examples to documentation, provide **commands that work in both shells** using MkDocs Material's command-line tab-switching feature:

=== "Bash"

    ```bash
    export VARIABLE=value
    uv run command --flag
    ```

=== "Fish"

    ```fish
    set -x VARIABLE value
    uv run command --flag
    ```

### Documentation Writing Guidelines

- Documentation should be **well-organized and easy to navigate**, but also **concise**, avoiding unnecessary verbosity.
- Favor **clear, minimal explanations** that answer questions directly, rather than overly elaborate or wordy sections.
- Focus on **practical examples** and **actionable guidance**.
- Keep technical explanations **accurate but accessible**.

### Markdown Linting

All markdown files must conform to the style rules enforced by `.markdownlint.yaml`. Key rules include:

- Bullet points must be properly punctuated with periods or commas.
- Unordered lists must use 4-space indentation.
- Code blocks should specify language when possible.
- Contributions should pass markdown linting before submission.

## 🚨 Critical Reminders

1. **ALWAYS use `uv run` prefix** for all commands.
2. **NEVER hardcode addresses** - use `pre` fixture exclusively.
3. **ALWAYS add type annotations** to functions.
4. **ALWAYS specify transaction sender** explicitly.
5. **ALWAYS mark fork requirements** with `@pytest.mark.valid_from()`.
6. **ALWAYS run lint/typecheck** before committing.
7. **NEVER push directly to main** - always create PRs.

## 🔍 Tool Preferences & Best Practices

**Search & Analysis**:

- **Use `rg` (ripgrep)** instead of `grep` for code searching: `rg "pattern" --type python` (faster, respects .gitignore).
- **Use `gh` CLI** for GitHub operations: `gh pr create --title "Title" --body "Description"`.
- **Use `jq`** for JSON analysis: `jq -r '.opName' debug_output/test_name.jsonl`.

**Testing & Development**:

- **Prefer `pytest -c pytest-framework.ini`** for framework tests (see Project Architecture > Testing Configurations).
- **Always use `--clean` flag** when regenerating fixtures to avoid cache issues.
- **Test specific functions** with `::test_function_name` syntax for faster iteration.
- **Use `uv run` prefix** for all commands (critical requirement).

**Quality & Validation**:

- **Run comprehensive checks**: `uvx --with=tox-uv tox run-parallel` before committing.
- **Fix lint issues automatically**: `uv run ruff check --fix`.
- **Type check incrementally**: `uv run mypy path/to/module`.
- **Validate fixtures**: `uv run hasher --root fixtures/` for integrity checks.

This CLAUDE.md represents the definitive guide for working with the Ethereum execution-spec-tests codebase. It prioritizes the most critical information upfront while providing comprehensive coverage of the sophisticated testing framework.
