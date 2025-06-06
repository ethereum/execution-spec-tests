# Troubleshooting Guide

This guide covers common issues encountered when running EEST consume commands and Hive simulators, along with their solutions.

## Environment and Setup Issues

### Problem: `HIVE_SIMULATOR Environment Variable Not Set`

!!! danger "Problem: `The HIVE_SIMULATOR environment variable is not set`"
    When trying to run consume commands without connecting to a Hive instance, you encounter:

    ```bash
    The HIVE_SIMULATOR environment variable is not set
    ```

!!! success "Solution: Set up Hive development mode"
    Start Hive in development mode and set the environment variable:

    ```bash
    # Start Hive in development mode
    ./hive --dev --client go-ethereum

    # Set the environment variable
    export HIVE_SIMULATOR=http://127.0.0.1:3000

    # Or set custom port if using --dev.addr
    export HIVE_SIMULATOR=http://127.0.0.1:5000
    ```

    **Verification:**
    ```bash
    echo $HIVE_SIMULATOR
    curl $HIVE_SIMULATOR/
    ```

### Problem: `Connection Refused`

!!! danger "Problem: `Connection refused` when running consume commands"
    The consume command fails to connect to the Hive simulator with connection errors.

=== "Hive not running"

    !!! success "Solution: Start Hive"
        ```bash
        # Check if Hive is running
        ps aux | grep hive
        
        # Start Hive in dev mode
        ./hive --dev --client your-client
        ```

=== "Wrong port"

    !!! success "Solution: Check and set correct port"
        ```bash
        # Check what port Hive is using
        ./hive --dev --dev.addr 127.0.0.1:3000
        export HIVE_SIMULATOR=http://127.0.0.1:3000
        ```

=== "Firewall blocking"

    !!! success "Solution: Configure firewall"
        ```bash
        # Test connection
        telnet 127.0.0.1 3000
        
        # If needed, configure firewall
        sudo ufw allow 3000
        ```

### Problem: `Docker Connection Issues`

!!! danger "Problem: `Cannot connect to Docker daemon`"
    Docker is not running or not accessible.

!!! success "Solution: Start and configure Docker"
    ```bash
    # Check Docker service
    sudo systemctl status docker

    # Start Docker if not running
    sudo systemctl start docker

    # Add user to docker group (logout/login required)
    sudo usermod -a -G docker $USER
    ```

!!! danger "Problem: `Permission denied while trying to connect to Docker`"
    User lacks permissions to access Docker.

!!! success "Solution: Fix Docker permissions"
    ```bash
    # Option 1: Add user to docker group
    sudo usermod -a -G docker $USER
    newgrp docker  # or logout/login

    # Option 2: Run with sudo (not recommended)
    sudo ./hive --sim ethereum/eest/consume-engine
    ```

## Client Build Issues

### Problem: `Docker Build Failures`

!!! danger "Problem: `Image build failed` with compilation errors"
    Client Docker image fails to build with Go or other compilation errors:

    ```
    module requires Go 1.19
    ```

!!! success "Solution: Update and rebuild images"
    ```bash
    # Update base images
    ./hive --docker.pull --sim ethereum/eest/consume-engine

    # Force rebuild with no cache
    ./hive --docker.nocache "clients/.*" --sim ethereum/eest/consume-engine

    # Show build output for debugging
    ./hive --docker.buildoutput --sim ethereum/eest/consume-engine
    ```

### Problem: `Git Repository Issues`

!!! danger "Problem: `Git repository not found or permission denied`"
    Client configuration references invalid or inaccessible repositories.

=== "Wrong repository URL"

    !!! success "Solution: Fix repository configuration"
        ```yaml
        # Incorrect
        build_args:
          github: ethereum/go-ethereum-wrong
        
        # Correct  
        build_args:
          github: ethereum/go-ethereum
        ```

=== "Non-existent branch/tag"

    !!! success "Solution: Verify branch exists"
        ```yaml
        # Check if branch exists before using
        build_args:
          github: ethereum/go-ethereum
          tag: existing-branch-name
        ```

=== "Private repository access"

    !!! success "Solution: Configure git credentials"
        ```bash
        # For private repos, configure git credentials
        git config --global credential.helper store
        ```

### Problem: `Local Build Path Issues`

!!! danger "Problem: `Local path not found` with local Dockerfiles"
    Local client source code is not in the expected location.

!!! success "Solution: Copy code to correct location"
    ```bash
    # Ensure local code is copied to correct location
    cp -r /path/to/your/client ./clients/client-name/client-name-local

    # Update configuration
    build_args:
      local_path: ./clients/client-name/client-name-local
    ```

## Client Runtime Issues

### Problem: `Client Startup Timeout`

!!! danger "Problem: `Client failed to start within timeout`"
    Client takes too long to start or fails during initialization.

=== "Increase timeout"

    !!! success "Solution: Allow more time for startup"
        ```bash
        ./hive --client.checktimelimit=60s --sim ethereum/eest/consume-engine
        ```

=== "Check client logs"

    !!! success "Solution: Debug with logs"
        ```bash
        ./hive --docker.output --sim ethereum/eest/consume-engine
        
        # Check specific container logs
        docker logs <container-id>
        ```

### Problem: `Port Configuration Issues`

!!! danger "Problem: `Client not responding on expected port`"
    Client is not listening on the port expected by the simulator.

=== "RLP simulator (port 8545)"

    !!! success "Solution: Verify RLP port configuration"
        ```bash
        # Check if client is listening on correct port
        docker exec <container-id> netstat -tlnp | grep 8545
        
        # Ensure client configuration
        environment:
          HIVE_CHECK_LIVE_PORT: "8545"
        ```

=== "Engine simulator (port 8551)"

    !!! success "Solution: Verify Engine API port configuration"
        ```bash
        # Check Engine API port
        docker exec <container-id> netstat -tlnp | grep 8551
        
        # Ensure client configuration
        environment:
          HIVE_CHECK_LIVE_PORT: "8551"
        ```

### Problem: `Client Crashes During Tests`

!!! danger "Problem: `Client container exits unexpectedly`"
    Client crashes during test execution.

!!! success "Solution: Debug client crashes"
    1. **Check exit status:**
       ```bash
       docker ps -a | grep <client-name>
       ```

    2. **Examine logs:**
       ```bash
       docker logs <container-id>
       ```

    3. **Increase log verbosity:**
       ```bash
       ./hive --sim.loglevel 5 --docker.output --sim ethereum/eest/consume-engine
       ```

    4. **Run with single test:**
       ```bash
       ./hive --sim.limit "id:specific-test-id" --sim ethereum/eest/consume-engine
       ```

## Test Execution Issues

### Problem: `Test Pattern Matching`

!!! danger "Problem: `No tests match the specified pattern`"
    Test filtering patterns don't match any tests.

=== "Wrong syntax"

    !!! success "Solution: Use correct pattern syntax"
        ```bash
        # Hive regex syntax
        ./hive --sim.limit ".*fork_Prague.*"
        
        # EEST pytest syntax (dev mode)
        uv run consume engine -k "fork_Prague"
        ```

=== "Special characters in test IDs"

    !!! success "Solution: Use exact ID matching"
        ```bash
        # Use id: prefix for exact matching
        ./hive --sim.limit "id:tests/path/test.py::test_name[param]"
        ```

=== "Verify pattern"

    !!! success "Solution: Test pattern with collectonly"
        ```bash
        # Check what matches your pattern
        ./hive --sim.limit "collectonly:.*your_pattern.*" --docker.output
        ```

### Problem: `Fixture Loading Issues`

!!! danger "Problem: `Fixture directory does not exist` or `No JSON files found`"
    Test fixtures are missing or inaccessible.

=== "Check fixture path"

    !!! success "Solution: Verify fixture location"
        ```bash
        # Verify fixtures exist
        ls -la ./fixtures/
        find ./fixtures/ -name "*.json" | head -5
        ```

=== "Download fixtures"

    !!! success "Solution: Obtain fixtures"
        ```bash
        # Use specific release
        --sim.buildarg fixtures=https://github.com/ethereum/execution-spec-tests/releases/download/v4.1.0/fixtures_develop.tar.gz
        
        # Use release shortcuts
        --sim.buildarg fixtures=stable@latest
        ```

=== "Format compatibility"

    !!! success "Solution: Check fixture format"
        ```bash
        # RLP simulator needs blockchain_tests
        ls fixtures/blockchain_tests/
        
        # Engine simulator needs blockchain_tests_engine  
        ls fixtures/blockchain_tests_engine/
        ```

## Performance Issues

### Problem: `Slow Test Execution`

!!! danger "Problem: `Tests running very slowly`"
    Test execution takes much longer than expected.

!!! success "Solution: Optimize performance"
    1. **Increase parallelism:**
       ```bash
       ./hive --sim.parallelism 4 --sim ethereum/eest/consume-engine
       ```

    2. **Reduce logging:**
       ```bash
       ./hive --sim.loglevel 2 --sim ethereum/eest/consume-engine
       ```

    3. **Remove docker output for faster execution:**
       ```bash
       # Remove --docker.output for production runs
       ./hive --sim ethereum/eest/consume-engine
       ```

    4. **Use local fixtures:**
       ```bash
       # Avoid re-downloading fixtures
       uv run consume engine --input ./cached_fixtures/
       ```

### Problem: `Memory Issues`

!!! danger "Problem: `Out of memory` or container killed"
    Tests fail due to insufficient memory.

!!! success "Solution: Increase memory allocation"
    1. **Check Docker memory:**
       ```bash
       # Check Docker memory settings
       docker system info | grep Memory
       ```

    2. **Reduce test parallelism:**
       ```bash
       ./hive --sim.parallelism 1 --sim ethereum/eest/consume-engine
       ```

    3. **Run tests in batches:**
       ```bash
       # Run specific test subsets
       uv run consume engine -k "eip1559"
       uv run consume engine -k "eip4844"
       ```

### Problem: `Disk Space Issues`

!!! danger "Problem: `No space left on device`"
    Insufficient disk space for test execution.

!!! success "Solution: Free up disk space"
    1. **Clean Docker images:**
       ```bash
       docker system prune -a
       docker volume prune
       ```

    2. **Clean Hive workspace:**
       ```bash
       rm -rf workspace/logs/*
       ```

    3. **Clean fixture cache:**
       ```bash
       rm -rf cached_downloads/*
       ```

## Exception and Validation Issues

### Problem: `Exception Mapping Errors`

!!! danger "Problem: `Undefined exception message` or exception mapping failures"
    Exception validation fails with mismatched error messages:

    ```
    expected exception: "TransactionException.INSUFFICIENT_ACCOUNT_FUNDS"
    returned exception: "zero gasUsed but transactions present"
    ```

!!! success "Solution: Configure exception handling"
    1. **Disable strict exception matching:**
       ```bash
       # For specific client
       uv run consume engine --disable-strict-exception-matching=nimbus
       # For specific fork
       uv run consume engine --disable-strict-exception-matching=prague
       # For multiple clients/forks
       uv run consume engine --disable-strict-exception-matching=nimbus,prague
       ```

    2. **Update exception mapper:**
       Check and update the client's exception mapper in:
       ```
       src/ethereum_clis/clis/<client-name>.py
       ```

    3. **For Hive runs, add flag to Dockerfile:**
       ```dockerfile
       # In hive simulator Dockerfile
       CMD ["python", "-m", "pytest", "--disable-strict-exception-matching=client-name"]
       ```

### Problem: `Fork Validation Issues`

!!! danger "Problem: `Fork-specific test failures`"
    Tests fail for specific Ethereum forks.

=== "Unsupported fork"

    !!! success "Solution: Check fork support"
        ```bash
        # Check which forks client supports
        docker exec <container-id> <client-binary> --help | grep fork
        ```

=== "Incorrect fork configuration"

    !!! success "Solution: Verify fork environment"
        ```bash
        # Verify fork environment variables
        docker exec <container-id> env | grep HIVE_FORK
        ```

=== "Test with supported fork"

    !!! success "Solution: Limit to supported forks"
        ```bash
        # Limit to known supported forks
        uv run consume engine -k "fork_Shanghai or fork_Cancun"
        ```

## Network Issues

### Problem: `Network Connectivity`

!!! danger "Problem: `Network timeout` or `Connection reset`"
    Network issues prevent downloading fixtures or connecting to services.

!!! success "Solution: Resolve network issues"
    1. **Increase network timeout:**
       ```bash
       ./hive --sim.timelimit=30m --sim ethereum/eest/consume-engine
       ```

    2. **Use local fixtures:**
       ```bash
       # Download once and use locally
       wget https://github.com/ethereum/execution-spec-tests/releases/download/v4.1.0/fixtures_develop.tar.gz
       tar -xzf fixtures_develop.tar.gz
       uv run consume engine --input ./fixtures/
       ```

    3. **Configure proxy if needed:**
       ```bash
       export HTTP_PROXY=http://proxy:port
       export HTTPS_PROXY=http://proxy:port
       ```

## Debugging Strategies

### Systematic Debugging Approach

!!! tip "Step-by-step debugging process"
    1. **Start simple:**
       ```bash
       # Test with single client and simple test
       ./hive --sim ethereum/eest/consume-engine \
         --client go-ethereum \
         --sim.limit "id:simple-test-id" \
         --docker.output
       ```

    2. **Increase verbosity:**
       ```bash
       ./hive --sim.loglevel 5 --docker.output --sim ethereum/eest/consume-engine
       ```

    3. **Use development mode:**
       ```bash
       # More interactive debugging
       ./hive --dev --client go-ethereum --docker.output
       export HIVE_SIMULATOR=http://127.0.0.1:3000
       uv run consume engine -k "specific_test" -v -s
       ```

### Log Analysis

!!! info "Important log locations"
    1. **Hive logs:**
       ```bash
       # Main hive output
       ./hive --sim ethereum/eest/consume-engine 2>&1 | tee hive.log
       ```

    2. **Client container logs:**
       ```bash
       # Individual client logs
       docker logs <container-id>
       
       # Follow logs in real-time
       docker logs -f <container-id>
       ```

    3. **EEST consume logs:**
       ```bash
       uv run consume engine -v --eest-log-level=DEBUG
       ```

### Container Inspection

!!! tip "Useful Docker commands for debugging"
    ```bash
    # List all containers
    docker ps -a

    # Inspect container configuration
    docker inspect <container-id>

    # Execute commands in running container
    docker exec -it <container-id> /bin/sh

    # Check network connectivity
    docker exec <container-id> ping host.docker.internal

    # Check file system
    docker exec <container-id> ls -la /genesis.json
    docker exec <container-id> ls -la /blocks/
    ```

## Other Issues Not Listed?

If you're facing an issue that's not listed here, you can easily report it on GitHub for resolution.

[Click here to report a consume-related bug](https://github.com/ethereum/execution-spec-tests/issues/new?title=bug(consume):%20...&labels=scope:consume,type:bug&body=%3Ccopy-paste%20command%20that%20triggered%20the%20issue%20here%3E%0A%3Ccopy-paste%20output%20or%20attach%20screenshot%20here%3E)

Please include the following details in your report:

1. The command that triggered the issue.
2. Any relevant error messages or screenshots.
3. Relevant version information from the output of `uv run eest info`.
