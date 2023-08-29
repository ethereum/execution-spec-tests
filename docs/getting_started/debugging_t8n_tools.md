# Debugging Transition Tools

The `--t8n-dump-dir` flag can be used to dump the inputs and outputs of every call made to the `t8n` command to help debugging or simply understand how a test is interacting with the EVM.

In particular, a script `t8n.sh` is generated for each call to the `t8n` command which can be used to reproduce the call to trigger errors or attach a debugger without the need to execute Python.

For example, running:

```console
fill tests/berlin/eip2930_access_list/ --fork Berlin \
    --t8n-dump-dir=/tmp/evm-t8n-dump
```

will produce the directory structure:

```console
/tmp/evm-t8n-dump/
└── test_access_list_fork_Berlin
    ├── 0
    │   ├── args.py
    │   ├── input
    │   │   ├── alloc.json
    │   │   ├── env.json
    │   │   └── txs.json
    │   ├── output
    │   │   ├── alloc.json
    │   │   ├── result.json
    │   │   └── txs.rlp
    │   ├── returncode.txt
    │   ├── stderr.txt
    │   ├── stdin.txt
    │   ├── stdout.txt
    │   └── t8n.sh
    └── 1
        ├── args.py
        ├── input
        │   ├── alloc.json
        │   ├── env.json
        │   └── txs.json
        ├── output
        │   ├── alloc.json
        │   ├── result.json
        │   └── txs.rlp
        ├── returncode.txt
        ├── stderr.txt
        ├── stdin.txt
        ├── stdout.txt
        └── t8n.sh
```

where the directories `0` and `1` correspond to the different calls made to the `t8n` tool executed during the test:

- `0` corresponds to the call used to calculate the state root of the test's initial alloc (which is why it has an empty transaction list).
- `1` corresponds to the call used to execute the first transaction or block from the test.

Note, there may be more directories present `2`, `3`, `4`,... if the test executes more transactions/blocks.

Each directory contains files containing information corresponding to the call, for example, the `args.py` file contains the arguments passed to the `t8n` command and the `output/alloc.json` file contains the output of the `t8n` command's `--output-alloc` flag.

## The `t8n.sh` Script

The `t8n.sh` script written to the debug directory can be used to reproduce any call made to the `t8n` command, for example, if a Besu `t8n-server` has been started on port `3001`, the request made by the test for first transaction can be reproduced as:

```console
/tmp/besu/test_access_list_fork_Berlin/1/t8n.sh 3021
```

which writes the response the from the `t8n-server` to the console output:

```json
{
  "alloc" : {
    "0x000000000000000000000000000000000000aaaa" : {
      "code" : "0x5854505854",
      "balance" : "0x4",
      "nonce" : "0x1"
    },
    "0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba" : {
      "balance" : "0x1bc16d674ecb26ce"
    },
    "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {
      "balance" : "0x2cd931",
      "nonce" : "0x1"
    }
  },
  "body" : "0xf8a0b89e01f89b0180078304ef0094000000000000000000000000000000000000aaaa0180f838f7940000000000000000000000000000000000000000e1a0000000000000000000000000000000000000000000000000000000000000000001a02e16eb72206c93c471b5894800495ee9c64ae2d9823bcc4d6adeb5d9d9af0dd4a03be6691e933a0816c59d059a556c27c6753e6ce76d1e357b9201865c80b28df3",
  "result" : {
    "stateRoot" : "0x51799508f764047aee6606bc6a00863856f83ee5b91555f00c8a3cbdfbec5acb",
    ...
    ...
  }
}
```

The `t8n.sh` is written to the debug directory for all [supported t8n tools](../index.md#transition-tool-support).
