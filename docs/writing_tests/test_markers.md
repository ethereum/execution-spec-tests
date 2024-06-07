# Test Markers

Test markers are used to categorize tests and to run specific subsets of tests. They are defined in the test files using the `pytest.mark` decorator.

## Fork Markers

These markers are used to specify the forks for which a test is valid.

### pytest.mark.valid_from("FORK_NAME")

This marker is used to specify the fork from which the test is valid. The test will not be filled for forks before the specified fork.

```python
import pytest

@pytest.mark.valid_from("London")
def test_something_only_valid_after_london():
    pass
```

In this example, the test will only be filled for the London fork and after, e.g. London, Paris, Shanghai, Cancun, etc.

### pytest.mark.valid_until("FORK_NAME")

This marker is used to specify the fork until which the test is valid. The test will not be filled for forks after the specified fork.

```python
import pytest

@pytest.mark.valid_until("London")
def test_something_only_valid_until_london():
    pass
```

In this example, the test will only be filled for the London fork and before, e.g. London, Berlin, Istanbul, etc.

### pytest.mark.valid_at_transition_to("FORK_NAME")

This marker is used to specify that a test is only meant to be filled at the transition to the specified fork.

The test usually starts at the fork prior to the specified fork at genesis and at block 5 (for pre-merge forks) or at timestamp 15,000 (for post-merge forks) the fork transition occurs.

## Fork Covariant Markers

These markers are used in conjunction with the fork markers to automatically parameterize tests with values that are valid for the fork being tested.

### pytest.mark.with_all_tx_types

This marker is used to automatically parameterize a test with all transaction types that are valid for the fork being tested.

```python
import pytest

@pytest.mark.with_all_tx_types
@pytest.mark.valid_from("Berlin")
def test_something_with_all_tx_types(tx_type):
    pass
```

In this example, the test will be parameterized for parameter `tx_type` with values `[0, 1]` for fork Berlin, but with values `[0, 1, 2]` for fork London (because of EIP-1559).

### pytest.mark.with_all_contract_creating_tx_types

This marker is used to automatically parameterize a test with all contract creating transaction types that are valid for the fork being tested.

This marker only differs from `pytest.mark.with_all_tx_types` in that it does not include transaction type 3 (Blob Transaction type) on fork Cancun and after.

### pytest.mark.with_all_precompiles

This marker is used to automatically parameterize a test with all precompiles that are valid for the fork being tested.

```python
import pytest

@pytest.mark.with_all_precompiles
@pytest.mark.valid_from("Shanghai")
def test_something_with_all_precompiles(precompile):
    pass
```

In this example, the test will be parameterized for parameter `precompile` with values `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` for fork Shanghai, but with values `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` for fork Cancun (because of EIP-4844).

## Other Markers

### pytest.mark.slow

This marker is used to mark tests that are slow to run. These tests are not run during tox testing, and are only run when a release is being prepared.

### pytest.mark.skip("reason")

This marker is used to skip a test with a reason.

```python
import pytest

@pytest.mark.skip("Not implemented")
def test_something():
    pass
```

### pytest.mark.xfail("reason")

This marker is used to mark a test as expected to fail.

```python
import pytest

@pytest.mark.xfail("EVM binary doesn't support this opcode")
def test_something():
    pass
```
