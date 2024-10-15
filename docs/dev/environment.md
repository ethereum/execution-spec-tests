# Setting up your environment

Application-wide [environment configuration](https://www.12factor.net/config), which varies across staging, production, and development environments are read from `env.yaml` in the project root.

This file will not be tracked by git, making it safe for storing local secrets.

To get started, run the command [env_init](../library/cli/env_init.md) cli to initialize your environment configuration.

```console
.
├── src
│   └── 📁 config  [Application wide environment and configurations]
│       ├── 📄 __init__.py
│       └── 📄 env.py  [Exposes `env.yaml` to the application]
└── 📄 env.yaml [Environment file (git ignored)]
```

## Usage

### 1. Generate env file

Run the [`env_init`](../library/cli/env_init.md) cli tool.

```console
➜ uv run env_init
Env file created:  execution-spec-tests/env.yaml
```

which should generate an `env.yaml` in the project root.

```yaml
remote_nodes:
  - name: mainnet_archive
    # Replace with your Ethereum RPC node URL
    node_url: http://example.com
    # Optional: Headers for RPC requests
    rpc_headers:
      client-secret: <secret>
```

### 2. Import `EnvConfig`

```console
from config import EnvConfig
EnvConfig().remote_nodes[0].name
'mainnet_archive'
```
