"""
Automatically generate JSON schema for the tool specification types.
"""

import mkdocs_gen_files
import yaml

from ethereum_test_tools.common.types import (
    Environment,
    RejectedTransaction,
    Result,
    TransactionLog,
    TransitionToolOutput,
)

t8n_types_file = "tool_specs/t8n/types.md"

types = {
    "Environment": Environment,
    "RejectedTransaction": RejectedTransaction,
    "Result": Result,
    "TransactionLog": TransactionLog,
    "TransitionToolOutput": TransitionToolOutput,
}

with mkdocs_gen_files.open(t8n_types_file, "w") as f:
    for t in types:
        json_schema = types[t].model_json_schema()
        f.write(f"## {t}\n\n")
        f.write("```yaml\n")
        f.write(f"{yaml.dump(json_schema, indent=2)}\n")
        f.write("```\n\n")
        f.write("\n\n")
