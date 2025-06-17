# CLAUDE.md - Ethereum Execution Spec Tests

> **CRITICAL**: This repository aims to provide excellent tooling for generating JSON test vectors that test Ethereum execution layer clients. Correctness is absolute priority. The repo prioritizes a contributor-first mindset.

## 🎯 Core Purpose

- `./tests/`: Python tests that **generate JSON test vectors (fixtures)** via `fill` command
- `./src/pytest_plugins/filler/`: Implements `fill` command (test vector generation from Python source)
- `./src/pytest_plugins/consume/`: Implements `consume` command (test vector execution)
- `./src/pytest_plugins/execute/`: Implements `execute` command (live JSON-RPC testing from Python source)
- `./src/ethereum_test_*`: Core framework libraries and data structures

### Key Terminology (CRITICAL)

**"Fixtures" has TWO meanings:**

1. **Test Fixtures** (JSON files) - The test vectors this framework generates
2. **Pytest Fixtures** - Standard pytest setup/teardown (`pre`, `state_test`, etc.)

### Workflows

```text
Fill/Consume: Python Tests → fill → JSON Fixtures → consume → Client Testing
Execute: Python Tests → execute → Live JSON-RPC Testing
```

## 🚀 Essential Commands

All commands use `uv run` prefix.

### Setup

```bash
uv sync --all-extras
uv run solc-select use 0.8.24 --always-install
uvx pre-commit install
```

### Core Workflow

```bash
# Create test
uv run eest make test

# Generate fixtures (PRIMARY WORKFLOW)
uv run fill --fork=Prague path/to/test.py --clean -v -m "not slow"

# Execute against client
uv run consume direct --bin=evm fixtures/

# Framework testing
uv run pytest -c pytest-framework.ini path/to/test.py::test_function
```

### Quality Checks

```bash
# Check code style and errors
uv run ruff check src tests .github/scripts

# Format code
uv run ruff format src tests .github/scripts

# Fix auto-fixable issues
uv run ruff check --fix src tests .github/scripts

# Type checking
uv run mypy src tests .github/scripts

# Framework unit tests
uv run pytest -c pytest-framework.ini -n auto -m "not run_in_serial"
uv run pytest -c pytest-framework.ini -m run_in_serial

# Run specific checks (fast checks)
uvx --with=tox-uv tox -e lint,typecheck,spellcheck

# Local docs check (fast mode: these warnings can be ignored "WARNING -  Doc file 'writing_tests/..."):
export FAST_DOCS=true && export GEN_TEST_DOC_VERSION="tox" && uv run mkdocs build
```

## 🎯 Core Framework Rules

### NEVER Use Hardcoded Addresses

```python
def test_example(pre: Alloc, state_test: StateTestFiller):
    # ✅ Dynamic allocation
    sender = pre.fund_eoa()
    contract = pre.deploy_contract(code=Op.SSTORE(1, 1))
    
    tx = Transaction(sender=sender, to=contract, gas_limit=5_000_000)
    state_test(pre=pre, tx=tx, post={contract: Account(storage={1: 1})})
```

### Key Methods

- `pre.deploy_contract(code, **kwargs) -> Address`
- `pre.fund_eoa(amount=None, **kwargs) -> EOA`
- `pre.fund_address(address, amount)`

### Gas Calculation Pattern

```python
intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
tx_gas_limit = intrinsic_gas_calculator(
    calldata=tx_data,
    contract_creation=False,
    access_list=access_lists,
) + 100_000
```

## 📁 Key Directories

```text
src/
├── ethereum_test_tools/     # Core framework
├── ethereum_test_types/     # Type definitions
├── ethereum_test_fixtures/  # Pydantic models for test fixtures
├── pytest_plugins/         # Plugin system
tests/                       # Test cases by fork
fixtures/                    # Generated test vectors (default output directory)
```

## ⚠️ Critical Anti-Patterns

- ❌ Hardcoded addresses (use `pre` fixture)
- ❌ `TestAddress` in new tests (use `pre.fund_eoa()`)
- ❌ Missing `sender` parameter in transactions
- ❌ Missing `@pytest.mark.valid_from("Fork")` markers
- ❌ Manual nonce management

## 🔧 Common Patterns

### Fork Compatibility

```python
@pytest.mark.valid_from("Cancun")
def test_example(pre: Alloc, state_test: StateTestFiller):
    if fork >= Fork.Cancun:
        # Cancun-specific logic
    else:
        # Pre-Cancun logic
```

### Parameterized Tests

```python
@pytest.mark.parametrize("value", [0, 1, 2**256-1])
def test_with_params(value: int, pre: Alloc, state_test: StateTestFiller):
```

## 🐛 Debugging Test Filling

### Generate EVM Traces

```bash
uv run fill --fork=Prague --evm-dump-dir=debug_output/ --traces path/to/test.py
jq -r '.opName' debug_output/**/*.jsonl
```

### Common Issues

- **Fill failures**: Check gas limits (increase if needed, use `transaction_intrinsic_cost_calculator`)
- **Address conflicts**: Always use `pre` fixture for dynamic allocation
- **Test collection**: Functions must start with `test_`
- **Import errors**: Check dependencies in `pyproject.toml`, run `uv sync --all-extras`

## 📝 Code Standards

- **Line length**: 100 characters
- **Type annotations**: Required
- **Import style**: Explicit imports only, no `import *`, no local imports.
- **Path handling**: Use `pathlib`
- **Code**: Use idiomatic python, prioritize readability.
- **Docstrings**: Always include for methods and classes. For one-liners """Use one single-line docstring with quotes on same line."""

## Commit Format

```text
<type>(<scope>): <description>

# Types: feat, fix, docs, style, refactor, test, chore, new
# Scopes: evm, forks, tools, pytest, tests, docs, ci, consume, fill, eest
```

## 🔍 Tool Preferences

- **Search**: `rg "pattern" --type python` (not grep)
- **JSON**: `jq -r '.field' file.json`
- **GitHub**: `gh` CLI for all operations

## 🎯 Development Workflow

1. `uv run eest make test` - Create test
2. Implement tests using `pre` fixture patterns
3. `uv run fill --fork=Fork test.py --clean -v tests/path/to/module` - Generate fixtures
4. `uv run ruff check --fix` - Fix linting
5. Commit with semantic format

**Critical**: Always run linting and type checking. Use `--clean` when filling. Never use hardcoded addresses.
