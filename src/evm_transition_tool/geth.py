"""
Go-ethereum Transition tool interface.
"""

import binascii
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path
from re import compile
from typing import Dict, Optional

from ethereum_test_base_types import Address, Alloc, ZeroPaddedHexNumber, to_json
from ethereum_test_forks import Fork
from ethereum_test_types.verkle import VerkleTree, WitnessCheck
from ethereum_test_types.verkle.types import Hash as VerkleHash

from .transition_tool import FixtureFormats, TransitionTool, dump_files_to_directory


class GethTransitionTool(TransitionTool):
    """
    Go-ethereum `evm` Transition tool interface wrapper class.
    """

    default_binary = Path("evm")
    detect_binary_pattern = compile(r"^evm(.exe)? version\b")
    t8n_subcommand: Optional[str] = "t8n"
    statetest_subcommand: Optional[str] = "statetest"
    blocktest_subcommand: Optional[str] = "blocktest"
    verkle_subcommand: Optional[str] = "verkle"

    binary: Path
    cached_version: Optional[str] = None
    trace: bool

    def __init__(
        self,
        *,
        binary: Optional[Path] = None,
        trace: bool = False,
    ):
        super().__init__(binary=binary, trace=trace)
        args = [str(self.binary), str(self.t8n_subcommand), "--help"]
        try:
            result = subprocess.run(args, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception("evm process unexpectedly returned a non-zero status code: " f"{e}.")
        except Exception as e:
            raise Exception(f"Unexpected exception calling evm tool: {e}.")
        self.help_string = result.stdout

    def is_fork_supported(self, fork: Fork) -> bool:
        """
        Returns True if the fork is supported by the tool.

        If the fork is a transition fork, we want to check the fork it transitions to.
        """
        return fork.transition_tool_name() in self.help_string

    def get_blocktest_help(self) -> str:
        """
        Return the help string for the blocktest subcommand.
        """
        args = [str(self.binary), "blocktest", "--help"]
        try:
            result = subprocess.run(args, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception("evm process unexpectedly returned a non-zero status code: " f"{e}.")
        except Exception as e:
            raise Exception(f"Unexpected exception calling evm tool: {e}.")
        return result.stdout

    def verify_fixture(
        self,
        fixture_format: FixtureFormats,
        fixture_path: Path,
        fixture_name: Optional[str] = None,
        debug_output_path: Optional[Path] = None,
    ):
        """
        Executes `evm [state|block]test` to verify the fixture at `fixture_path`.
        """
        command: list[str] = [str(self.binary)]

        if debug_output_path:
            command += ["--debug", "--json", "--verbosity", "100"]

        if FixtureFormats.is_state_test(fixture_format):
            assert self.statetest_subcommand, "statetest subcommand not set"
            command.append(self.statetest_subcommand)
        elif FixtureFormats.is_blockchain_test(fixture_format):
            assert self.blocktest_subcommand, "blocktest subcommand not set"
            command.append(self.blocktest_subcommand)
        else:
            raise Exception(f"Invalid test fixture format: {fixture_format}")

        if fixture_name and fixture_format == FixtureFormats.BLOCKCHAIN_TEST:
            assert isinstance(fixture_name, str), "fixture_name must be a string"
            command.append("--run")
            command.append(fixture_name)
        command.append(str(fixture_path))

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if debug_output_path:
            debug_fixture_path = debug_output_path / "fixtures.json"
            # Use the local copy of the fixture in the debug directory
            verify_fixtures_call = " ".join(command[:-1]) + f" {debug_fixture_path}"
            verify_fixtures_script = textwrap.dedent(
                f"""\
                #!/bin/bash
                {verify_fixtures_call}
                """
            )
            dump_files_to_directory(
                str(debug_output_path),
                {
                    "verify_fixtures_args.py": command,
                    "verify_fixtures_returncode.txt": result.returncode,
                    "verify_fixtures_stdout.txt": result.stdout.decode(),
                    "verify_fixtures_stderr.txt": result.stderr.decode(),
                    "verify_fixtures.sh+x": verify_fixtures_script,
                },
            )
            shutil.copyfile(fixture_path, debug_fixture_path)

        if result.returncode != 0:
            raise Exception(
                f"EVM test failed.\n{' '.join(command)}\n\n Error:\n{result.stderr.decode()}"
            )

        if FixtureFormats.is_state_test(fixture_format):
            result_json = json.loads(result.stdout.decode())
            if not isinstance(result_json, list):
                raise Exception(f"Unexpected result from evm statetest: {result_json}")
        else:
            result_json = []  # there is no parseable format for blocktest output
        return result_json

    def _run_verkle_command(self, subcommand: str, *args: str) -> str:
        """
        Helper function to run a verkle subcommand and return the output as a string.
        """
        command = [
            str(self.binary),
            str(self.verkle_subcommand),
            subcommand,
            *args,
        ]
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise Exception(
                f"Failed to run verkle subcommand: '{' '.join(command)}'. "
                f"Error: '{result.stderr.decode()}'"
            )
        return result.stdout.decode().strip()

    def from_mpt_to_vkt(self, mpt_alloc: Alloc) -> VerkleTree:
        """
        Returns the verkle tree representation for an input MPT.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            alloc_path = os.path.join(temp_dir, "alloc.json")
            with open(alloc_path, "w") as f:
                json.dump(to_json(mpt_alloc), f)

            output = self._run_verkle_command("tree-keys", "--input.alloc", alloc_path)
            return VerkleTree(json.loads(output))

    def get_verkle_state_root(self, mpt_alloc: Alloc) -> bytes:
        """
        Returns the VKT state root from an input MPT.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            alloc_path = os.path.join(temp_dir, "alloc.json")
            with open(alloc_path, "w") as f:
                json.dump(to_json(mpt_alloc), f)

            hex_string = self._run_verkle_command("state-root", "--input.alloc", alloc_path)
            return binascii.unhexlify(hex_string[2:])

    def get_verkle_single_key(
        self, address: Address, storage_slot: Optional[ZeroPaddedHexNumber] = None
    ) -> str:
        """
        Returns the VKT key for an account address or storage slot.
        """
        args = [str(address)]
        if storage_slot is not None:
            args.append(str(storage_slot))
        output = self._run_verkle_command("single-key", *args)
        return output

    def get_verkle_code_chunk_key(self, address: Address, code_chunk: ZeroPaddedHexNumber) -> str:
        """
        Returns the VKT key of a code chunk for an account address.
        """
        output = self._run_verkle_command("code-chunk-key", str(address), str(code_chunk))
        return output

    def format_witness_check(
        self, witness_check: WitnessCheck
    ) -> Dict[VerkleHash, VerkleHash | None]:
        """
        Returns the formatted witness check as a key value dictionary
        """
        witness_check_key_values: Dict[VerkleHash, VerkleHash | None] = {}

        # Format account entries using `evm verkle single-key`
        if witness_check.account_entries:
            for address, entry, value in witness_check.account_entries:
                tree_key_str = self.get_verkle_single_key(address)
                tree_key = bytearray.fromhex(tree_key_str[2:])
                entry_bytes = entry.value.to_bytes(2, byteorder="big")
                tree_key[-2:] = entry_bytes
                witness_check_key_values[VerkleHash(bytes(tree_key))] = value

        # Format storage entries using `evm verkle single-key`
        if witness_check.storage_slots:
            for address, storage_slot, value in witness_check.storage_slots:
                storage_tree_key = self.get_verkle_single_key(
                    address, ZeroPaddedHexNumber(storage_slot)
                )
                witness_check_key_values[VerkleHash(storage_tree_key)] = value

        # Format code chunks using `evm verkle code-chunk-key`
        if witness_check.code_chunks:
            for address, code_chunk, value in witness_check.code_chunks:
                code_chunk_tree_key = self.get_verkle_code_chunk_key(
                    address, ZeroPaddedHexNumber(code_chunk)
                )
                witness_check_key_values[VerkleHash(code_chunk_tree_key)] = value

        return witness_check_key_values
