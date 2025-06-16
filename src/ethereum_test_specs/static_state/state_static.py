"""Ethereum General State Test filler static test spec parser."""

import re
from copy import deepcopy
from hashlib import sha256
from itertools import count
from typing import Any, Callable, ClassVar, Dict, Iterator, List, Tuple

import pytest
from _pytest.mark.structures import ParameterSet

from ethereum_test_base_types import (
    Account,
    Address,
    Hash,
    HexNumber,
    Storage,
    ZeroPaddedHexNumber,
)
from ethereum_test_exceptions import TransactionExceptionInstanceOrList
from ethereum_test_forks import Fork
from ethereum_test_types import EOA, Alloc, Environment, Transaction
from ethereum_test_types import Alloc as BaseAlloc
from pytest_plugins.filler.pre_alloc import Alloc as FillerAlloc
from pytest_plugins.filler.pre_alloc import AllocMode

from ..base_static import BaseStaticTest
from ..state import StateTestFiller
from .common import (
    AddressOrTagInFiller,
    AddressTag,
    parse_address_or_tag,
)
from .expect_section import (
    AccountInExpectSection,
)
from .state_test_filler import (
    StateTestInFiller,
    StateTestVector,
)

CONTRACT_ADDRESS_INCREMENTS_DEFAULT = 0x100


class StateStaticTest(StateTestInFiller, BaseStaticTest):
    """General State Test static filler from ethereum/tests."""

    test_name: str = ""
    vectors: List[StateTestVector] | None = None
    format_name: ClassVar[str] = "state_test"

    _alloc_registry: Dict[str, BaseAlloc] = {}
    _tag_to_address_map: Dict[str, Dict[str, Address]] = {}
    _tag_to_eoa_map: Dict[str, Dict[str, EOA]] = {}
    _request: pytest.FixtureRequest | None = None

    def model_post_init(self, context):
        """Initialize StateStaticTest."""
        super().model_post_init(context)

    def _get_alloc_for_test(self, test_id: str, fork: Fork) -> BaseAlloc:
        """Get or create an Alloc instance for this test using same logic as Python tests."""
        # TODO: [DRY] We should think of a good way to share this code if we can so if
        #  the logic changes, we can update it in one place.

        # Use test_id directly - each test variation gets unique addresses
        if test_id not in self._alloc_registry:
            test_hash = int.from_bytes(sha256(test_id.encode("utf-8")).digest(), "big")

            def contract_address_iterator() -> Iterator[Address]:
                return iter(
                    Address((test_hash + (i * CONTRACT_ADDRESS_INCREMENTS_DEFAULT)) % 2**160)
                    for i in count()
                )

            def eoa_iterator() -> Iterator[EOA]:
                return iter(
                    EOA(
                        key=(test_hash + i)
                        % 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
                        nonce=0,
                    )
                    for i in count()
                )

            self._alloc_registry[test_id] = FillerAlloc(
                alloc_mode=AllocMode.PERMISSIVE,
                contract_address_iterator=contract_address_iterator(),
                eoa_iterator=eoa_iterator(),
            )
            self._tag_to_address_map[test_id] = {}
            self._tag_to_eoa_map[test_id] = {}

        return self._alloc_registry[test_id]

    def _resolve_address_or_tag(self, value: Any, test_id: str, fork: Fork) -> Any:
        """Resolve address tag strings to Address, pass through other values."""
        if isinstance(value, str):
            parsed = parse_address_or_tag(value)
            if isinstance(parsed, AddressTag):
                alloc = self._get_alloc_for_test(test_id, fork)

                # Check if we've already resolved this tag
                if parsed.original_string in self._tag_to_address_map.get(test_id, {}):
                    return self._tag_to_address_map[test_id][parsed.original_string]

                # Generate new address based on tag type
                if parsed.tag_type == "contract":
                    # Use deploy_contract to get next contract address
                    # We'll deploy with empty code for now, just to reserve the address
                    if parsed.tag_name == "sender":
                        eoa = alloc.fund_eoa(amount=0)
                        self._tag_to_address_map[test_id][parsed.original_string] = Address(eoa)
                        self._tag_to_eoa_map[test_id][parsed.original_string] = eoa
                        return Address(eoa)
                    else:
                        address = alloc.deploy_contract(code=b"")
                        self._tag_to_address_map[test_id][parsed.original_string] = address
                        return address
                elif parsed.tag_type == "eoa":
                    # Use fund_eoa to get next EOA
                    eoa = alloc.fund_eoa(amount=0)  # Don't fund yet, just get the address
                    self._tag_to_address_map[test_id][parsed.original_string] = Address(eoa)
                    self._tag_to_eoa_map[test_id][parsed.original_string] = eoa
                    return Address(eoa)
                else:
                    raise ValueError(f"Unknown tag type: {parsed.tag_type}")
            else:
                return parsed
        return value

    def _resolve_tags_in_code(self, code_str: str, test_id: str, fork: Fork) -> str:
        """Resolve address tags in code strings before compilation."""
        tag_pattern = r"<(eoa|contract):[^>]+>"

        def replace_tag(match):
            tag_str = match.group(0)
            parsed = parse_address_or_tag(tag_str)
            if isinstance(parsed, AddressTag):
                address = self._resolve_address_or_tag(tag_str, test_id, fork)
                start_pos = match.start()
                preceeding_2chars = code_str[start_pos - 2 : start_pos]
                if not (
                    preceeding_2chars == "0x" or any(kw in preceeding_2chars for kw in [" ", "("])
                ):
                    # - If the tag is not preceded by 0x, we're inside a hex string
                    # - If the tag is preceded by a space, we'd need the 0x prefix
                    # return the address without the 0x prefix
                    return str(address)[2:]
                return str(address)
            return tag_str

        # Replace all tags in the code string
        return re.sub(tag_pattern, replace_tag, code_str)

    def fill_function(self) -> Callable:
        """Return a StateTest spec from a static file."""
        d_g_v_parameters: List[ParameterSet] = []
        for d in range(len(self.transaction.data)):
            for g in range(len(self.transaction.gas_limit)):
                for v in range(len(self.transaction.value)):
                    exception_test = False
                    for expect in self.expect:
                        if expect.has_index(d, g, v) and expect.expect_exception is not None:
                            exception_test = True
                    # TODO: This does not take into account exceptions that only happen on
                    #       specific forks, but this requires a covariant parametrize
                    marks = [pytest.mark.exception_test] if exception_test else []
                    d_g_v_parameters.append(
                        pytest.param(d, g, v, marks=marks, id=f"d{d}-g{g}-v{v}")
                    )

        @pytest.mark.valid_at(*self.get_valid_at_forks())
        @pytest.mark.parametrize("d,g,v", d_g_v_parameters)
        def test_state_vectors(
            state_test: StateTestFiller,
            fork: Fork,
            d: int,
            g: int,
            v: int,
            request: pytest.FixtureRequest,
        ):
            for expect in self.expect:
                if expect.has_index(d, g, v):
                    if fork.name() in expect.network:
                        test_id = request.node.nodeid
                        # Store request for use in other methods
                        self._request = request
                        # Process pre state first to populate caches
                        pre = self._get_pre(test_id, fork)
                        env = self._get_env(test_id, fork)

                        # Now create the vector with populated caches
                        post, tx = self._make_vector(
                            d,
                            g,
                            v,
                            expect.result,
                            test_id,
                            fork,
                            exception=None
                            if expect.expect_exception is None
                            else expect.expect_exception[fork.name()],
                        )
                        return state_test(
                            env=env,
                            pre=pre,
                            post=post,
                            tx=tx,
                        )
            pytest.fail(f"Expectation not found for d={d}, g={g}, v={v}, fork={fork}")

        if self.info and self.info.pytest_marks:
            for mark in self.info.pytest_marks:
                apply_mark = getattr(pytest.mark, mark)
                test_state_vectors = apply_mark(test_state_vectors)

        return test_state_vectors

    def get_valid_at_forks(self) -> List[str]:
        """Return list of forks that are valid for this test."""
        fork_list: List[str] = []
        for expect in self.expect:
            for fork in expect.network:
                if fork not in fork_list:
                    fork_list.append(fork)
        return fork_list

    def _get_env(self, test_id: str, fork: Fork) -> Environment:
        """Parse environment."""
        # Convert Environment data from .json filler into pyspec type
        test_env = self.env
        resolved_coinbase = self._resolve_address_or_tag(test_env.current_coinbase, test_id, fork)
        env = Environment(
            fee_recipient=Address(resolved_coinbase),
            difficulty=ZeroPaddedHexNumber(test_env.current_difficulty)
            if test_env.current_difficulty is not None
            else None,
            prev_randao=ZeroPaddedHexNumber(test_env.current_random)
            if test_env.current_random is not None
            else None,
            gas_limit=ZeroPaddedHexNumber(test_env.current_gas_limit),
            number=ZeroPaddedHexNumber(test_env.current_number),
            timestamp=ZeroPaddedHexNumber(test_env.current_timestamp),
            base_fee_per_gas=ZeroPaddedHexNumber(test_env.current_base_fee)
            if test_env.current_base_fee is not None
            else None,
            excess_blob_gas=ZeroPaddedHexNumber(test_env.current_excess_blob_gas)
            if test_env.current_excess_blob_gas is not None
            else None,
        )
        return env

    def _get_pre(self, test_id: str, fork: Fork) -> Alloc:
        """Parse pre."""
        # Get the Alloc instance with proper iterators
        self._get_alloc_for_test(test_id, fork)

        # First pass: resolve all tags and determine which are contracts vs EOAs
        for account_address, _account in self.pre.items():
            parsed = parse_address_or_tag(account_address)
            if isinstance(parsed, AddressTag):
                # Pre-populate our caches by resolving the tag
                self._resolve_address_or_tag(account_address, test_id, fork)

        # Second pass: populate the pre-allocation
        pre = Alloc()
        for account_address, account in self.pre.items():
            # Resolve address tags to actual addresses
            resolved_address = self._resolve_address_or_tag(account_address, test_id, fork)

            storage: Storage = Storage()
            for key, value in account.storage.items():
                # Resolve address tags in storage keys and values
                resolved_key = self._resolve_address_or_tag(key, test_id, fork)
                resolved_value = self._resolve_address_or_tag(value, test_id, fork)
                storage[resolved_key] = resolved_value

            # Resolve tags in code before compilation
            code_bytes = b""
            if account.code is not None:
                # Create a copy of the code to avoid modifying the original
                code_copy = deepcopy(account.code)
                # Resolve any tags in the code string
                code_copy.code_raw = self._resolve_tags_in_code(code_copy.code_raw, test_id, fork)
                code_bytes = code_copy.compiled

            pre[resolved_address] = Account(
                balance=account.balance,
                nonce=account.nonce,
                code=code_bytes,
                storage=storage,
            )
        return pre

    def _make_vector(
        self,
        d: int,
        g: int,
        v: int,
        expect_result: Dict[AddressOrTagInFiller, AccountInExpectSection],
        test_id: str,
        fork: Fork,
        exception: TransactionExceptionInstanceOrList | None,
    ) -> Tuple[Alloc, Transaction]:
        """Compose test vector from test data."""
        general_tr = self.transaction
        data_box = general_tr.data[d]

        # Resolve transaction 'to' address if it's a tag
        resolved_to = None
        if general_tr.to is not None:
            resolved_to_addr = self._resolve_address_or_tag(general_tr.to, test_id, fork)
            resolved_to = Address(resolved_to_addr)

        # For static tests, there's only one sender EOA
        # Look for any EOA tag in the pre state - that's our sender
        sender_eoa = None
        # Get the same registry key logic as _get_alloc_for_test
        for addr_str in self.pre.keys():
            parsed = parse_address_or_tag(addr_str)
            if isinstance(parsed, AddressTag) and parsed.tag_name == "sender":
                # Found the sender EOA - get it from our registry
                if parsed.original_string in self._tag_to_eoa_map.get(test_id, {}):
                    sender_eoa = self._tag_to_eoa_map[test_id][parsed.original_string]
                    break

        if sender_eoa and sender_eoa.key is not None:
            # Use sender_eos's key as the secret key for the transaction
            secret_key_to_use = sender_eoa.key
        else:
            if isinstance(general_tr.secret_key, str) and general_tr.secret_key.startswith(
                "<sender:key:"
            ):
                # Perhaps this is a test that is trying to test non-existing accounts,
                # use a generated EOA's key anyhow, funded as `0` (since not in pre state)
                sender_eoa = self._get_alloc_for_test(test_id, fork).fund_eoa(amount=0)
                if sender_eoa.key is not None:
                    secret_key_to_use = sender_eoa.key
                else:
                    raise ValueError(f"Sender EOA has no key: {sender_eoa}")
            else:
                # This is a test that has not been converted to use tagging either
                # because it needs hard-coded addresses or because of some other reason.
                # Use the secret key directly from the transaction.
                secret_key_to_use = Hash(general_tr.secret_key)

        # Resolve tags in transaction data before compilation
        data_copy = deepcopy(data_box.data)
        data_copy.code_raw = self._resolve_tags_in_code(data_copy.code_raw, test_id, fork)

        # Resolve tags in access list
        resolved_access_list = None
        if data_box.access_list is not None:
            from ethereum_test_base_types import AccessList as BaseAccessList

            resolved_access_list = []
            for access_entry in data_box.access_list:
                # Resolve the address if it's a tag
                resolved_address = self._resolve_address_or_tag(
                    access_entry.address, test_id, fork
                )
                resolved_access_list.append(
                    BaseAccessList(
                        address=Address(resolved_address), storage_keys=access_entry.storage_keys
                    )
                )

        tr: Transaction = Transaction(
            data=data_copy.compiled,
            access_list=resolved_access_list,
            gas_limit=HexNumber(general_tr.gas_limit[g]),
            value=HexNumber(general_tr.value[v]),
            gas_price=general_tr.gas_price,
            max_fee_per_gas=general_tr.max_fee_per_gas,
            max_priority_fee_per_gas=general_tr.max_priority_fee_per_gas,
            max_fee_per_blob_gas=general_tr.max_fee_per_blob_gas,
            blob_versioned_hashes=general_tr.blob_versioned_hashes,
            nonce=HexNumber(general_tr.nonce),
            to=resolved_to,
            secret_key=secret_key_to_use,
            error=exception,
        )

        post = Alloc()
        for address, account in expect_result.items():
            # Resolve address tags to actual addresses
            resolved_address = self._resolve_address_or_tag(address, test_id, fork)

            if account.expected_to_not_exist is not None:
                post[resolved_address] = Account.NONEXISTENT
                continue

            account_kwargs: Dict[str, Any] = {}
            if account.storage is not None:
                storage = Storage()
                for key, value in account.storage.items():
                    # Resolve address tags in storage keys
                    resolved_key = self._resolve_address_or_tag(key, test_id, fork)
                    if value != "ANY":
                        # Resolve address tags in storage values
                        resolved_value = self._resolve_address_or_tag(value, test_id, fork)
                        storage[resolved_key] = resolved_value
                    else:
                        storage.set_expect_any(resolved_key)
                account_kwargs["storage"] = storage
            if account.code is not None:
                # Create a copy of the code to avoid modifying the original
                code_copy = deepcopy(account.code)
                # Resolve tags in code before compilation
                code_copy.code_raw = self._resolve_tags_in_code(code_copy.code_raw, test_id, fork)
                account_kwargs["code"] = code_copy.compiled
            if account.balance is not None:
                account_kwargs["balance"] = account.balance
            if account.nonce is not None:
                account_kwargs["nonce"] = account.nonce

            post[resolved_address] = Account(**account_kwargs)

        return post, tr
