"""
Useful types for generating Ethereum tests.
"""

from dataclasses import dataclass
from itertools import count
from typing import Any, ClassVar, Dict, Iterator, List, Sequence, SupportsBytes, Type, TypeAlias

from coincurve.keys import PrivateKey, PublicKey
from ethereum import rlp as eth_rlp
from ethereum.base_types import U256, Uint
from ethereum.crypto.hash import keccak256
from ethereum.frontier.fork_types import Account as FrontierAccount
from ethereum.frontier.fork_types import Address as FrontierAddress
from ethereum.frontier.state import State, set_account, set_storage, state_root
from pydantic import (
    AliasGenerator,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    TypeAdapter,
    computed_field,
)
from pydantic.alias_generators import to_camel
from trie import HexaryTrie

from ethereum_test_forks import Fork

from ..exceptions import ExceptionList, TransactionException
from .base_types import (
    AddressType,
    BloomType,
    HashType,
    HexBytesType,
    HexNumberType,
    from_hash,
    to_hex_number,
)
from .constants import TestPrivateKey
from .conversions import BytesConvertible


# Sentinel classes
class Removable:
    """
    Sentinel class to detect if a parameter should be removed.
    (`None` normally means "do not modify")
    """

    pass


class Auto:
    """
    Class to use as a sentinel value for parameters that should be
    automatically calculated.
    """

    def __repr__(self) -> str:
        """Print the correct test id."""
        return "auto"


# Base Models


class CamelModel(BaseModel):
    """
    Model that uses camel case
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class SerializationCamelModel(BaseModel):
    """
    Model that uses camel case for serialization
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        populate_by_name=True,
    )


MAX_STORAGE_KEY_VALUE = 2**256 - 1
MIN_STORAGE_KEY_VALUE = -(2**255)


StorageKeyValueType = HexNumberType
StorageKeyValueTypeAdapter = TypeAdapter(StorageKeyValueType)
StorageType = Dict[StorageKeyValueType, StorageKeyValueType]


class Storage(RootModel[Dict[StorageKeyValueType, StorageKeyValueType]]):
    """
    Definition of a storage in pre or post state of a test
    """

    root: Dict[StorageKeyValueType, StorageKeyValueType]

    _current_slot: Iterator[StorageKeyValueType] = count(0)

    StorageDictType: ClassVar[TypeAlias] = Dict[
        str | int | bytes | SupportsBytes, str | int | bytes | SupportsBytes
    ]
    """
    Dictionary type to be used when defining an input to initialize a storage.
    """

    @dataclass(kw_only=True)
    class InvalidType(Exception):
        """
        Invalid type used when describing test's expected storage key or value.
        """

        key_or_value: Any

        def __init__(self, key_or_value: Any, *args):
            super().__init__(args)
            self.key_or_value = key_or_value

        def __str__(self):
            """Print exception string"""
            return f"invalid type for key/value: {self.key_or_value}"

    @dataclass(kw_only=True)
    class InvalidValue(Exception):
        """
        Invalid value used when describing test's expected storage key or
        value.
        """

        key_or_value: Any

        def __init__(self, key_or_value: Any, *args):
            super().__init__(args)
            self.key_or_value = key_or_value

        def __str__(self):
            """Print exception string"""
            return f"invalid value for key/value: {self.key_or_value}"

    @dataclass(kw_only=True)
    class AmbiguousKeyValue(Exception):
        """
        Key is represented twice in the storage.
        """

        key_1: str | int
        val_1: str | int
        key_2: str | int
        val_2: str | int

        def __init__(
            self,
            key_1: str | int,
            val_1: str | int,
            key_2: str | int,
            val_2: str | int,
            *args,
        ):
            super().__init__(args)
            self.key_1 = key_1
            self.val_1 = val_1
            self.key_2 = key_2
            self.val_2 = val_2

        def __str__(self):
            """Print exception string"""
            return f"""
            Key is represented twice (due to negative numbers) with different
            values in storage:
            s[{self.key_1}] = {self.val_1} and s[{self.key_2}] = {self.val_2}
            """

    @dataclass(kw_only=True)
    class MissingKey(Exception):
        """
        Test expected to find a storage key set but key was missing.
        """

        key: int

        def __init__(self, key: int, *args):
            super().__init__(args)
            self.key = key

        def __str__(self):
            """Print exception string"""
            return "key {0} not found in storage".format(Storage.key_value_to_string(self.key))

    @dataclass(kw_only=True)
    class KeyValueMismatch(Exception):
        """
        Test expected a certain value in a storage key but value found
        was different.
        """

        address: AddressType
        key: int
        want: int
        got: int

        def __init__(self, address: AddressType, key: int, want: int, got: int, *args):
            super().__init__(args)
            self.address = address
            self.key = key
            self.want = want
            self.got = got

        def __str__(self):
            """Print exception string"""
            return (
                f"incorrect value in address {self.address} for "
                + f"key {Storage.key_value_to_string(self.key)}:"
                + f" want {Storage.key_value_to_string(self.want)} (dec:{self.want}),"
                + f" got {Storage.key_value_to_string(self.got)} (dec:{self.got})"
            )

    def __contains__(self, key: StorageKeyValueType) -> bool:
        """Checks for an item in the storage"""
        return key in self.root

    def __getitem__(self, key: StorageKeyValueType) -> StorageKeyValueType:
        """Returns an item from the storage"""
        return self.root[key]

    def __setitem__(self, key: StorageKeyValueType, value: StorageKeyValueType):  # noqa: SC200
        """Sets an item in the storage"""
        self.root[key] = StorageKeyValueTypeAdapter.validate_python(value)

    def __delitem__(self, key: StorageKeyValueType):
        """Deletes an item from the storage"""
        del self.root[key]

    def keys(self) -> set[StorageKeyValueType]:
        """Returns the keys of the storage"""
        return set(self.root.keys())

    def store_next(self, value: StorageKeyValueType) -> StorageKeyValueType:
        """
        Stores a value in the storage and returns the key where the value is stored.

        Increments the key counter so the next time this function is called,
        the next key is used.
        """
        self[slot := next(self._current_slot)] = StorageKeyValueTypeAdapter.validate_python(value)
        return slot

    def contains(self, other: "Storage") -> bool:
        """
        Returns True if self contains all keys with equal value as
        contained by second storage.
        Used for comparison with test expected post state and alloc returned
        by the transition tool.
        """
        for key in other.keys():
            if key not in self:
                return False
            if self[key] != other[key]:
                return False
        return True

    def must_contain(self, address: AddressType, other: "Storage"):
        """
        Succeeds only if self contains all keys with equal value as
        contained by second storage.
        Used for comparison with test expected post state and alloc returned
        by the transition tool.
        Raises detailed exception when a difference is found.
        """
        for key in other.keys():
            if key not in self:
                # storage[key]==0 is equal to missing storage
                if other[key] != 0:
                    raise Storage.MissingKey(key=key)
            elif self[key] != other[key]:
                raise Storage.KeyValueMismatch(
                    address=address, key=key, want=self[key], got=other[key]
                )

    def must_be_equal(self, address: AddressType, other: "Storage | None"):
        """
        Succeeds only if "self" is equal to "other" storage.
        """
        # Test keys contained in both storage objects
        if other is None:
            other = Storage({})
        for key in self.keys() & other.keys():
            if self[key] != other[key]:
                raise Storage.KeyValueMismatch(
                    address=address, key=key, want=self[key], got=other[key]
                )

        # Test keys contained in either one of the storage objects
        for key in self.keys() ^ other.keys():
            if key in self:
                if self[key] != 0:
                    raise Storage.KeyValueMismatch(address=address, key=key, want=self[key], got=0)

            elif other[key] != 0:
                raise Storage.KeyValueMismatch(address=address, key=key, want=0, got=other[key])


class Account(BaseModel):
    """
    State associated with an address.
    """

    nonce: HexNumberType | None = None
    """
    The scalar value equal to a) the number of transactions sent by
    an Externally Owned Account, b) the amount of contracts created by a
    contract.
    """
    balance: HexNumberType | None = None
    """
    The amount of Wei (10<sup>-18</sup> Eth) the account has.
    """
    code: HexBytesType | None = None
    """
    Bytecode contained by the account.
    """
    storage: Storage | None = None
    """
    Storage within a contract.
    """

    NONEXISTENT: ClassVar[object] = object()
    """
    Sentinel object used to specify when an account should not exist in the
    state.
    """

    @dataclass(kw_only=True)
    class NonceMismatch(Exception):
        """
        Test expected a certain nonce value for an account but a different
        value was found.
        """

        address: AddressType
        want: int | None
        got: int | None

        def __init__(self, address: AddressType, want: int | None, got: int | None, *args):
            super().__init__(args)
            self.address = address
            self.want = want
            self.got = got

        def __str__(self):
            """Print exception string"""
            return (
                f"unexpected nonce for account {self.address}: "
                + f"want {self.want}, got {self.got}"
            )

    @dataclass(kw_only=True)
    class BalanceMismatch(Exception):
        """
        Test expected a certain balance for an account but a different
        value was found.
        """

        address: AddressType
        want: int | None
        got: int | None

        def __init__(self, address: AddressType, want: int | None, got: int | None, *args):
            super().__init__(args)
            self.address = address
            self.want = want
            self.got = got

        def __str__(self):
            """Print exception string"""
            return (
                f"unexpected balance for account {self.address}: "
                + f"want {self.want}, got {self.got}"
            )

    @dataclass(kw_only=True)
    class CodeMismatch(Exception):
        """
        Test expected a certain bytecode for an account but a different
        one was found.
        """

        address: AddressType
        want: bytes | None
        got: bytes | None

        def __init__(self, address: AddressType, want: bytes | None, got: bytes | None, *args):
            super().__init__(args)
            self.address = address
            self.want = want
            self.got = got

        def __str__(self):
            """Print exception string"""
            return (
                f"unexpected code for account {self.address}: "
                + f"want {self.want}, got {self.got}"
            )

    def check_alloc(self: "Account", address: AddressType, account: "Account"):
        """
        Checks the returned alloc against an expected account in post state.
        Raises exception on failure.
        """
        if self.nonce is not None:
            if self.nonce != account.nonce:
                raise Account.NonceMismatch(
                    address=address,
                    want=self.nonce,
                    got=account.nonce,
                )

        if self.balance is not None:
            if self.balance != account.balance:
                raise Account.BalanceMismatch(
                    address=address,
                    want=self.balance,
                    got=account.balance,
                )

        if self.code is not None:
            if self.code != account.code:
                raise Account.CodeMismatch(
                    address=address,
                    want=self.code,
                    got=account.code,
                )

        if self.storage is not None:
            self.storage.must_be_equal(address=address, other=account.storage)

    def has_empty_code(self: "Account") -> bool:
        """
        Returns true if an account has no bytecode.
        """
        return not self.code or self.code == b""

    def is_empty(self: "Account") -> bool:
        """
        Returns true if an account deemed empty.
        """
        return (
            (self.nonce == 0 or self.nonce is None)
            and (self.balance == 0 or self.balance is None)
            and self.has_empty_code()
            and (not self.storage or self.storage == {} or self.storage is None)
        )

    @classmethod
    def with_code(cls: Type, code: BytesConvertible) -> "Account":
        """
        Create account with provided `code` and nonce of `1`.
        """
        return Account(nonce=1, code=code)

    @classmethod
    def merge(
        cls: Type, account_1: "Dict | Account | None", account_2: "Dict | Account | None"
    ) -> "Account":
        """
        Create a merged account from two sources.
        """

        def to_kwargs_dict(account: "Dict | Account | None") -> Dict:
            if account is None:
                return {}
            if isinstance(account, dict):
                return account
            elif isinstance(account, cls):
                return account.model_dump()
            raise TypeError(f"Unexpected type for account merge: {type(account)}")

        kwargs = to_kwargs_dict(account_1)
        kwargs.update(to_kwargs_dict(account_2))

        return cls(**kwargs)


class Alloc(RootModel[Dict[AddressType, Account]]):
    """
    Allocation of accounts in the state, pre and post test execution.
    """

    root: Dict[AddressType, Account]

    @classmethod
    def merge(cls, alloc_1: "Alloc", alloc_2: "Alloc") -> "Alloc":
        """
        Returns the merged allocation of two sources.
        """
        merged = alloc_1.model_dump()

        for address, other_account in alloc_2.root.items():
            merged_account = Account.merge(merged.get(address, None), other_account)
            if merged_account.is_empty():
                if address in merged:
                    merged.pop(address, None)
            else:
                merged[address] = merged_account

        return Alloc(merged)

    def empty_accounts(self) -> List[AddressType]:
        """
        Returns a list of addresses of empty accounts.
        """
        return [address for address, account in self.root.items() if account.is_empty()]

    def state_root(self) -> bytes:
        """
        Returns the state root of the allocation.
        """
        state = State()
        for address, account in self.root.items():
            set_account(
                state=state,
                address=FrontierAddress(address),
                account=FrontierAccount(
                    nonce=Uint(account.nonce) if account.nonce is not None else Uint(0),
                    balance=(U256(account.balance) if account.balance is not None else U256(0)),
                    code=account.code if account.code is not None else b"",
                ),
            )
            if account.storage is not None:
                for key, value in account.storage.root.items():
                    set_storage(
                        state=state,
                        address=FrontierAddress(address),
                        key=from_hash(key),
                        value=U256(value),
                    )
        return state_root(state)


class Withdrawal(CamelModel):
    """
    Withdrawal type
    """

    index: HexNumberType
    validator_index: HexNumberType
    address: AddressType
    amount: HexNumberType

    def to_serializable_list(self) -> List[Any]:
        """
        Returns a list of the withdrawal's attributes in the order they should
        be serialized.
        """
        return [
            Uint(self.index),
            Uint(self.validator_index),
            self.address,
            Uint(self.amount),
        ]


def withdrawals_root(withdrawals: List[Withdrawal]) -> bytes:
    """
    Returns the withdrawals root of a list of withdrawals.
    """
    t = HexaryTrie(db={})
    for i, w in enumerate(withdrawals):
        t.set(eth_rlp.encode(Uint(i)), eth_rlp.encode(w.to_serializable_list()))
    return t.root_hash


DEFAULT_BASE_FEE = 7


class Environment(CamelModel):
    """
    Structure used to keep track of the context in which a block
    must be executed.
    """

    fee_recipient: AddressType = Field(
        "0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        serialization_alias="currentCoinbase",
        validate_default=True,
    )
    gas_limit: HexNumberType = Field(
        100_000_000_000_000_000, serialization_alias="currentGasLimit"
    )
    number: HexNumberType = Field(1, serialization_alias="currentNumber")
    timestamp: HexNumberType = Field(1_000, serialization_alias="currentTimestamp")
    prev_randao: HexNumberType | None = Field(None, serialization_alias="currentRandom")
    difficulty: HexNumberType | None = Field(None, serialization_alias="currentDifficulty")
    base_fee_per_gas: HexNumberType | None = Field(None, serialization_alias="currentBaseFee")
    blob_gas_used: HexNumberType | None = Field(None, serialization_alias="currentBlobGasUsed")
    excess_blob_gas: HexNumberType | None = Field(None, serialization_alias="currentExcessBlobGas")

    parent_difficulty: HexNumberType | None = Field(None)
    parent_timestamp: HexNumberType | None = Field(None)
    parent_base_fee_per_gas: HexNumberType | None = Field(
        None, serialization_alias="parentBaseFee"
    )
    parent_gas_used: HexNumberType | None = Field(None)
    parent_gas_limit: HexNumberType | None = Field(None)
    parent_ommers_hash: HashType = Field(
        0, serialization_alias="parentUncleHash", validate_default=True
    )
    parent_blob_gas_used: HexNumberType | None = Field(None)
    parent_excess_blob_gas: HexNumberType | None = Field(None)
    parent_beacon_block_root: HashType | None = Field(None)

    block_hashes: Dict[HexNumberType, HashType] = Field(default_factory=dict)
    ommers: List[HashType] = Field(default_factory=list)
    withdrawals: List[Withdrawal] | None = Field(None)
    extra_data: HexBytesType = Field(b"\x00")

    @computed_field  # type: ignore[misc]
    @property
    def parent_hash(self) -> HashType:
        """
        Obtains the latest hash according to the highest block number in
        `block_hashes`.
        """
        if len(self.block_hashes) == 0:
            return bytes([0] * 32)

        last_index = max(self.block_hashes.keys())
        return HashType(self.block_hashes[last_index])

    def set_fork_requirements(self, fork: Fork) -> "Environment":
        """
        Fills the required fields in an environment depending on the fork.
        """
        number = self.number
        timestamp = self.timestamp

        updated_values: Dict[str, Any] = {}

        if fork.header_prev_randao_required(number, timestamp) and self.prev_randao is None:
            updated_values["prev_randao"] = 0

        if fork.header_withdrawals_required(number, timestamp) and self.withdrawals is None:
            updated_values["withdrawals"] = []

        if (
            fork.header_base_fee_required(number, timestamp)
            and self.base_fee_per_gas is None
            and self.parent_base_fee_per_gas is None
        ):
            updated_values["base_fee_per_gas"] = DEFAULT_BASE_FEE

        if fork.header_zero_difficulty_required(number, timestamp):
            updated_values["difficulty"] = 0
        elif self.difficulty is None and self.parent_difficulty is None:
            updated_values["difficulty"] = 0x20000

        if (
            fork.header_excess_blob_gas_required(number, timestamp)
            and self.excess_blob_gas is None
            and self.parent_excess_blob_gas is None
        ):
            updated_values["excess_blob_gas"] = 0

        if (
            fork.header_blob_gas_used_required(number, timestamp)
            and self.blob_gas_used is None
            and self.parent_blob_gas_used is None
        ):
            updated_values["blob_gas_used"] = 0

        if (
            fork.header_beacon_root_required(number, timestamp)
            and self.parent_beacon_block_root is None
        ):
            updated_values["parent_beacon_block_root"] = 0

        return self.model_copy(update=updated_values)


class AccessList(CamelModel):
    """
    Access List for transactions.
    """

    address: AddressType
    storage_keys: List[HashType]

    def to_list(self) -> List[AddressType | List[HashType]]:
        """
        Returns the access list as a list of serializable elements.
        """
        return [self.address, self.storage_keys]


class Transaction(CamelModel):
    """
    Generic object that can represent all Ethereum transaction types.
    """

    ty: HexNumberType | None = Field(None, alias="type")
    """
    Transaction type value.
    """
    chain_id: HexNumberType = 1
    nonce: HexNumberType = 0
    gas_price: HexNumberType | None = None
    max_priority_fee_per_gas: HexNumberType | None = None
    max_fee_per_gas: HexNumberType | None = None
    gas_limit: HexNumberType = Field(21000, alias="gas")
    to: AddressType | None = Field(0xAA, validate_default=True)
    value: HexNumberType = 0
    data: HexBytesType = Field(b"", alias="input")
    access_list: List[AccessList] | None = None
    max_fee_per_blob_gas: HexNumberType | None = None
    blob_versioned_hashes: Sequence[HashType] | None = None
    v: HexNumberType | None = None
    r: HexNumberType | None = None
    s: HexNumberType | None = None
    wrapped_blob_transaction: bool = Field(False, exclude=True)
    blobs: Sequence[HexBytesType] = Field(None, exclude=True)
    blob_kzg_commitments: Sequence[bytes] | None = Field(None, exclude=True)
    blob_kzg_proofs: Sequence[bytes] | None = Field(None, exclude=True)
    sender: AddressType | None = None
    secret_key: HashType | None = None
    protected: bool = Field(True, exclude=True)
    error: TransactionException | None = Field(None, exclude=True)  # TODO: Add ExceptionList
    rlp: HexBytesType | None = Field(None, exclude=True)

    class InvalidFeePayment(Exception):
        """
        Transaction described more than one fee payment type.
        """

        def __str__(self):
            """Print exception string"""
            return "only one type of fee payment field can be used in a single tx"

    class InvalidSignaturePrivateKey(Exception):
        """
        Transaction describes both the signature and private key of
        source account.
        """

        def __str__(self):
            """Print exception string"""
            return "can't define both 'signature' and 'private_key'"

    def model_post_init(self, __context):
        """
        Ensures the transaction has no conflicting properties.
        """
        super().model_post_init(__context)

        if self.gas_price is not None and (
            self.max_fee_per_gas is not None
            or self.max_priority_fee_per_gas is not None
            or self.max_fee_per_blob_gas is not None
        ):
            raise Transaction.InvalidFeePayment()

        if (
            self.gas_price is None
            and self.max_fee_per_gas is None
            and self.max_priority_fee_per_gas is None
            and self.max_fee_per_blob_gas is None
        ):
            self.gas_price = 10

        if self.v is not None and self.secret_key is not None:
            raise Transaction.InvalidSignaturePrivateKey()

        if self.v is None and self.secret_key is None:
            self.secret_key = from_hash(TestPrivateKey)

        if self.ty is None:
            # Try to deduce transaction type from included fields
            if self.max_fee_per_blob_gas is not None:
                self.ty = 3
            elif self.max_fee_per_gas is not None:
                self.ty = 2
            elif self.access_list is not None:
                self.ty = 1
            else:
                self.ty = 0

        # Set default values for fields that are required for certain tx types
        if self.ty >= 1 and self.access_list is None:
            self.access_list = []

        if self.ty >= 2 and self.max_priority_fee_per_gas is None:
            self.max_priority_fee_per_gas = 0

    def with_error(self, error: TransactionException | ExceptionList) -> "Transaction":
        """
        Create a copy of the transaction with an added error.
        """
        return self.model_copy(update={"error": error})

    def with_nonce(self, nonce: int) -> "Transaction":
        """
        Create a copy of the transaction with a modified nonce.
        """
        return self.model_copy(update={"nonce": nonce})

    def with_fields(self, **kwargs) -> "Transaction":
        """
        Create a deepcopy of the transaction with modified fields.
        """
        return self.model_copy(update=kwargs, deep=True)

    def payload_body(self) -> List[Any]:
        """
        Returns the list of values included in the transaction body.
        """
        if self.v is None or self.r is None or self.s is None:
            raise ValueError("signature must be set before serializing any tx type")

        if self.gas_limit is None:
            raise ValueError("gas_limit must be set for all tx types")
        to = AddressType(self.to) if self.to is not None else bytes()

        if self.ty == 3:
            # EIP-4844: https://eips.ethereum.org/EIPS/eip-4844
            if self.max_priority_fee_per_gas is None:
                raise ValueError("max_priority_fee_per_gas must be set for type 3 tx")
            if self.max_fee_per_gas is None:
                raise ValueError("max_fee_per_gas must be set for type 3 tx")
            if self.max_fee_per_blob_gas is None:
                raise ValueError("max_fee_per_blob_gas must be set for type 3 tx")
            if self.blob_versioned_hashes is None:
                raise ValueError("blob_versioned_hashes must be set for type 3 tx")
            if self.access_list is None:
                raise ValueError("access_list must be set for type 3 tx")

            if self.wrapped_blob_transaction:
                if self.blobs is None:
                    raise ValueError("blobs must be set for network version of type 3 tx")
                if self.blob_kzg_commitments is None:
                    raise ValueError(
                        "blob_kzg_commitments must be set for network version of type 3 tx"
                    )
                if self.blob_kzg_proofs is None:
                    raise ValueError(
                        "blob_kzg_proofs must be set for network version of type 3 tx"
                    )

                return [
                    [
                        Uint(self.chain_id),
                        Uint(self.nonce),
                        Uint(self.max_priority_fee_per_gas),
                        Uint(self.max_fee_per_gas),
                        Uint(self.gas_limit),
                        to,
                        Uint(self.value),
                        self.data,
                        [a.to_list() for a in self.access_list],
                        Uint(self.max_fee_per_blob_gas),
                        list(self.blob_versioned_hashes),
                        Uint(self.v),
                        Uint(self.r),
                        Uint(self.s),
                    ],
                    self.blobs,
                    self.blob_kzg_commitments,
                    self.blob_kzg_proofs,
                ]
            else:
                return [
                    Uint(self.chain_id),
                    Uint(self.nonce),
                    Uint(self.max_priority_fee_per_gas),
                    Uint(self.max_fee_per_gas),
                    Uint(self.gas_limit),
                    to,
                    Uint(self.value),
                    self.data,
                    [a.to_list() for a in self.access_list],
                    Uint(self.max_fee_per_blob_gas),
                    list(self.blob_versioned_hashes),
                    Uint(self.v),
                    Uint(self.r),
                    Uint(self.s),
                ]
        elif self.ty == 2:
            # EIP-1559: https://eips.ethereum.org/EIPS/eip-1559
            if self.max_priority_fee_per_gas is None:
                raise ValueError("max_priority_fee_per_gas must be set for type 2 tx")
            if self.max_fee_per_gas is None:
                raise ValueError("max_fee_per_gas must be set for type 2 tx")
            if self.access_list is None:
                raise ValueError("access_list must be set for type 2 tx")
            return [
                Uint(self.chain_id),
                Uint(self.nonce),
                Uint(self.max_priority_fee_per_gas),
                Uint(self.max_fee_per_gas),
                Uint(self.gas_limit),
                to,
                Uint(self.value),
                self.data,
                [a.to_list() for a in self.access_list],
                Uint(self.v),
                Uint(self.r),
                Uint(self.s),
            ]
        elif self.ty == 1:
            # EIP-2930: https://eips.ethereum.org/EIPS/eip-2930
            if self.gas_price is None:
                raise ValueError("gas_price must be set for type 1 tx")
            if self.access_list is None:
                raise ValueError("access_list must be set for type 1 tx")

            return [
                Uint(self.chain_id),
                Uint(self.nonce),
                Uint(self.gas_price),
                Uint(self.gas_limit),
                to,
                Uint(self.value),
                self.data,
                [a.to_list() for a in self.access_list],
                Uint(self.v),
                Uint(self.r),
                Uint(self.s),
            ]
        elif self.ty == 0:
            if self.gas_price is None:
                raise ValueError("gas_price must be set for type 0 tx")
            # EIP-155: https://eips.ethereum.org/EIPS/eip-155
            return [
                Uint(self.nonce),
                Uint(self.gas_price),
                Uint(self.gas_limit),
                to,
                Uint(self.value),
                self.data,
                Uint(self.v),
                Uint(self.r),
                Uint(self.s),
            ]

        raise NotImplementedError(f"serialized_bytes not implemented for tx type {self.ty}")

    def serialized_bytes(self) -> bytes:
        """
        Returns bytes of the serialized representation of the transaction,
        which is almost always RLP encoding.
        """
        if self.rlp is not None:
            return self.rlp

        if self.ty is None:
            raise ValueError("ty must be set for all tx types")

        if self.ty > 0:
            return bytes([self.ty]) + eth_rlp.encode(self.payload_body())
        else:
            return eth_rlp.encode(self.payload_body())

    def signing_envelope(self) -> List[Any]:
        """
        Returns the list of values included in the envelope used for signing.
        """
        if self.gas_limit is None:
            raise ValueError("gas_limit must be set for all tx types")
        to = AddressType(self.to) if self.to is not None else bytes()

        if self.ty == 3:
            # EIP-4844: https://eips.ethereum.org/EIPS/eip-4844
            if self.max_priority_fee_per_gas is None:
                raise ValueError("max_priority_fee_per_gas must be set for type 3 tx")
            if self.max_fee_per_gas is None:
                raise ValueError("max_fee_per_gas must be set for type 3 tx")
            if self.max_fee_per_blob_gas is None:
                raise ValueError("max_fee_per_blob_gas must be set for type 3 tx")
            if self.blob_versioned_hashes is None:
                raise ValueError("blob_versioned_hashes must be set for type 3 tx")
            return [
                Uint(self.chain_id),
                Uint(self.nonce),
                Uint(self.max_priority_fee_per_gas),
                Uint(self.max_fee_per_gas),
                Uint(self.gas_limit),
                to,
                Uint(self.value),
                self.data,
                [a.to_list() for a in self.access_list] if self.access_list is not None else [],
                Uint(self.max_fee_per_blob_gas),
                list(self.blob_versioned_hashes),
            ]
        elif self.ty == 2:
            # EIP-1559: https://eips.ethereum.org/EIPS/eip-1559
            if self.max_priority_fee_per_gas is None:
                raise ValueError("max_priority_fee_per_gas must be set for type 2 tx")
            if self.max_fee_per_gas is None:
                raise ValueError("max_fee_per_gas must be set for type 2 tx")
            return [
                Uint(self.chain_id),
                Uint(self.nonce),
                Uint(self.max_priority_fee_per_gas),
                Uint(self.max_fee_per_gas),
                Uint(self.gas_limit),
                to,
                Uint(self.value),
                self.data,
                [a.to_list() for a in self.access_list] if self.access_list is not None else [],
            ]
        elif self.ty == 1:
            # EIP-2930: https://eips.ethereum.org/EIPS/eip-2930
            if self.gas_price is None:
                raise ValueError("gas_price must be set for type 1 tx")

            return [
                Uint(self.chain_id),
                Uint(self.nonce),
                Uint(self.gas_price),
                Uint(self.gas_limit),
                to,
                Uint(self.value),
                self.data,
                [a.to_list() for a in self.access_list] if self.access_list is not None else [],
            ]
        elif self.ty == 0:
            if self.gas_price is None:
                raise ValueError("gas_price must be set for type 0 tx")

            if self.protected:
                # EIP-155: https://eips.ethereum.org/EIPS/eip-155
                return [
                    Uint(self.nonce),
                    Uint(self.gas_price),
                    Uint(self.gas_limit),
                    to,
                    Uint(self.value),
                    self.data,
                    Uint(self.chain_id),
                    Uint(0),
                    Uint(0),
                ]
            else:
                return [
                    Uint(self.nonce),
                    Uint(self.gas_price),
                    Uint(self.gas_limit),
                    to,
                    Uint(self.value),
                    self.data,
                ]
        raise NotImplementedError("signing for transaction type {self.ty} not implemented")

    def signing_bytes(self) -> bytes:
        """
        Returns the serialized bytes of the transaction used for signing.
        """
        if self.ty is None:
            raise ValueError("ty must be set for all tx types")

        if self.ty > 0:
            return bytes([self.ty]) + eth_rlp.encode(self.signing_envelope())
        else:
            return eth_rlp.encode(self.signing_envelope())

    def signature_bytes(self) -> bytes:
        """
        Returns the serialized bytes of the transaction signature.
        """
        assert self.v is not None and self.r is not None and self.s is not None
        v = self.v
        if self.ty == 0:
            if self.protected:
                assert self.chain_id is not None
                v -= 35 + (self.chain_id * 2)
            else:
                v -= 27
        return (
            self.r.to_bytes(32, byteorder="big")
            + self.s.to_bytes(32, byteorder="big")
            + bytes([v])
        )

    def with_signature_and_sender(self, *, keep_secret_key: bool = False) -> "Transaction":
        """
        Returns a signed version of the transaction using the private key.
        """
        updated_values: Dict[str, Any] = {}

        if self.v is not None:
            # Transaction already signed
            if self.sender is not None:
                return self.model_copy()

            public_key = PublicKey.from_signature_and_message(
                self.signature_bytes(), keccak256(self.signing_bytes()), hasher=None
            )
            updated_values["sender"] = keccak256(public_key.format(compressed=False)[1:])[
                32 - 20 :
            ]
            return self.model_copy(update=updated_values)

        if self.secret_key is None:
            raise ValueError("secret_key must be set to sign a transaction")

        # Get the signing bytes
        signing_hash = keccak256(self.signing_bytes())

        # Sign the bytes

        # TODO: unnecessary check
        private_key = PrivateKey(secret=self.secret_key if self.secret_key else bytes(32))
        signature_bytes = private_key.sign_recoverable(signing_hash, hasher=None)
        public_key = PublicKey.from_signature_and_message(
            signature_bytes, signing_hash, hasher=None
        )

        sender = keccak256(public_key.format(compressed=False)[1:])[32 - 20 :]
        updated_values["sender"] = sender

        v, r, s = (
            signature_bytes[64],
            int.from_bytes(signature_bytes[0:32], byteorder="big"),
            int.from_bytes(signature_bytes[32:64], byteorder="big"),
        )
        if self.ty == 0:
            if self.protected:
                v += 35 + (self.chain_id * 2)
            else:  # not protected
                v += 27

        updated_values["v"] = v
        updated_values["r"] = r
        updated_values["s"] = s

        # Remove the secret key if requested
        if not keep_secret_key:
            updated_values["secret_key"] = None

        return self.model_copy(update=updated_values)


def transaction_list_root(input_txs: List[Transaction] | None) -> HashType:
    """
    Returns the transactions root of a list of transactions.
    """
    t = HexaryTrie(db={})
    for i, tx in enumerate(input_txs or []):
        t.set(eth_rlp.encode(Uint(i)), tx.serialized_bytes())
    return HashType(t.root_hash)


def transaction_list_to_serializable_list(input_txs: List[Transaction] | None) -> List[Any]:
    """
    Returns the transaction list as a list of serializable objects.
    """
    if input_txs is None:
        return []

    txs: List[Any] = []
    for tx in input_txs:
        if tx.ty is None:
            raise ValueError("ty must be set for all tx types")

        if tx.ty > 0:
            txs.append(tx.serialized_bytes())
        else:
            txs.append(tx.payload_body())
    return txs


def serialize_transactions(input_txs: List[Transaction] | None) -> bytes:
    """
    Serialize a list of transactions into a single byte string, usually RLP encoded.
    """
    return eth_rlp.encode(transaction_list_to_serializable_list(input_txs))


def blob_versioned_hashes_from_transactions(
    input_txs: List[Transaction] | None,
) -> List[HashType]:
    """
    Gets a list of ordered blob versioned hashes from a list of transactions.
    """
    versioned_hashes: List[HashType] = []

    if input_txs is None:
        return versioned_hashes

    for tx in input_txs:
        if tx.blob_versioned_hashes is not None and tx.ty == 3:
            versioned_hashes.extend(tx.blob_versioned_hashes)

    return versioned_hashes


# TODO: Move to other file

# Transition tool models


class TransactionReceipt(CamelModel):
    """
    Transaction receipt
    """

    root: HexBytesType
    status: HexNumberType
    cumulative_gas_used: HexNumberType
    logs_bloom: BloomType
    logs: List[Dict[str, str]] | None = None
    transaction_hash: HashType
    contract_address: AddressType
    gas_used: HexNumberType
    effective_gas_price: HexNumberType | None = None
    block_hash: HashType
    transaction_index: HexNumberType
    blob_gas_used: HexNumberType | None = None
    blob_gas_price: HexNumberType | None = None


class RejectedTransaction(CamelModel):
    """
    Rejected transaction
    """

    index: HexNumberType
    error: str


class Result(CamelModel):
    """
    Result of a t8n
    """

    state_root: HashType
    ommers_hash: HashType | None = Field(None, validation_alias="sha3Uncles")
    transactions_trie: HashType = Field(..., alias="txRoot")
    receipts_root: HashType
    logs_hash: HashType
    logs_bloom: BloomType
    receipts: List[TransactionReceipt]
    rejected_transactions: List[RejectedTransaction] | None = Field(None, alias="rejected")
    difficulty: HexNumberType | None = Field(None, alias="currentDifficulty")
    gas_used: HexNumberType
    base_fee_per_gas: HexNumberType | None = Field(None, alias="currentBaseFee")
    withdrawals_root: HashType | None = None
    excess_blob_gas: HexNumberType | None = Field(None, alias="currentExcessBlobGas")
    blob_gas_used: HexNumberType | None = None
