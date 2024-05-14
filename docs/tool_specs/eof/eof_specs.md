


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
    If called with the `--hex` arg:
      The tool don't write any files. Instead if an input eof container is invalid
      it finishes with an error code and stderr an error message prefixed by eof
      exception error code, followed by the error message.

    If the container is valid, the tool finishes with 0 code.

    Example:
      eofparse --state.fork Prague --hex "0xef0000..code"
      eof00001 err: unreachable_instructions
	     
      eofparse --state.fork Prague --hex "0xef0000..code"
      OK 5fe10003e00003e00003e0fffa00
	  
    If provided with stdin stream:
      The tool parses input stream line by line, expecting hex code separated by newline
      For each hex code from input stream it performs validation and outputs the result
      in stdout where each line corresponds to the input line.

    Example:
      printf "ef000.....d60A7 \n ef000101000...B000bad60A7" | eofparse
      OK 5fe10003e00003e00003e0fffa00
      eof00001 err: unreachable_instructions

  --help
    Print options help message
```
