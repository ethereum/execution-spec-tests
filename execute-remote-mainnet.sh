#!/bin/bash

# This script is used to execute the tests on the remote mainnet.

TESTS="tests"
RPC_SEED_KEY="$1"
RPC_URL="$2"
RPC_CHAIN_ID="$3"

uv run execute remote --fork=Prague --dry-run -m mainnet $TESTS --rpc-seed-key $RPC_SEED_KEY --rpc-endpoint $RPC_URL --rpc-chain-id $RPC_CHAIN_ID