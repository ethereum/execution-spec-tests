# EIP Checklist Generation

The EIP checklist feature helps track test coverage for EIP implementations by automatically generating filled checklists based on test markers.

## Overview

When implementing tests for an EIP, you can mark specific tests as covering checklist items from the [EIP testing checklist template](../writing_tests/checklist_templates/eip_testing_checklist_template.md). The framework will then generate a filled checklist showing which items have been implemented.

## Using the `pytest.mark.eip_checklist` Marker

To mark a test as implementing a specific checklist item:

```python
import pytest
from ethereum_test_tools import StateTestFiller

@pytest.mark.eip_checklist("new_transaction_type/test/intrinsic_validity/gas_limit/exact")
def test_exact_intrinsic_gas(state_test: StateTestFiller):
    """Test transaction with exact intrinsic gas limit."""
    # Test implementation
    pass
```

### Marker Parameters

- **First positional parameter** (required): The checklist item ID from the template
- **`eip` keyword parameter** (optional): List of additional EIPs covered by the test

Example with multiple EIPs covered by the same test:

```python
@pytest.mark.eip_checklist("new_transaction_type/test/signature/invalid/v/0", eip=[7702, 2930])
def test_invalid_signature(state_test: StateTestFiller):
    """Test invalid signature that affects multiple EIPs."""
    pass
```

## Generating Checklists

### Using the Dedicated `checklist` Command

To generate only checklists without filling fixtures:

```bash
# Generate checklists for all EIPs
checklist

# Generate checklist for specific EIP
checklist --eip 7702

# Specify output directory
checklist --output ./my-checklists

# Multiple EIPs
checklist --eip 7702 --eip 2930
```

### Automatic Generation in Documentation

When building the documentation with `mkdocs`, checklists are automatically generated for all EIPs that have tests with checklist markers. The checklists appear in the test documentation alongside the test modules.

## Output Format

The generated checklist will show:

- ✅ for completed items
- Test names that implement each item (up to 3, with "..." if more)
- Empty cells for uncompleted items
- A percentage of covered checklist items
