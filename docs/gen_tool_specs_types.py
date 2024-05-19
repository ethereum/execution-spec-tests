"""
Automatically generate JSON schema for the tool specification types.
"""

import mkdocs_gen_files

from ethereum_test_tools.common.types import RejectedTransaction, Result, TransitionToolOutput

t8n_types_file = "tool_specs/t8n/types.md"
