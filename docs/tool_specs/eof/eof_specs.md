

# Ethereum EVM Object Format code verification tool

Each client is required to implement the `evm eof` tool, which is used to validate eof code tests by verifying eof container validity.

**Format**: `[eof code] -> [result]`

## EVM EOF CLI:

**Usage:**

    evm-eof [command options] [arguments...]
    echo $inputstream | evm-eof

**Options:**

```
Parameters:
  --state.fork value (required)
	   Sets the fork rules and all EIPs included in it for eof code validation.
	   Current supported forks and EIPs: ["Prague"]

Inputs:
  --hex code (required)
	   Direct input of the evm eof bytecode


Outputs:
	The tool don't write any files. Instead if an input eof container is invalid it finishes with an error code and stderr an error message prefixed by eof exception error code, followed by the error message. 
	If the container is valid, the tool finishes with 0 code.

  --help
	   Print options help message
```
