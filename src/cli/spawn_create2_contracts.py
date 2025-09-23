#!/usr/bin/env python3
"""
Deploy a CREATE2 factory for on-the-fly contract address generation in BloatNet tests.

This factory uses a constant initcode that generates unique 24KB contracts by:
1. Using ADDRESS opcode for pseudo-randomness (within the factory's context)
2. Expanding randomness with SHA3 and XOR operations
3. Creating max-size contracts with deterministic CREATE2 addresses
"""

import sys
from dataclasses import dataclass

import click
import rlp
from coincurve import PrivateKey
from eth_utils import keccak
from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeElapsedColumn

from ethereum_test_base_types import Address, Hash, TestPrivateKey
from ethereum_test_rpc import EthRPC, SendTransactionExceptionError
from ethereum_test_rpc.rpc_types import TransactionByHashResponse
from ethereum_test_tools import While
from ethereum_test_types import Transaction
from ethereum_test_vm import Opcodes as Op

XOR_TABLE_SIZE = 256
XOR_TABLE = [keccak(i.to_bytes(32, "big")) for i in range(XOR_TABLE_SIZE)]
MAX_CONTRACT_SIZE = 24576

console = Console()


class RPCRequest:
    """Pure RPC abstraction for Ethereum interactions."""

    def __init__(self, rpc_url: str):
        """
        Initialize RPC client.

        Args:
            rpc_url: RPC endpoint URL.

        """
        self.rpc_url = rpc_url
        self._rpc = self._connect()

    @property
    def rpc(self) -> EthRPC:
        """Get connected RPC client."""
        return self._rpc

    def _connect(self) -> EthRPC:
        """Connect to RPC endpoint and validate connection."""
        try:
            rpc = EthRPC(self.rpc_url)
            rpc.post_request(method="chainId")
            console.print(f"[green]✅ Connected to RPC:[/green] [cyan]{self.rpc_url}[/cyan]")
            return rpc
        except Exception as e:
            console.print(f"[red]Failed to connect to {self.rpc_url}: {e}[/red]")
            raise

    def get_account_balance(self, account: Address) -> int:
        """Get account balance."""
        return self.rpc.get_balance(account)

    def get_transaction_count(self, account: Address) -> int:
        """Get account nonce."""
        return self.rpc.get_transaction_count(account)

    def send_transaction(self, tx: Transaction) -> Hash:
        """Send transaction and return hash."""
        return self.rpc.send_transaction(tx)

    def wait_for_transaction(self, tx: Transaction) -> TransactionByHashResponse:
        """Wait for transaction receipt."""
        return self.rpc.wait_for_transaction(tx)


@dataclass(kw_only=True)
class FactoryDeploymentResult:
    """Result of factory deployment operation."""

    factory_address: Address
    init_code_hash: str
    initcode_address: Address
    deployed_contracts: int = 0


class DeploymentFactory:
    """Handles all deployment operations and orchestration."""

    def __init__(self, rpc_request: RPCRequest, private_key: int = TestPrivateKey):
        """
        Initialize deployment factory.

        Args:
            rpc_request: RPC client for blockchain interactions.
            private_key: Private key for signing transactions.

        """
        self.rpc = rpc_request
        self.private_key = private_key
        self._account = self._derive_account_from_private_key()

    @property
    def account(self) -> Address:
        """Get validated account address."""
        return self._account

    def _derive_account_from_private_key(self) -> Address:
        """Derive account address from private key and validate it."""
        try:
            # Convert private key to bytes and derive public key
            private_key_obj = PrivateKey(self.private_key.to_bytes(32, "big"))
            public_key = private_key_obj.public_key

            # Derive address from public key (last 20 bytes of keccak hash)
            account = Address(keccak(public_key.format(compressed=False)[1:])[-20:])

            balance = self.rpc.get_account_balance(account)
            if balance == 0:
                console.print(f"[yellow]Warning: Account {account} has zero balance[/yellow]")

            console.print(f"Using account: [cyan]{account}[/cyan] (balance: {balance} wei)")
            return account
        except Exception as e:
            console.print(f"[red]Error deriving account from private key: {e}[/red]")
            raise

    def deploy_contract(self, bytecode: bytes, description: str) -> Address:
        """
        Deploy a contract and return its address.

        Args:
            bytecode: Contract bytecode to deploy.
            description: Human-readable description for logging.

        Returns:
            Deployed contract address.

        Raises:
            Exception: If deployment fails.

        """
        console.print(f"\n[bold]Deploying {description}...[/bold]")
        try:
            # Get current gas price from network

            tx = Transaction(
                nonce=self.rpc.get_transaction_count(self.account),
                gas_limit=1_000_000,
                gas_price=self.rpc.rpc.gas_price(),
                data=bytecode,
                secret_key=self.private_key,
            )

            tx_hash = self.rpc.send_transaction(tx)
            console.print(f"Transaction hash: [dim]{tx_hash}[/dim]")

            receipt = self.rpc.wait_for_transaction(tx)
            if receipt is None:
                raise Exception(f"Failed to get receipt for {description}")

            if receipt.error:
                raise Exception(f"Failed to deploy {description}: {receipt.error}")

            contract_address = Address(keccak(rlp.encode([self.account, tx.nonce]))[-20:])
            console.print(
                f"[green]✅ {description} deployed at:[/green] [cyan]{contract_address}[/cyan]"
            )
            return contract_address
        except SendTransactionExceptionError as e:
            console.print(f"[red]Transaction failed for {description}: {e}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Error deploying {description}: {e}[/red]")
            raise

    def deploy_create2_factory(self) -> FactoryDeploymentResult:
        """
        Deploy both the initcode template and factory.

        Returns:
            FactoryDeploymentResult with deployment information.

        """
        # Deploy initcode template
        initcode = self._build_initcode()

        initcode_address = self.deploy_contract(
            bytecode=initcode, description="initcode template contract"
        )

        # Deploy factory
        factory_code = self._build_factory_code(initcode_address)

        factory_address = self.deploy_contract(
            bytecode=factory_code, description="CREATE2 factory"
        )

        init_code_hash = keccak(initcode)

        return FactoryDeploymentResult(
            factory_address=factory_address,
            init_code_hash=init_code_hash.hex(),
            initcode_address=initcode_address,
        )

    def spawn_contracts(self, factory_address: Address) -> bool:
        """
        Spawn a contract via CREATE2.

        Args:
            factory_address: Address of the factory contract.

        Returns:
            True if spawn succeeded, False otherwise.

        """
        try:
            # Get current gas price from network
            gas_price = self.rpc.rpc.gas_price()

            tx = Transaction(
                nonce=self.rpc.get_transaction_count(self.account),
                to=factory_address,
                gas_price=gas_price,
                secret_key=self.private_key,
            )

            self.rpc.send_transaction(tx)
            receipt = self.rpc.wait_for_transaction(tx)
            return receipt is not None
        except Exception:
            return False

    def deploy_contracts_via_factory(self, factory_address: Address, num_contracts: int) -> int:
        """
        Deploy multiple contracts using the factory with progress tracking.

        Args:
            factory_address: Address of the deployed factory contract.
            num_contracts: Number of contracts to deploy.

        Returns:
            Number of successfully deployed contracts.

        """
        console.print(f"\n[bold]Deploying {num_contracts} contracts via factory...[/bold]")
        deployed_count = 0

        with Progress(
            TextColumn("[bold cyan]Deploying contracts...[/bold cyan]"),
            BarColumn(bar_width=None, complete_style="green3", finished_style="bold green3"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            expand=True,
        ) as progress:
            task_id = progress.add_task("Deploying", total=num_contracts)

            for i in range(num_contracts):
                if self.spawn_contracts(factory_address):
                    deployed_count += 1
                else:
                    console.print(f"[yellow]⚠️ Failed to deploy contract {i}[/yellow]")

                progress.update(task_id, advance=1)

        return deployed_count

    def _build_initcode(self) -> bytes:
        """
        Build the initcode that generates unique 24KB contracts using ADDRESS for randomness.

        This initcode follows the pattern from test_worst_bytecode.py:
        1. Uses ADDRESS as initial seed for pseudo-randomness (creates uniqueness per deployment)
        2. Expands to 24KB using SHA3 and XOR operations
        3. Sets first byte to STOP for quick CALL returns

        Returns:
            The compiled initcode as bytes.

        """
        initcode = (
            # Uses ADDRESS as seed for pseudo-randomness (creates uniqueness per deployment)
            Op.MSTORE(0, Op.ADDRESS)
            # Loop to expand bytecode using SHA3 and XOR operations
            + While(
                body=(
                    Op.SHA3(Op.SUB(Op.MSIZE, 32), 32)
                    # # Use XOR table to expand without excessive SHA3 calls
                    + sum(
                        (Op.PUSH32[xor_value] + Op.XOR + Op.DUP1 + Op.MSIZE + Op.MSTORE)
                        for xor_value in XOR_TABLE
                    )
                    + Op.POP
                ),
                condition=Op.LT(Op.MSIZE, MAX_CONTRACT_SIZE),
            )
            + Op.MSTORE8(0, 0x00)
            + Op.RETURN(0, MAX_CONTRACT_SIZE)
        )
        return bytes(initcode)

    def _build_factory_code(self, initcode_address: Address) -> bytes:
        """
        Build the factory contract code.

        Args:
            initcode_address: Address of the deployed initcode template.

        Returns:
            Factory contract bytecode.

        """
        factory_code = (
            Op.EXTCODECOPY(
                address=initcode_address,
                dest_offset=0,
                offset=0,
                size=Op.EXTCODESIZE(initcode_address),
            )
            + Op.MSTORE(
                0,
                Op.CREATE2(
                    value=0,
                    offset=0,
                    size=Op.EXTCODESIZE(initcode_address),
                    salt=Op.SLOAD(0),
                ),
            )
            + Op.SSTORE(0, Op.ADD(Op.SLOAD(0), 1))
            + Op.RETURN(0, 32)
        )
        return bytes(factory_code)


def print_deployment_results(result: FactoryDeploymentResult) -> None:
    """
    Print the deployment results in a formatted way.

    Args:
        result: The deployment result data.

    """
    console.print("\n" + "=" * 60)
    console.print("[bold green]Factory deployed successfully![/bold green]")
    console.print(f"Factory address: [cyan]{result.factory_address}[/cyan]")
    console.print(f"Initcode template address: [cyan]{result.initcode_address}[/cyan]")
    console.print(f"Init code hash: [dim]0x{result.init_code_hash}[/dim]")
    if result.deployed_contracts > 0:
        console.print(f"[green]Deployed contracts count: {result.deployed_contracts}[/green]")
    console.print("=" * 60)


@click.command(help="Deploy factory and spawn contracts via factory with create2 pattern.")
@click.option(
    "--rpc-url",
    default="http://127.0.0.1:8545",
    type=str,
    help="RPC URL (default: http://127.0.0.1:8545)",
)
@click.option(
    "--deploy-count",
    type=int,
    help="Deploy N contracts using the factory",
)
@click.option(
    "--private-key",
    type=str,
    help="Private key for signing transactions",
)
def spawn_create2_contracts(rpc_url: str, deploy_count: int, private_key: str) -> None:
    """Deploy factory and spawn contracts via factory with create2 pattern."""
    try:
        parsed_private_key = int(private_key, 16)

        rpc_request = RPCRequest(rpc_url)
        deployment_factory = DeploymentFactory(rpc_request, parsed_private_key)

        result = deployment_factory.deploy_create2_factory()

        if deploy_count:
            deployed_count = deployment_factory.deploy_contracts_via_factory(
                result.factory_address, deploy_count
            )
            if deployed_count == deploy_count:
                console.print(
                    f"\n[green]✅ Successfully deployed {deploy_count} contracts[/green]"
                )
            else:
                console.print(
                    f"\n[yellow]⚠️ Deployed {deployed_count}/{deploy_count} contracts[/yellow]"
                )

        print_deployment_results(result)

    except Exception as e:
        console.print(f"\n[red]❌ Deployment failed: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    spawn_create2_contracts()
