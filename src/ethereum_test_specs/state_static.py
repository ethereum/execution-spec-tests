"""Ethereum General State Test filler static test spec parser."""

from functools import cached_property
from typing import Callable, ClassVar, Dict, List

import pytest

from cli.fillerconvert.structures.common import AddressInFiller
from cli.fillerconvert.structures.expect_section import (
    AccountInExpectSection,
)
from cli.fillerconvert.structures.state_test_filler import StateTestInFiller, StateTestVector
from ethereum_test_base_types import Address, Bytes, Hash, HexNumber, Storage, ZeroPaddedHexNumber
from ethereum_test_forks import Fork, get_forks
from ethereum_test_types import Account, Alloc, Environment, Transaction

from .base_static import BaseStaticTest
from .state import StateTestFiller


class StateStaticTest(StateTestInFiller, BaseStaticTest):
    """General State Test static filler from ethereum/tests."""

    test_name: str = ""
    vectors: List[StateTestVector] | None = None
    format_name: ClassVar[str] = "state_test"

    class Config:
        """Model Config."""

        extra = "forbid"

    def model_post_init(self, context):
        """Generate Test Vectors from the test Filler."""
        super().model_post_init(context)
        self.vectors = self.get_test_vectors()

    def fill_function(self) -> Callable:
        """Return a StateTest spec from a static file."""

        @pytest.mark.parametrize(
            "vector",
            self.vectors,
            ids=lambda c: c.id,
        )
        def test_state_vectors(
            state_test: StateTestFiller,
            fork: Fork,
            vector: StateTestVector,
        ):
            return state_test(
                env=vector.env, pre=vector.pre, post=vector.post, tx=vector.tx, fork=vector.fork
            )

        return test_state_vectors

    def get_test_vectors(self) -> List[StateTestVector]:
        """Build test vector data for pyspecs."""
        vectors: List[StateTestVector] = []

        # for each transaction compute test vector
        for d, _ in enumerate(self.transaction.data, start=0):
            for g, _ in enumerate(self.transaction.gas_limit, start=0):
                for v, _ in enumerate(self.transaction.value, start=0):
                    tx_vectors = self._port_transaction_to_vectors(
                        data_index=d, gas_index=g, value_index=v
                    )
                    vectors.extend(tx_vectors)

        return vectors

    def _port_transaction_to_vectors(
        self, data_index: int, gas_index: int, value_index: int
    ) -> List[StateTestVector]:
        """Make test vectors from given transaction index."""
        vectors: List[StateTestVector] = []

        for expect in self.expect:
            if expect.has_index(data_index, gas_index, value_index):
                for fork in expect.network:
                    vector = self._make_vector(
                        fork,
                        self._get_env,
                        self._get_pre,
                        data_index,
                        gas_index,
                        value_index,
                        expect.result,
                        exception=None
                        if expect.expect_exception is None
                        else expect.expect_exception[fork],
                    )
                    vectors.append(vector)
        return vectors

    @cached_property
    def _get_env(self) -> Environment:
        """Parse environment."""
        # Convert Environment data from .json filler into pyspec type
        test_env = self.env
        env = Environment(
            fee_recipient=Address(test_env.current_coinbase),
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
        )
        return env

    @cached_property
    def _get_pre(self) -> Alloc:
        """Parse pre."""
        # Convert pre state data from .json filler into pyspec type
        pre = Alloc()
        for account_address, account in self.pre.items():
            storage: Storage = Storage()
            for key, value in account.storage.items():
                storage[key] = value

            acc_code, acc_code_opt = account.code
            pre[account_address] = Account(
                balance=account.balance,
                nonce=account.nonce,
                code=acc_code,
                storage=storage,
            )
        return pre

    def _make_vector(
        self,
        fork,
        env,
        pre,
        d: int,
        g: int,
        v: int,
        expect_result: Dict[AddressInFiller, AccountInExpectSection],
        exception: str | None,
    ) -> StateTestVector:
        """Compose test vector from test data."""
        general_tr = self.transaction
        data = general_tr.data[d]

        data_code, options = data.data

        tr: Transaction = Transaction(
            data=data_code,
            access_list=data.access_list,
            gas_limit=HexNumber(general_tr.gas_limit[g]),
            value=HexNumber(general_tr.value[v]),
            gas_price=general_tr.gas_price,
            max_fee_per_gas=general_tr.max_fee_per_gas,
            max_priority_fee_per_gas=general_tr.max_priority_fee_per_gas,
            nonce=HexNumber(general_tr.nonce),
            to=Address(general_tr.to),
            secret_key=Hash(general_tr.secret_key),
        )

        post = Alloc()
        for address, account in expect_result.items():
            storage = Storage()
            if account.storage is not None:
                for key, value in account.storage.items():
                    storage[key] = value

            # TODO looks like pyspec post state verification will not work for default values?
            # Because if we require balance to be 0 it must be checked,
            # but if we don't care about the value of the balance how to specify it?
            code = Bytes(b"")
            if account.code is not None:
                code, code_options = account.code

            post[address] = Account(
                balance=account.balance if account.balance is not None else ZeroPaddedHexNumber(0),
                nonce=account.nonce if account.nonce is not None else ZeroPaddedHexNumber(0),
                code=code,
                storage=storage,
            )

        vector_id = f"ported_{self.test_name}_d{d}g{g}v{v}_{fork}"
        all_forks_by_name = {fork.name(): fork for fork in get_forks()}
        print(vector_id)
        vector = StateTestVector(
            id=vector_id,
            env=env,
            pre=pre,
            tx=tr,
            tx_exception=exception,
            post=post,
            fork=all_forks_by_name[fork],
        )
        print(vector.model_dump_json(by_alias=True, exclude_unset=True))
        return vector
