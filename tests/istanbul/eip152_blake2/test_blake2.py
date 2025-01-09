"""
abstract: Tests [EIP-152: BLAKE2 compression precompile](https://eips.ethereum.org/EIPS/eip-152)
    Test cases for [EIP-152: BLAKE2 compression precompile](https://eips.ethereum.org/EIPS/eip-152).
"""

from dataclasses import dataclass

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    StateTestFiller,
    TestParameterGroup,
    Transaction,
    YulCompiler,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-152.md"
REFERENCE_SPEC_VERSION = "5510973b40973b6aa774f04c9caba823c8ff8460"


@dataclass(kw_only=True, frozen=True, repr=False)
class Blake2Input(TestParameterGroup):
    """
    Helper class that defines the BLAKE2 precompile inputs and creates the
    call data from them.

    Attributes:
        tx_data_rounds (bytes): The number of rounds for the BLAKE2 precompile.
        h (str): The state vector for the BLAKE2 precompile.
        m (str): The message block vector for the BLAKE2 precompile.
        t_0 (str): Offset counter 0 for the BLAKE2 precompile.
        t_1 (str): Offset counter 1 for the BLAKE2 precompile.
        f (str): The final block indicator flag for the BLAKE2 precompile.

    """

    rounds: bytes
    data: bytes = b""

    def create_blake2_tx_data(self):
        """Generate input for the BLAKE2 precompile."""
        return self.rounds


@dataclass(kw_only=True, frozen=True, repr=False)
class ExpectedOutput(TestParameterGroup):
    """
    Expected test result.

    Attributes:
        returned_data (str): The output returnData is the expected output of the call

    """

    call_return_code: str
    data_1: str
    data_2: str


@pytest.mark.valid_from("Istanbul")
@pytest.mark.parametrize(
    ["data", "output"],
    [
        pytest.param(
            Blake2Input(rounds=b"\x00"),
            ExpectedOutput(
                call_return_code="0x00",
                data_1="0x00",
                data_2="0x00",
            ),
            id="EIP-192-case0",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x01"),
            ExpectedOutput(
                call_return_code="0x00",
                data_1="0x00",
                data_2="0x00",
            ),
            id="EIP-192-case1",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x02"),
            ExpectedOutput(
                call_return_code="0x00",
                data_1="0x00",
                data_2="0x00",
            ),
            id="EIP-192-case2",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x03"),
            ExpectedOutput(
                call_return_code="0x00",
                data_1="0x00",
                data_2="0x00",
            ),
            id="EIP-192-case3",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x04"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x08c9bcf367e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d5f3af54fa5",
                data_2="0xd282e6ad7f520e511f6c3e2b8c68059b9442be0454267ce079217e1319cde05b",
            ),
            id="EIP-192-case4",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x05"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xba80a53f981c4d0d6a2797b69f12f6e94c212f14685ac4b74b12bb6fdbffa2d1",
                data_2="0x7d87c5392aab792dc252d5de4533cc9518d38aa8dbf1925ab92386edd4009923",
            ),
            id="EIP-192-case5",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x06"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x75ab69d3190a562c51aef8d88f1c2775876944407270c42c9844252c26d28752",
                data_2="0x98743e7f6d5ea2f2d3e8d226039cd31b4e426ac4f2d3d666a610c2116fde4735",
            ),
            id="EIP-192-case6",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x07"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xb63a380cb2897d521994a85234ee2c181b5f844d2c624c002677e9703449d2fb",
                data_2="0xa551b3a8333bcdf5f2f7e08993d53923de3d64fcc68c034e717b9293fed7a421",
            ),
            id="EIP-192-case7",
        ),
        # Slow case with large number of rounds
        # pytest.param(
        #     Blake2Input(rounds=b"\x08"),
        #     ExpectedOutput(
        #         call_return_code="0x01",
        #         data_1="0xfc59093aafa9ab43daae0e914c57635c5402d8e3d2130eb9b3cc181de7f0ecf9",
        #         data_2="0xb22bf99a7815ce16419e200e01846e6b5df8cc7703041bbceb571de6631d2615",
        #     ),
        #     id="EIP-192-case8",
        # ),
        pytest.param(
            Blake2Input(rounds=b"\x09"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xf3e89a60ec4b0b1854744984e421d22b82f181bd4601fb9b1726b2662da61c29",
                data_2="0xdff09e75814acb2639fd79e56616e55fc135f8476f0302b3dc8d44e082eb83a8",
            ),
            id="EIP-192-case9",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x10"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xa8ef8236e5f48a74af375df15681d128457891c1cc4706f30747b2d40300b2f4",
                data_2="0x9d19f80fbd0945fd87736e1fc1ff10a80fd85a7aa5125154f3aaa3789ddff673",
            ),
            id="EIP-192-0016",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x20"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xbc5e888ed71b546da7b1506179bdd6c184a6410c40de33f9c330207417797889",
                data_2="0x5dbe74144468aefe5c2afce693c62dbca99e5e076dd467fe90a41278b16d691e",
            ),
            id="EIP-192-0032",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x40"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x74097ae7b16ffd18c742aee5c55dc89d54b6f1a8a19e6139ccfb38afba56b6b0",
                data_2="0x2cc35c441c19c21194fefb6841e72202f7c9d05eb9c3cfd8f94c67aa77d473c1",
            ),
            id="EIP-192-0064",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x80"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xd82c6a670dc90af9d7f77644eacbeddfed91b760c65c927871784abceaab3f81",
                data_2="0x3759733a1736254fb1cfc515dbfee467930955af56e27ee435f836fc3e65969f",
            ),
            id="EIP-192-0128",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x01\x00"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x5d6ff04d5ebaee5687d634613ab21e9a7d36f782033c74f91d562669aaf9d592",
                data_2="0xc86346cb2df390243a952834306b389e656876a67934e2c023bce4918a016d4e",
            ),
            id="EIP-192-0256",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x02\x00"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xa2c1eb780a6e1249156fe0751e5d4687ea9357b0651c78df660ab004cb477363",
                data_2="0x6298bbbc683e4a0261574b6d857a6a99e06b2eea50b16f86343d2625ff222b98",
            ),
            id="EIP-192-0512",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x04\x00"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x689419d2bf32b5a9901a2c733b9946727026a60d8773117eabb35f04a52cdcf1",
                data_2="0xb8fb4473454cf03d46c36a10b3f784aae4dc80a24424960e66a8ad5a8c2bfb30",
            ),
            id="EIP-192-1024",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x10", data=b"\x10"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x68790ca7594dd6fc28f0a86b7ddce0a225a8ea8fc2637f910eb71f6e54d9f8fa",
                data_2="0x3e6302691015f11b15b755076d316823e6ce2ee4dd4aef60efc9189f6bd21bfd",
            ),
            id="EIP-192-0016-16",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x20", data=b"\x10"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xcf087b9b6ae026d358a13c577a04a4af4e65293be70b7cb2a7e00bd1317440af",
                data_2="0x94b896bca7c282001aeb86cc307973096917897eadc97ed8eefb0d2b3c309a8b",
            ),
            id="EIP-192-0032-16",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x40", data=b"\x10"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xafd469613835ad3c75a54cd3087160eb308f5d6cd2151f1490f51b182dc5d130",
                data_2="0x16428bf21e474e2921023bbeec971429210a51f0b63741583b0153fe8f6c27b6",
            ),
            id="EIP-192-0064-16",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x80", data=b"\x10"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x94e963dcaa85d33dad6c0043b6700f5e227a2d8bed804bd16970e64fa6f1e163",
                data_2="0x07399239bcddf968612c8c9ba953d9b173575c31ef269c3a8721cb9bf1c02012",
            ),
            id="EIP-192-0128-16",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x01\x00", data=b"\x10"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x7476f1f8e159b30b156b0e9fffbaee5badbb45abb488ea9cfa04f60d3a096408",
                data_2="0x7535a649e438ba993f03cfc0d8d8676a792030a996b6a6fde5c29108b6bfb871",
            ),
            id="EIP-192-0256-16",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x02\x00", data=b"\x10"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xa65aadbf393aad57c4b06d6471134c5c01002c23dfe8290e115e024e05bc1bf1",
                data_2="0x084d1651de54a83902ed582cb8f2ba381c69687cceaecea0cd8fe5529f86686e",
            ),
            id="EIP-192-0512-16",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x04\x00", data=b"\x10"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0xbc112be5618b20d24be64c9e1c6efd63fea38cc79d53692fad6568b16e953eb6",
                data_2="0x128c1ec8ffaf9a2d69e3cb043d6e11e1c7afd48573311052b6e7ec0960371186",
            ),
            id="EIP-192-1024-16",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x10", data=b"\x00x"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x7df6f69476a03ae29e944814846460b058d1762fffe77f938ea723d1033de0d5",
                data_2="0xbb1f8234bd73afaf955622fa2cdde95594577a8d53191908eb69b316a53c985b",
            ),
            id="EIP-192-0016-120",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x20", data=b"\x00x"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x38dfb111db6c59c39c9bea26c8c872620d89dec22fd7da93c47d0708a3973f52",
                data_2="0x2858fd9c60fae53f366d7e2820040a8662b336de6d859764f20747acbb8999fe",
            ),
            id="EIP-192-0032-120",
        ),
        pytest.param(
            Blake2Input(rounds=b"\x00\x40", data=b"\x00x"),
            ExpectedOutput(
                call_return_code="0x01",
                data_1="0x59c7c9896cdc9fda0a77bd41adba14bdd6cb47cbbd7c338482f5382d7be16ac4",
                data_2="0x4a2ddfe6833bf9a15737dd66469d2d0495d39a9cb3c8ed93152684d92a74f8bc",
            ),
            id="EIP-192-0064-120",
        ),
    ],
)
def test_blake2(
    state_test: StateTestFiller,
    yul: YulCompiler,
    data: Blake2Input,
    output: ExpectedOutput,
    pre: Alloc,
):
    """Test BLAKE2 precompile."""
    env = Environment()

    account = pre.deploy_contract(
        code=yul(
            """
            {
                // Selected test case / number of rounds
                let param := calldataload(0x04)

                // Message length (if specified)
                let msgLen := calldataload(0x24)

                // The default buffer length. Changed by some test cases
                let bufLength := 213

                // The test case we're checking
                switch param
                // 0-8 are test cases from the EIP
                //
                // Huge strings in the EIP cut into 0x20 chunks using:
                // for(var i=0; i<(2*0xE0); i+=0x40) {
                //     console.log(`mstore(0x${(i/2).toString(16)}, 0x${
                //          x.slice(i, i+0x40).padEnd(0x40, "0")})`)
                // }

                case 0 {
                    bufLength := 0
                }
                case 1 {
                    bufLength := 212
                    mstore(0x00, 0x00000c48c9bdf267e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d5f3a)
                    mstore(0x20, 0xf54fa5d182e6ad7f520e511f6c3e2b8c68059b6bbd41fbabd9831f79217e1319)
                    mstore(0x40, 0xcde05b6162630000000000000000000000000000000000000000000000000000)
                    mstore(0x60, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0x80, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xa0, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xc0, 0x0000000300000000000000000000000000000001000000000000000000000000)
                }
                case 2 {
                    bufLength := 214
                    mstore(0x00, 0x000000000c48c9bdf267e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d)
                    mstore(0x20, 0x5f3af54fa5d182e6ad7f520e511f6c3e2b8c68059b6bbd41fbabd9831f79217e)
                    mstore(0x40, 0x1319cde05b616263000000000000000000000000000000000000000000000000)
                    mstore(0x60, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0x80, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xa0, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xc0, 0x0000000000030000000000000000000000000000000100000000000000000000)
                }
                case 3 {
                    mstore(0x00, 0x0000000c48c9bdf267e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d5f)
                    mstore(0x20, 0x3af54fa5d182e6ad7f520e511f6c3e2b8c68059b6bbd41fbabd9831f79217e13)
                    mstore(0x40, 0x19cde05b61626300000000000000000000000000000000000000000000000000)
                    mstore(0x60, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0x80, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xa0, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xc0, 0x0000000003000000000000000000000000000000020000000000000000000000)
                }
                case 4 {
                    mstore(0x00, 0x0000000048c9bdf267e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d5f)
                    mstore(0x20, 0x3af54fa5d182e6ad7f520e511f6c3e2b8c68059b6bbd41fbabd9831f79217e13)
                    mstore(0x40, 0x19cde05b61626300000000000000000000000000000000000000000000000000)
                    mstore(0x60, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0x80, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xa0, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xC0, 0x0000000003000000000000000000000000000000010000000000000000000000)
                }
                case 5 {
                    mstore(0x00,0x0000000c48c9bdf267e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d5f)
                    mstore(0x20,0x3af54fa5d182e6ad7f520e511f6c3e2b8c68059b6bbd41fbabd9831f79217e13)
                    mstore(0x40,0x19cde05b61626300000000000000000000000000000000000000000000000000)
                    mstore(0x60,0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0x80,0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xa0,0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xc0,0x0000000003000000000000000000000000000000010000000000000000000000)
                }
                case 6 {
                    mstore(0x00, 0x0000000c48c9bdf267e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d5f)
                    mstore(0x20, 0x3af54fa5d182e6ad7f520e511f6c3e2b8c68059b6bbd41fbabd9831f79217e13)
                    mstore(0x40, 0x19cde05b61626300000000000000000000000000000000000000000000000000)
                    mstore(0x60, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0x80, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xa0, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xc0, 0x0000000003000000000000000000000000000000000000000000000000000000)
                }
                case 7 {
                    mstore(0x00, 0x0000000148c9bdf267e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d5f)
                    mstore(0x20, 0x3af54fa5d182e6ad7f520e511f6c3e2b8c68059b6bbd41fbabd9831f79217e13)
                    mstore(0x40, 0x19cde05b61626300000000000000000000000000000000000000000000000000)
                    mstore(0x60, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0x80, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xa0, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xc0, 0x0000000003000000000000000000000000000000010000000000000000000000)
                }
                // Not used because it's 2^64-1 rounds which is too slow
                case 8 {
                    mstore(0x00, 0xffffffff48c9bdf267e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d5f)
                    mstore(0x20, 0x3af54fa5d182e6ad7f520e511f6c3e2b8c68059b6bbd41fbabd9831f79217e13)
                    mstore(0x40, 0x19cde05b61626300000000000000000000000000000000000000000000000000)
                    mstore(0x60, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0x80, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xa0, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xc0, 0x0000000003000000000000000000000000000000010000000000000000000000)
                }


                // This case is provided by jochem-brouwer in 
                // https://github.com/ethereum/tests/pull/948#issuecomment-925964632  
                case 9 {
                    mstore(0x00, 0x0000000c48c9bdf267e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d5f)
                    mstore(0x20, 0x3af54fa5d182e6ad7f520e511f6c3e2b8c68059b6bbd41fbabd9831f79217e13)
                    mstore(0x40, 0x19cde05b61626364650000000000000000000000000000000000000000000000)
                    mstore(0x60, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0x80, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xa0, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xc0, 0x0000000005000000000000000000000000000000010000000000000000000000)
                }

                // if param is over 0x0F then it's the number of rounds
                if gt(param, 0x0F) {
                    mstore(0x00, 0x0000000048c9bdf267e6096a3ba7ca8485ae67bb2bf894fe72f36e3cf1361d5f)
                    mstore(0x20, 0x3af54fa5d182e6ad7f520e511f6c3e2b8c68059b6bbd41fbabd9831f79217e13)
                    mstore(0x40, 0x19cde05b61626300000000000000000000000000000000000000000000000000)
                    mstore(0x60, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0x80, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xa0, 0x0000000000000000000000000000000000000000000000000000000000000000)
                    mstore(0xc0, 0x0000000003000000000000000000000000000000010000000000000000000000)

                    // The first four bytes are the number of rounds.
                    mstore8(0x00, shr(24, and(param, 0xFF000000)))
                    mstore8(0x01, shr(16, and(param, 0x00FF0000)))
                    mstore8(0x02, shr( 8, and(param, 0x0000FF00)))
                    mstore8(0x03,         and(param, 0x000000FF))
                }  // if param is over 0x0F

                // The message starts at byte 0x44
                if gt(msgLen, 0) {
                    for { } gt(msgLen, 0) { } {
                        // Write a byte
                        mstore8(add(0x44, msgLen), add(0x60, msgLen))
                        msgLen := sub(msgLen, 1)
                    }
                }

                // The input is bytes 0-bufLength
                // The output is bytes 0x200-0x23F
                let retVal := call(gas(), 9, 0, 0, bufLength, 0x200, 0x40)

                // Return the results
                sstore(0, retVal)   // Success? Failure?
                // The output
                sstore(1, mload(0x200))
                sstore(2, mload(0x220))
            }
            """
        ),
    )
    sender = pre.fund_eoa()

    tx = Transaction(
        ty=0x0,
        to=account,
        data=data.create_blake2_tx_data(),
        gas_limit="0xF000000000",
        gas_price=10,
        protected=True,
        sender=sender,
        value=100000,
    )

    post = {}
    post = {
        account: Account(
            storage={
                0: output.call_return_code,
                1: output.data_1,
                2: output.data_2,
            }
        )
    }
    state_test(env=env, pre=pre, post=post, tx=tx)
