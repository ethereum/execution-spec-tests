"""Pydantic models for fuzzer output format v2."""

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

from ethereum_test_base_types import Address, Bytes, Hash, HexNumber

# ruff: noqa: N815  # Allow mixedCase for JSON field compatibility


class FuzzerAccount(BaseModel):
    """Account definition in fuzzer output."""

    balance: HexNumber
    nonce: HexNumber = HexNumber(0)
    code: Bytes = Bytes(b"")
    storage: Dict[HexNumber, HexNumber] = Field(default_factory=dict)
    privateKey: Optional[Bytes] = Field(None, alias="privateKey")

    @field_validator("storage", mode="before")
    @classmethod
    def validate_storage(cls, v):
        """Convert storage keys and values to HexNumber."""
        if not v:
            return {}
        return {HexNumber(k): HexNumber(v_) for k, v_ in v.items()}


class FuzzerTransaction(BaseModel):
    """Transaction definition in fuzzer output."""

    from_: Address = Field(..., alias="from")
    to: Optional[Address] = None
    value: HexNumber = HexNumber(0)
    gas: HexNumber
    gasPrice: Optional[HexNumber] = Field(None, alias="gasPrice")
    maxFeePerGas: Optional[HexNumber] = Field(None, alias="maxFeePerGas")
    maxPriorityFeePerGas: Optional[HexNumber] = Field(None, alias="maxPriorityFeePerGas")
    nonce: HexNumber
    data: Bytes = Bytes(b"")
    accessList: Optional[List[Dict[str, Union[str, List[str]]]]] = Field(None, alias="accessList")
    blobVersionedHashes: Optional[List[Hash]] = Field(None, alias="blobVersionedHashes")
    maxFeePerBlobGas: Optional[HexNumber] = Field(None, alias="maxFeePerBlobGas")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class FuzzerEnvironment(BaseModel):
    """Environment definition in fuzzer output."""

    currentCoinbase: Address = Field(..., alias="currentCoinbase")
    currentDifficulty: HexNumber = Field(HexNumber(0), alias="currentDifficulty")
    currentGasLimit: HexNumber = Field(..., alias="currentGasLimit")
    currentNumber: HexNumber = Field(..., alias="currentNumber")
    currentTimestamp: HexNumber = Field(..., alias="currentTimestamp")
    currentBaseFee: Optional[HexNumber] = Field(None, alias="currentBaseFee")
    currentRandom: Optional[Hash] = Field(None, alias="currentRandom")
    currentExcessBlobGas: Optional[HexNumber] = Field(None, alias="currentExcessBlobGas")
    currentBlobGasUsed: Optional[HexNumber] = Field(None, alias="currentBlobGasUsed")
    parentBeaconBlockRoot: Optional[Hash] = Field(None, alias="parentBeaconBlockRoot")
    parentUncleHash: Optional[Hash] = Field(None, alias="parentUncleHash")
    parentDifficulty: Optional[HexNumber] = Field(None, alias="parentDifficulty")
    parentBaseFee: Optional[HexNumber] = Field(None, alias="parentBaseFee")
    parentGasUsed: Optional[HexNumber] = Field(None, alias="parentGasUsed")
    parentGasLimit: Optional[HexNumber] = Field(None, alias="parentGasLimit")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class FuzzerOutput(BaseModel):
    """Main fuzzer output format v2."""

    version: str = Field(..., pattern="^2\\.0$")
    fork: str
    chainId: int = Field(1, alias="chainId")
    accounts: Dict[Address, FuzzerAccount]
    transactions: List[FuzzerTransaction]
    env: FuzzerEnvironment

    @field_validator("version")
    @classmethod
    def validate_version(cls, v):
        """Ensure version is 2.0."""
        if v != "2.0":
            raise ValueError(f"Only version 2.0 is supported, got {v}")
        return v

    @field_validator("accounts", mode="before")
    @classmethod
    def validate_accounts(cls, v):
        """Convert account addresses to Address type."""
        if not v:
            return {}
        return {
            Address(addr): (FuzzerAccount(**acc_data) if isinstance(acc_data, dict) else acc_data)
            for addr, acc_data in v.items()
        }

    def validate_private_keys(self) -> None:
        """Validate that all transaction senders have private keys."""
        senders = {tx.from_ for tx in self.transactions}
        for sender in senders:
            if sender not in self.accounts:
                raise ValueError(f"Sender {sender} not found in accounts")
            if not self.accounts[sender].privateKey:
                raise ValueError(f"No private key for sender {sender}")

    def get_sender_private_key(self, sender: Address) -> Bytes:
        """Get the private key for a sender address."""
        if sender not in self.accounts:
            raise ValueError(f"Sender {sender} not found in accounts")
        private_key = self.accounts[sender].privateKey
        if not private_key:
            raise ValueError(f"No private key for sender {sender}")
        return private_key
