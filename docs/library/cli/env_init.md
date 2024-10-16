# The `env_init` CLI

Generate an example `env.yaml` [environment](../../dev/configurations.md) config file if it doesn't exist.

```console
➜ uv run env_init http EnvConfig
Env file created:  execution-spec-tests/env.yaml
```

If an `env.yaml` already exists, this command will NOT override it. In that case, it is recommended to manually make changes.

```console
➜ ls | grep "env.yaml"
env.yaml
➜ uv run env_init
🚧 The configuration file 'execution-spec-tests/env.yaml' already exists. Please update it manually if needed.
```
