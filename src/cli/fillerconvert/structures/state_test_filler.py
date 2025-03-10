"""Ethereum/tests state test Filler structure."""

from typing import Dict, List

from pydantic import BaseModel, Field, RootModel, model_validator

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


class StateTestVector:
    """A data from .json test filler that is required for a state test vector."""

    id: str
    env: Environment
    pre: Alloc
    tx: Transaction
    post: Alloc


class StateTestFiller(RootModel[Dict[str, StateTestInFiller]]):
    """A state test filler file from ethereum/tests."""

    @model_validator(mode="before")
    def check_single_key(cls, values):  # noqa: N805
        """Check that the input is a dictionary with exactly one key."""
        if not isinstance(values, dict) or len(values) != 1:
            raise ValueError("The dictionary must have exactly one key.")
        return values

    def get_test_vectors(self) -> List[StateTestVector]:
        """Build test vector data for pyspecs."""
        vectors: List[StateTestVector] = []
        for test_name, state_test in self.root.items():
            # Convert Environment data from .json filler into pyspec type
            env = Environment()
            env.fee_recipient = Address(state_test.env.current_coinbase)
            env.difficulty = ZeroPaddedHexNumber(state_test.env.current_difficulty)
            env.gas_limit = ZeroPaddedHexNumber(state_test.env.current_gas_limit)
            env.number = ZeroPaddedHexNumber(state_test.env.current_number)
            env.timestamp = ZeroPaddedHexNumber(state_test.env.current_timestamp)

            # Convert pre state data from .json filler into pyspec type
            pre = Alloc()
            for account_address, account in state_test.pre.items():
                storage: Storage = Storage()
                for key, value in account.storage.items():
                    storage[key] = value

                pre[account_address] = Account(
                    balance=account.balance,
                    nonce=account.nonce,
                    code=Bytes.fromhex(account.code[2:]),
                    storage=storage,
                )

            # for each transaction compute test vector
            for d, _ in enumerate(state_test.transaction.data, start=0):
                for g, _ in enumerate(state_test.transaction.gas_limit, start=0):
                    for v, _ in enumerate(state_test.transaction.value, start=0):
                        for expect in state_test.expect:
                            if expect.has_index(d, g, v):
                                for fork in expect.network:
                                    vector = self._make_vector(
                                        test_name,
                                        state_test,
                                        fork,
                                        env,
                                        pre,
                                        d,
                                        g,
                                        v,
                                        expect.result,
                                    )
                                    vectors.append(vector)
        return vectors

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
    ) -> StateTestVector:
        """Compose test vector from test data."""
        vector = StateTestVector()
        vector.env = env
        vector.pre = pre

        tr: Transaction = Transaction()
        data = state_test.transaction.data[d]
        tr.data = Bytes.fromhex(data[2:])
        tr.gas_limit = HexNumber(state_test.transaction.gas_limit[g])
        tr.value = HexNumber(state_test.transaction.value[v])
        tr.gas_price = HexNumber(state_test.transaction.gas_price)
        tr.nonce = HexNumber(state_test.transaction.nonce)
        tr.to = Address(state_test.transaction.to)
        tr.secret_key = Hash(state_test.transaction.secret_key)
        vector.tx = tr

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

        vector.id = f"ported_{test_name}_d{d}g{g}v{v}_{fork}"
        print(vector.id)
        return vector
