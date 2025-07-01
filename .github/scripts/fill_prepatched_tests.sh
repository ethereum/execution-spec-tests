#!/bin/bash
# Fill pre-patched test sources from before the PR
# Usage: fill_prepatched_tests.sh <modified_deleted_test_files> <base_test_path> <patch_test_path> <block_gas_limit> <fill_until>
# Exit codes:
#   0 - Success
#   1 - Failure to generate tests

set -e

MODIFIED_DELETED_FILES="$1"
BASE_TEST_PATH="$2"
PATCH_TEST_PATH="$3"
BLOCK_GAS_LIMIT="${4:-36000000}"
FILL_UNTIL="${5:-Cancun}"

echo "--------------------"
echo "converted-ethereum-tests.txt seem untouched, try to fill pre-patched version of .py files:"

git checkout main
PREV_COMMIT=$(git rev-parse HEAD)
echo "Checkout head $PREV_COMMIT"

echo "Select files that were changed and exist on the main branch:"
echo "$MODIFIED_DELETED_FILES"

rm -rf fixtures
rm -f filloutput.log

uv run fill $MODIFIED_DELETED_FILES --clean --until=$FILL_UNTIL --evm-bin evmone-t8n --skip-evm-dump --block-gas-limit $BLOCK_GAS_LIMIT -m "state_test or blockchain_test" --output $BASE_TEST_PATH > >(tee -a filloutput.log) 2> >(tee -a filloutput.log >&2)

if grep -q "FAILURES" filloutput.log; then
    echo "Error: failed to generate .py tests from before the PR."
    exit 1
fi

if grep -q "ERROR collecting test session" filloutput.log; then
    echo "Error: failed to generate .py tests from before the PR."
    exit 1
fi

# TODO: Here we can inspect $BASE_TEST_PATH vs $PATCH_TEST_PATH and remove fixtures with the same hash in both directories, to only leave fixtures that have been modified or removed,
#       and then set any_modified_fixtures=false if the fixture set before the PR is empty after this check.
echo "any_modified_fixtures=true" >> "$GITHUB_OUTPUT"
exit 0