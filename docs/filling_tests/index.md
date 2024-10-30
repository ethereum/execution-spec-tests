# Filling Tests

Execution of test cases against clients is a two-step process. First JSON test fixtures are generated from the Python test cases in this repository using `fill`. Then the resulting JSON fixtures can be executed against a client. The process of generating fixtures is often referred to as "filling" the tests.

!!! note "The `execute` command"

    The `execute` command can directly execute test cases against a client via its RPC without using generated JSON fixtures. For all other methods of testing clients, the JSON fixtures are required.
