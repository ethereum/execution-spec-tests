# Test Markers

Test markers are used to categorize tests and to run specific subsets of tests. They are defined in the test files using the `pytest.mark` decorator.

The examples below use `StateTestFiller` tests, but the same markers can also be applied to `BlockchainTestFiller` tests.

## Fork Markers

These markers are used to specify the forks for which a test is valid.

### `@pytest.mark.valid_from("FORK_NAME")`

This marker is used to specify the fork from which the test is valid. The test will not be filled for forks before the specified fork.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller

@pytest.mark.valid_from("London")
def test_something_only_valid_after_london(
    state_test: StateTestFiller, 
    pre: Alloc
):
    pass
```

In this example, the test will only be filled for the London fork and after, e.g. London, Paris, Shanghai, Cancun, etc.

### `@pytest.mark.valid_until("FORK_NAME")`

This marker is used to specify the fork until which the test is valid. The test will not be filled for forks after the specified fork.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller

@pytest.mark.valid_until("London")
def test_something_only_valid_until_london(
    state_test: StateTestFiller, 
    pre: Alloc
):
    pass
```

In this example, the test will only be filled for the London fork and before, e.g. London, Berlin, Istanbul, etc.

### `@pytest.mark.valid_at_transition_to("FORK_NAME")`

This marker is used to specify that a test is only meant to be filled at the transition to the specified fork.

The test usually starts at the fork prior to the specified fork at genesis and at block 5 (for pre-merge forks) or at timestamp 15,000 (for post-merge forks) the fork transition occurs.

## Fork Covariant Markers

These markers are used in conjunction with the fork validity markers to automatically parameterize tests with values that are valid for the fork being tested.

### `@pytest.mark.with_all_tx_types`

This marker is used to automatically parameterize a test with all transaction types that are valid for the fork being tested.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller

@pytest.mark.with_all_tx_types
@pytest.mark.valid_from("Berlin")
def test_something_with_all_tx_types(
    state_test: StateTestFiller, 
    pre: Alloc,
    tx_type: int
):
    pass
```

In this example, the test will be parameterized for parameter `tx_type` with values `[0, 1]` for fork Berlin, but with values `[0, 1, 2]` for fork London (because of EIP-1559).

### `@pytest.mark.with_all_contract_creating_tx_types`

This marker is used to automatically parameterize a test with all contract creating transaction types that are valid for the fork being tested.

This marker only differs from `pytest.mark.with_all_tx_types` in that it does not include transaction type 3 (Blob Transaction type) on fork Cancun and after.

### `@pytest.mark.with_all_precompiles`

This marker is used to automatically parameterize a test with all precompiles that are valid for the fork being tested.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller

@pytest.mark.with_all_precompiles
@pytest.mark.valid_from("Shanghai")
def test_something_with_all_precompiles(
    state_test: StateTestFiller, 
    pre: Alloc,
    precompile: int,
):
    pass
```

In this example, the test will be parameterized for parameter `precompile` with values `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` for fork Shanghai, but with values `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` for fork Cancun which introduced the [point evaluation precompile](https://eips.ethereum.org/EIPS/eip-4844#point-evaluation-precompile) defined in EIP-4844.

### `@pytest.mark.with_all_evm_code_types`

This marker is used to automatically parameterize a test with all EVM code types that are valid for the fork being tested.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller

@pytest.mark.with_all_evm_code_types
@pytest.mark.valid_from("Frontier")
def test_something_with_all_evm_code_types(
    state_test: StateTestFiller,     
    pre: Alloc,
):
    pass
```

In this example, the test will be parameterized for parameter `evm_code_type` only with value `[EVMCodeType.LEGACY]` starting on fork Frontier, and eventually it will be parametrized with with values `[EVMCodeType.LEGACY, EVMCodeType.EOF_V1]` on the EOF activation fork.

In all calls to `pre.deploy_contract`, if the code parameter is `Bytecode` type, and `evm_code_type==EVMCodeType.EOF_V1`, the bytecode will be automatically wrapped in an EOF V1 container.

Code wrapping might fail in the following circumstances:

- The code contains invalid EOF V1 opcodes.
- The code does not end with a valid EOF V1 terminating opcode (such as `Op.STOP` or `Op.REVERT` or `Op.RETURN`).

In the case where the code wrapping fails, `evm_code_type` can be added as a parameter to the test and the bytecode can be dynamically modified to be compatible with the EOF V1 container.

One thing to note is that `evm_code_type` is not necessary to be added as a parameter to the test because the `pre: Alloc` fixture automatically consumes this fixture, and therefore it only needs to be added to the test signature if the test's logic needs it.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller
from ethereum_test_vm import EVMCodeType
from ethereum_test_vm import Opcodes as Op

@pytest.mark.with_all_evm_code_types
@pytest.mark.valid_from("Frontier")
def test_something_with_all_evm_code_types(
    state_test: StateTestFiller,
    pre: Alloc,
    evm_code_type: EVMCodeType
):
    code = Op.SSTORE(1, 1)
    if evm_code_type == EVMCodeType.EOF_V1:
        # Modify the bytecode to be compatible with EOF V1 container
        code += Op.STOP
    pre.deploy_contract(code)
    ...
```

### `@pytest.mark.with_all_call_opcodes`

This marker is used to automatically parameterize a test with all EVM call opcodes that are valid for the fork being tested.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller
from ethereum_test_vm import Opcodes as Op

@pytest.mark.with_all_call_opcodes
@pytest.mark.valid_from("Frontier")
def test_something_with_all_call_opcodes(
    state_test: StateTestFiller,
    pre: Alloc,
    call_opcode: Op
):
    pass
```

In this example, the test will be parametrized for parameter `call_opcode` with values `[Op.CALL, Op.CALLCODE]` starting on fork Frontier, `[Op.CALL, Op.CALLCODE, Op.DELEGATECALL]` on fork Homestead, `[Op.CALL, Op.CALLCODE, Op.DELEGATECALL, Op.STATICCALL]` on fork Byzantium, and eventually it will be parametrized with with values `[Op.CALL, Op.CALLCODE, Op.DELEGATECALL, Op.STATICCALL, Op.EXTCALL, Op.EXTSTATICCALL, Op.EXTDELEGATECALL]` on the EOF activation fork.

Parameter `evm_code_type` will also be parametrized with the correct EVM code type for the opcode under test.

### `@pytest.mark.with_all_create_opcodes`

This marker is used to automatically parameterize a test with all EVM create opcodes that are valid for the fork being tested.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller
from ethereum_test_vm import Opcodes as Op

@pytest.mark.with_all_create_opcodes
@pytest.mark.valid_from("Frontier")
def test_something_with_all_create_opcodes(
    state_test: StateTestFiller,
    pre: Alloc,
    create_opcode: Op
):
    pass
```

In this example, the test will be parametrized for parameter `create_opcode` with values `[Op.CREATE]` starting on fork Frontier, `[Op.CREATE, Op.CREATE2]` starting on fork Constantinople, and eventually it will be parametrized with with values `[Op.CREATE, Op.CREATE2, Op.EOFCREATE]` on the EOF activation fork.

Parameter `evm_code_type` will also be parametrized with the correct EVM code type for the opcode under test.

### `@pytest.mark.with_all_system_contracts`

This marker is used to automatically parameterize a test with all system contracts that are valid for the fork being tested.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller
from ethereum_test_base_types import Address

@pytest.mark.with_all_system_contracts
@pytest.mark.valid_from("Cancun")
def test_something_with_all_system_contracts(
    state_test: StateTestFiller,
    pre: Alloc,
    system_contract: Address,
):
    pass

```

In this example, the test will be parameterized for parameter `system_contract` with value `[0x000F3DF6D732807EF1319FB7B8BB8522D0BEAC02]` for fork Cancun.

### Covariant Marker Keyword Arguments

All fork covariant markers accept the following keyword arguments:

#### `selector`

A lambda function that can be used to filter the fork covariant values that are valid for this specific test.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller

@pytest.mark.with_all_tx_types(selector=lambda tx_type: tx_type != 2)
@pytest.mark.valid_from("London")
def test_something_with_all_tx_types(
    state_test: StateTestFiller, 
    pre: Alloc,
    tx_type: int
):
    pass
```

Ideally, the lambda function should be used to explicitly filter out values that are not compatible with the test (exclusive filter), rather than explicitly selecting values (inclusive filter), as the parametrized values might change with future forks.

#### `marks`

A marker, list of markers, or a lambda function that can be used to add additional markers to the test.

```python
import pytest

@pytest.mark.with_all_tx_types(
    marks=lambda tx_type: pytest.mark.skip("incompatible") if tx_type == 1 else None,
)
@pytest.mark.valid_from("London")
def test_something_with_all_tx_types_but_skip_type_1(state_test_only, tx_type):
    assert tx_type != 1
    ...
```

In this example, the test will be skipped if `tx_type` is equal to 1 by returning a `pytest.mark.skip` marker, and return `None` otherwise.

## Other Markers

### `@pytest.mark.slow`

This marker is used to mark tests that are slow to run. These tests are not run during tox testing, and are only run when a release is being prepared.

### `@pytest.mark.pre_alloc_modify`

This marker is used to mark tests that modify the pre-alloc in a way that would be impractical to reproduce in a real-world scenario.

Examples of this include:

- Modifying the pre-alloc to have a balance of 2^256 - 1.
- Address collisions that would require hash collisions.

### `@pytest.mark.skip()`

This marker can be used to skip a test.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller

@pytest.mark.skip(reason="Not implemented")
def test_something(state_test: StateTestFiller, pre: Alloc):
    pass
```

### `@pytest.mark.xfail()`

This marker can be used to mark a test as expected to fail.

```python
import pytest

from ethereum_test_tools import Alloc, StateTestFiller

@pytest.mark.xfail(reason="EVM binary doesn't support this opcode")
def test_something(state_test: StateTestFiller, pre: Alloc):
    pass
```
