"""Ethereum/tests state test Filler structure."""

import json
from functools import cached_property
from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from ethereum_test_base_types import Address, Bytes, Hash, HexNumber, Storage, ZeroPaddedHexNumber
from ethereum_test_types import Account, Alloc, Environment, Transaction

from .account import AccountInFiller
from .common import AddressInFiller
from .environment import EnvironmentInStateTestFiller
from .expect_section import AccountInExpectSection, ExpectSectionInStateTestFiller
from .general_transaction import GeneralTransactionInFiller

# ConfigDict
# CAMEL_CASE_CONFIG = ConfigDict(
#    alias_generator=to_camel,
#    populate_by_name=True,
#    from_attributes=True,
#    extra="forbid",
# )


class Info(BaseModel):
    """Class that represents an info filler."""

    comment: str


class StateTestInFiller(BaseModel):
    """A single test in state test filler."""

    info: Info | None = Field(None, alias="_info")
    env: EnvironmentInStateTestFiller
    pre: Dict[AddressInFiller, AccountInFiller]
    transaction: GeneralTransactionInFiller
    expect: List[ExpectSectionInStateTestFiller]

    class Config:
        """Model Config."""

        extra = "forbid"

    @model_validator(mode="after")
    @classmethod
    def match_labels(cls, model: "StateTestInFiller") -> "StateTestInFiller":
        """Replace labels in expect section with corresponding tx.d indexes."""
        for expect_section in model.expect:
            indexes_data = expect_section.indexes.data
            if isinstance(indexes_data, str):
                indexes_data = indexes_data.replace(":label ", "")
                tx_matches: List[int] = []
                for idx, d in enumerate(model.transaction.data):
                    code, opt = d.data
                    if indexes_data == opt.label:
                        tx_matches.append(idx)

                expect_section.indexes.data = tx_matches
        return model


class StateTestVector(BaseModel):
    """A data from .json test filler that is required for a state test vector."""

    id: str
    env: Environment
    pre: Alloc
    tx: Transaction
    tx_exception: str | None
    post: Alloc


def remove_comments(d: dict) -> dict:
    """Remove comments from a dictionary."""
    result = {}
    for k, v in d.items():
        if isinstance(k, str) and k.startswith("//"):
            continue
        if isinstance(v, dict):
            v = remove_comments(v)
        elif isinstance(v, list):
            v = [remove_comments(i) if isinstance(i, dict) else i for i in v]
        result[k] = v
    return result


class StateFiller(BaseModel):
    """Class that represents a state test filler."""

    tests: Dict[str, StateTestInFiller]

    @field_validator("tests", mode="before")
    def check_single_key(cls, v):  # noqa: N805
        """Filler must have one dict element."""
        if not isinstance(v, dict) or len(v) != 1:
            raise ValueError("The 'tests' dictionary must have exactly one key.")
        return v

    @classmethod
    def from_json(cls, path: Path) -> "StateFiller":
        """Read the state filler from a JSON file."""
        with open(path, "r") as f:
            o = json.load(f)
            filler = StateFiller(tests=remove_comments(o))
            filler.get_test_vectors()
            return filler

    @classmethod
    def from_yml(cls, path: Path) -> "StateFiller":
        """Read the state filler from a YML file."""
        with open(path, "r") as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            filler = StateFiller(tests=remove_comments(o))
            filler.get_test_vectors()
            return filler

    def get_test_vectors(self) -> List[StateTestVector]:
        """Build test vector data for pyspecs."""
        vectors: List[StateTestVector] = []

        # State Test Filler always have only one test object
        test_name, state_test = list(self.tests.items())[0]

        # for each transaction compute test vector
        for d, _ in enumerate(state_test.transaction.data, start=0):
            for g, _ in enumerate(state_test.transaction.gas_limit, start=0):
                for v, _ in enumerate(state_test.transaction.value, start=0):
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

        # State Test Filler always have only one test object
        test_name, state_test = list(self.tests.items())[0]

        for expect in state_test.expect:
            if expect.has_index(data_index, gas_index, value_index):
                for fork in expect.network:
                    vector = self._make_vector(
                        test_name,
                        state_test,
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
        test_name, state_test = list(self.tests.items())[0]

        # Convert Environment data from .json filler into pyspec type
        env = Environment()
        env.fee_recipient = Address(state_test.env.current_coinbase)
        env.difficulty = ZeroPaddedHexNumber(state_test.env.current_difficulty)
        env.gas_limit = ZeroPaddedHexNumber(state_test.env.current_gas_limit)
        env.number = ZeroPaddedHexNumber(state_test.env.current_number)
        env.timestamp = ZeroPaddedHexNumber(state_test.env.current_timestamp)
        return env

    @cached_property
    def _get_pre(self) -> Alloc:
        """Parse pre."""
        test_name, state_test = list(self.tests.items())[0]
        # Convert pre state data from .json filler into pyspec type
        pre = Alloc()
        for account_address, account in state_test.pre.items():
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
        test_name,
        state_test: StateTestInFiller,
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
        general_tr = state_test.transaction
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
            post[address] = Account(
                balance=account.balance if account.balance is not None else ZeroPaddedHexNumber(0),
                nonce=account.nonce if account.nonce is not None else ZeroPaddedHexNumber(0),
                code=account.code if account.code is not None else Bytes(b""),
                storage=storage,
            )

        vector_id = f"ported_{test_name}_d{d}g{g}v{v}_{fork}"
        print(vector_id)
        vector = StateTestVector(
            id=vector_id, env=env, pre=pre, tx=tr, tx_exception=exception, post=post
        )
        print(vector.model_dump_json(by_alias=True, exclude_unset=True))
        return vector
