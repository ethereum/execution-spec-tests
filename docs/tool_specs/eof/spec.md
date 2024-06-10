


# Ethereum EVM Object Format code verification tool

Each client is required to implement the `evm eof` tool, which is used to validate EOF code tests by verifying EOF container validity.

**Format**: `[eof code] -> [result]`

## EVM EOF CLI:

**Usage:**

    evm-eof [command options] [arguments...]
    echo $inputstream | evm-eof

**Options:**

```
Parameters:
  --state.fork value (required)
     Sets the fork rules and all EIPs included in it for EOF code validation.
     Current supported forks and EIPs: ["Prague"]

Inputs:
  --hex code (required)
     Direct input of the EVM EOF bytecode


Outputs:
    If called with the `--hex` argument:
      The tool don't write any files. Instead if an input EOF container is invalid
      it finishes with an error code and an error message will be written to standard error prefixed by EOF
      exception error code, followed by the error message.

      If the container is valid, the tool finishes with 0 code. And the strout message
      contains OK followed by the hexcode of code sections that has successfully been
      parsed, separated by commas.

      Example:
        eofparse --state.fork Prague --hex "0xef0000..code"
        eof00001 err: unreachable_instructions
	     
        eofparse --state.fork Prague --hex "0xef0000..code"
        OK 5f35...000400,5f5ff3,5f5ffd,fe,e4
	  
    If provided with stdin stream:
      The tool parses input stream line by line, expecting hex code separated by newline
      For each hex code from input stream it performs validation and outputs the result
      in stdout where each line corresponds to the input line.

      Example:
        printf "ef000.....d60A7 \n ef000101000...B000bad60A7" | eofparse
        OK 5f35...000400,5f5ff3,5f5ffd,fe,e4
        eof00001 err: unreachable_instructions

    Note: The bytes were ommited here to save screen space. the code represents valid EOF
    Note: eof00001 - is an example exception code, the table of exception codes to be defined

  --help
    Print options help message
```
