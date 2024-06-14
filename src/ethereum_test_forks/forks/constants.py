"""
Constant values used by the forks.
"""

from typing import Dict, Generator, Iterator, Mapping, Tuple

from Crypto.Hash import SHA256

# TODO: Use for large verkle conversion init MPT
MAX_ACCOUNTS = 1000
MAX_NONCE = 2**64 - 1
MAX_BALANCE = 2**256 - 1
MAX_STORAGE_SLOTS_PER_ACCOUNT = 1000
MAX_ACCOUNT_CODE_SIZE = 2**14 + 2**13  # EIP-170


def seed_generator(seed: int) -> Generator[int, None, None]:
    """
    Generate a seed using the SHA256 hash function.
    """
    seed = int.from_bytes(
        bytes=SHA256.new(data=seed.to_bytes(length=256, byteorder="big")).digest(), byteorder="big"
    )
    while True:
        yield seed
        seed = int.from_bytes(
            bytes=SHA256.new(data=seed.to_bytes(length=256, byteorder="big")).digest(),
            byteorder="big",
        )


def storage_generator(
    seed: Iterator[int], max_slots: int
) -> Generator[Tuple[int, int], None, None]:
    """
    Generate storage slots for an account.
    """
    MAX_KEY_VALUE = 2**256 - 1
    for _ in range(max_slots):
        yield next(seed) % MAX_KEY_VALUE, next(seed) % MAX_KEY_VALUE


def account_generator(
    seed: Iterator[int], max_accounts: int
) -> Generator[Tuple[int, Dict[str, str | int | Dict[int, int]]], None, None]:
    """
    Generate accounts.
    """
    for _ in range(max_accounts):
        storage_g = storage_generator(seed, next(seed) % MAX_STORAGE_SLOTS_PER_ACCOUNT)
        yield next(seed) % 2**160, {
            "nonce": next(seed) % MAX_NONCE,
            "balance": next(seed) % MAX_BALANCE,
            "storage": {k: v for k, v in storage_g},
            "code": "0x" + "00" * 32,
        }


VERKLE_PRE_ALLOCATION: Mapping = {
    addr: account
    for addr, account in account_generator(seed=seed_generator(0), max_accounts=MAX_ACCOUNTS)
}
