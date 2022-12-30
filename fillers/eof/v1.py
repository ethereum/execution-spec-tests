"""
Test EVM Object Format Version 1
"""
from typing import List, Tuple

from ethereum_test_tools import (
    Account,
    Code,
    Environment,
    Initcode,
    StateTest,
    TestAddress,
    Transaction,
    Yul,
    compute_create2_address,
    compute_create_address,
    test_from,
    to_address,
)
from ethereum_test_tools.eof import LATEST_EOF_VERSION
from ethereum_test_tools.eof.v1 import (
    VERSION_MAX_SECTION_KIND,
    Container,
    Section,
    SectionKind,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

EOF_FORK_NAME = "Shanghai"

EIP_EOF = 3540
EIP_CODE_VALIDATION = 3670
EIP_STATIC_RELATIVE_JUMPS = 4200
EIP_EOF_FUNCTIONS = 4750
EIP_EOF_STACK_VALIDATION = 5450

V1_EOF_EIPS = [
    EIP_EOF,
    EIP_CODE_VALIDATION,
    EIP_STATIC_RELATIVE_JUMPS,
    EIP_EOF_FUNCTIONS,
    # EIP_EOF_STACK_VALIDATION, Not implemented yet
]

V1_EOF_OPCODES: List[Op] = [
    Op.STOP,
    Op.ADD,
    Op.MUL,
    Op.SUB,
    Op.DIV,
    Op.SDIV,
    Op.MOD,
    Op.SMOD,
    Op.ADDMOD,
    Op.MULMOD,
    Op.EXP,
    Op.SIGNEXTEND,
    Op.LT,
    Op.GT,
    Op.SLT,
    Op.SGT,
    Op.EQ,
    Op.ISZERO,
    Op.AND,
    Op.OR,
    Op.XOR,
    Op.NOT,
    Op.BYTE,
    Op.SHL,
    Op.SHR,
    Op.SAR,
    Op.SHA3,
    Op.ADDRESS,
    Op.BALANCE,
    Op.ORIGIN,
    Op.CALLER,
    Op.CALLVALUE,
    Op.CALLDATALOAD,
    Op.CALLDATASIZE,
    Op.CALLDATACOPY,
    Op.CODESIZE,
    Op.CODECOPY,
    Op.GASPRICE,
    Op.EXTCODESIZE,
    Op.EXTCODECOPY,
    Op.RETURNDATASIZE,
    Op.RETURNDATACOPY,
    Op.EXTCODEHASH,
    Op.BLOCKHASH,
    Op.COINBASE,
    Op.TIMESTAMP,
    Op.NUMBER,
    Op.PREVRANDAO,
    Op.GASLIMIT,
    Op.CHAINID,
    Op.SELFBALANCE,
    Op.BASEFEE,
    Op.POP,
    Op.MLOAD,
    Op.MSTORE,
    Op.MSTORE8,
    Op.SLOAD,
    Op.SSTORE,
    Op.JUMP,
    Op.JUMPI,
    Op.PC,
    Op.MSIZE,
    Op.GAS,
    Op.JUMPDEST,
    Op.PUSH1,
    Op.PUSH2,
    Op.PUSH3,
    Op.PUSH4,
    Op.PUSH5,
    Op.PUSH6,
    Op.PUSH7,
    Op.PUSH8,
    Op.PUSH9,
    Op.PUSH10,
    Op.PUSH11,
    Op.PUSH12,
    Op.PUSH13,
    Op.PUSH14,
    Op.PUSH15,
    Op.PUSH16,
    Op.PUSH17,
    Op.PUSH18,
    Op.PUSH19,
    Op.PUSH20,
    Op.PUSH21,
    Op.PUSH22,
    Op.PUSH23,
    Op.PUSH24,
    Op.PUSH25,
    Op.PUSH26,
    Op.PUSH27,
    Op.PUSH28,
    Op.PUSH29,
    Op.PUSH30,
    Op.PUSH31,
    Op.PUSH32,
    Op.DUP1,
    Op.DUP2,
    Op.DUP3,
    Op.DUP4,
    Op.DUP5,
    Op.DUP6,
    Op.DUP7,
    Op.DUP8,
    Op.DUP9,
    Op.DUP10,
    Op.DUP11,
    Op.DUP12,
    Op.DUP13,
    Op.DUP14,
    Op.DUP15,
    Op.DUP16,
    Op.SWAP1,
    Op.SWAP2,
    Op.SWAP3,
    Op.SWAP4,
    Op.SWAP5,
    Op.SWAP6,
    Op.SWAP7,
    Op.SWAP8,
    Op.SWAP9,
    Op.SWAP10,
    Op.SWAP11,
    Op.SWAP12,
    Op.SWAP13,
    Op.SWAP14,
    Op.SWAP15,
    Op.SWAP16,
    Op.LOG0,
    Op.LOG1,
    Op.LOG2,
    Op.LOG3,
    Op.LOG4,
    Op.CREATE,
    Op.CALL,
    Op.CALLCODE,
    Op.RETURN,
    Op.DELEGATECALL,
    Op.CREATE2,
    Op.STATICCALL,
    Op.REVERT,
    Op.INVALID,
    Op.SELFDESTRUCT,
]
"""
List of all valid EOF V1 opcodes for Shanghai.
"""


# TODO: Add `Op.TLOAD`, `Op.TSTORE`, if EIP 1153 is included
if EIP_EOF_FUNCTIONS in V1_EOF_EIPS:
    V1_EOF_OPCODES += [
        Op.CALLF,
        Op.RETF,
    ]

if EIP_STATIC_RELATIVE_JUMPS in V1_EOF_EIPS:
    V1_EOF_OPCODES += [
        Op.RJUMP,
        Op.RJUMPI,
    ]


# Helper functions

ALL_VALID_CONTAINERS: List[Code | Container] = [
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
        ],
        name="single_code_section",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0x00",
            ),
        ],
        name="single_code_single_data_section",
    ),
]

# Source: EIP-3540
ALL_INVALID_CONTAINERS: List[Code | Container] = [
    Code(
        bytecode=bytes([0xEF]),
        name="incomplete_magic",
    ),
    Code(
        bytecode=bytes([0xEF, 0x00]),
        name="no_version",
    ),
    Container(
        custom_magic=0x01,
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
        ],
        name="invalid_magic_01",
    ),
    Container(
        custom_magic=0xFF,
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
        ],
        name="invalid_magic_ff",
    ),
    Container(
        custom_version=0x00,
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
        ],
        name="invalid_version_zero",
    ),
    Container(
        custom_version=LATEST_EOF_VERSION + 1,
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
        ],
        name="invalid_version_low",
    ),
    Container(
        custom_version=0xFF,
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
        ],
        name="invalid_version_high",
    ),
    Code(
        bytecode=bytes([0xEF, 0x00, 0x01]),
        name="no_version",
    ),
    Container(
        sections=[],
        name="no_sections",
    ),
    Code(
        bytecode=bytes([0xEF, 0x00, 0x01, 0x01]),
        name="no_code_section_size",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.DATA,
                data="0x00",
            ),
        ],
        name="no_code_section",
    ),
    Code(
        bytecode=bytes([0xEF, 0x00, 0x01, 0x01, 0x00]),
        name="code_section_size_incomplete",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x",
                custom_size=3,
            ),
        ],
        custom_terminator=bytes(),
        name="no_section_terminator_1",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x600000",
            ),
        ],
        custom_terminator=bytes(),
        name="no_section_terminator_2",
    ),
    Container(
        sections=[
            Section(
                custom_size=0x01,
                kind=SectionKind.CODE,
                data="0x",
            ),
        ],
        name="no_code_section_contents",
    ),
    Container(
        sections=[
            Section(
                custom_size=0x02,
                kind=SectionKind.CODE,
                data="0x00",
            ),
        ],
        name="incomplete_code_section_contents",
    ),
    Container(
        sections=[
            Section(
                custom_size=0x02,
                kind=SectionKind.CODE,
                data="0x00",
            ),
        ],
        name="incomplete_code_section_contents",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x600000",
            ),
        ],
        extra=bytes([0xDE, 0xAD, 0xBE, 0xEF]),
        name="trailing_bytes_after_code_section",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x600000",
            ),
            Section(
                kind=SectionKind.CODE,
                data="0x600000",
            ),
        ],
        name="multiple_code_sections",
        auto_type_section=False,
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x",
            ),
        ],
        name="empty_code_section",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0xDEADBEEF",
            ),
        ],
        name="empty_code_section_with_non_empty_data",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.DATA,
                data="0xDEADBEEF",
            ),
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
        ],
        name="data_section_preceding_code_section",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.DATA,
                data="0xDEADBEEF",
            ),
        ],
        name="data_section_without_code_section",
    ),
    Code(
        bytecode=bytes([0xEF, 0x00, 0x01, 0x01, 0x00, 0x02, 0x02]),
        name="no_data_section_size",
    ),
    Code(
        bytecode=bytes([0xEF, 0x00, 0x01, 0x01, 0x00, 0x02, 0x02, 0x00]),
        name="data_section_size_incomplete",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x020004",
            ),
        ],
        custom_terminator=bytes(),
        name="no_section_terminator_3",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x600000",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0xAABBCCDD",
            ),
        ],
        custom_terminator=bytes(),
        name="no_section_terminator_4",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x600000",
            ),
            Section(
                kind=SectionKind.DATA,
                data="",
                custom_size=1,
            ),
        ],
        name="no_data_section_contents",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x600000",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0xAABBCC",
                custom_size=4,
            ),
        ],
        name="data_section_contents_incomplete",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x600000",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0xAABBCCDD",
            ),
        ],
        extra=bytes([0xEE]),
        name="trailing_bytes_after_data_section",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x600000",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0xAABBCC",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0xAABBCC",
            ),
        ],
        name="multiple_data_sections",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0xAA",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0xAA",
            ),
        ],
        name="multiple_code_and_data_sections_1",
        auto_type_section=False,
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0xAA",
            ),
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
            Section(
                kind=SectionKind.DATA,
                data="0xAA",
            ),
        ],
        name="multiple_code_and_data_sections_2",
        auto_type_section=False,
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
            Section(
                kind=VERSION_MAX_SECTION_KIND + 1,
                data="0x01",
            ),
        ],
        name="unknown_section_1",
    ),
    Container(
        sections=[
            Section(
                kind=VERSION_MAX_SECTION_KIND + 1,
                data="0x01",
            ),
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
        ],
        name="unknown_section_2",
    ),
    Container(
        sections=[
            Section(
                kind=SectionKind.CODE,
                data="0x00",
            ),
            Section(
                kind=VERSION_MAX_SECTION_KIND + 1,
                data="0x",
            ),
        ],
        name="empty_unknown_section_2",
    ),
]

if EIP_CODE_VALIDATION in V1_EOF_EIPS:
    VALID_TERMINATING_OPCODES = [
        Op.STOP,
        Op.RETURN,
        Op.REVERT,
        Op.INVALID,
    ]

    if EIP_EOF_FUNCTIONS in V1_EOF_EIPS:
        VALID_TERMINATING_OPCODES.append(Op.RETF)

    for valid_opcode in VALID_TERMINATING_OPCODES:
        test_bytecode = bytes()
        # We need to push some items onto the stack so the code is valid
        # even with stack validation
        for i in range(valid_opcode.popped_stack_items):
            test_bytecode += Op.ORIGIN
        test_bytecode += valid_opcode
        ALL_VALID_CONTAINERS.append(
            Container(
                sections=[
                    Section(
                        kind=SectionKind.TYPE,
                        data=bytes.fromhex("0000") + valid_opcode.popped_stack_items.to_bytes(2, byteorder="big"),
                    ),
                    Section(
                        kind=SectionKind.CODE,
                        data=test_bytecode,
                    ),
                    Section(
                        kind=SectionKind.DATA,
                        data="0x00",
                    ),
                ],
                name=f"valid_terminating_opcode_{str(valid_opcode)}",
            ),
        )

    # Create a list of all opcodes that are not valid terminating opcodes
    INVALID_TERMINATING_OPCODES = [
        bytes([i])
        for i in range(256)
        if i not in [x.int() for x in VALID_TERMINATING_OPCODES]
    ]
    # Create containers where each invalid terminating opcode is located at the
    # end of the bytecode
    for invalid_opcode in INVALID_TERMINATING_OPCODES:
        ALL_INVALID_CONTAINERS.append(
            Container(
                sections=[
                    Section(
                        kind=SectionKind.CODE,
                        data=invalid_opcode,
                    ),
                    Section(
                        kind=SectionKind.DATA,
                        data="0x00",
                    ),
                ],
                name=f"invalid_terminating_opcode_0x{invalid_opcode.hex()}",
            ),
        )

    # Create a list of all invalid opcodes not assigned on EOF_V1
    INVALID_OPCODES = [
        bytes([i])
        for i in range(256)
        if i not in [x.int() for x in V1_EOF_OPCODES]
    ]
    # Create containers containing a valid terminating opcode, but the
    # invalid opcode somewhere in the bytecode
    for invalid_opcode in INVALID_OPCODES:
        ALL_INVALID_CONTAINERS.append(
            Container(
                sections=[
                    Section(
                        kind=SectionKind.CODE,
                        data=invalid_opcode + Op.STOP,
                    ),
                    Section(
                        kind=SectionKind.DATA,
                        data="0x00",
                    ),
                ],
                name=f"invalid_terminating_opcode_0x{invalid_opcode.hex()}",
            ),
        )

    # Create a list of all valid opcodes that require data portion immediately
    # after
    VALID_DATA_PORTION_OPCODES = [
        op for op in V1_EOF_OPCODES if op.data_portion_length > 0
    ]
    # Create an invalid EOF container where the data portion of a valid opcode
    # is truncated or terminates the bytecode
    for data_portion_opcode in VALID_DATA_PORTION_OPCODES:
        # No data portion
        ALL_INVALID_CONTAINERS.append(
            Container(
                sections=[
                    Section(
                        kind=SectionKind.CODE,
                        data=data_portion_opcode,
                    ),
                    Section(
                        kind=SectionKind.DATA,
                        data="0x00",
                    ),
                ],
                name=f"valid_truncated_opcode_{data_portion_opcode}_"
                + "no_data",
            ),
        )
        if data_portion_opcode.data_portion_length > 1:
            # Single byte as data portion
            ALL_INVALID_CONTAINERS.append(
                Container(
                    sections=[
                        Section(
                            kind=SectionKind.CODE,
                            data=data_portion_opcode + Op.STOP,
                        ),
                        Section(
                            kind=SectionKind.DATA,
                            data="0x00",
                        ),
                    ],
                    name=f"valid_truncated_opcode_{data_portion_opcode}_"
                    + "one_byte",
                ),
            )
        # Data portion complete but terminates the bytecode
        ALL_INVALID_CONTAINERS.append(
            Container(
                sections=[
                    Section(
                        kind=SectionKind.CODE,
                        data=data_portion_opcode
                        + (Op.STOP * data_portion_opcode.data_portion_length),
                    ),
                    Section(
                        kind=SectionKind.DATA,
                        data="0x00",
                    ),
                ],
                name=f"valid_truncated_opcode_{data_portion_opcode}_"
                + "terminating",
            ),
        )

    if EIP_STATIC_RELATIVE_JUMPS in V1_EOF_EIPS:

        valid_codes: List[Tuple[bytes, str]] = [
            (
                Op.RJUMP(0) + Op.STOP,
                "zero_relative_jump",
            ),
            #  (
            #      Op.RJUMP(-3) + Op.STOP,
            #      "minus_three_relative_jump",
            #  ),
            #  (
            #      Op.RJUMP(1) + Op.STOP + Op.JUMPDEST + Op.STOP,
            #      "one_relative_jump_to_jumpdest",
            #  ),
            #  (
            #      Op.RJUMP(1) + Op.STOP + Op.STOP,
            #      "one_relative_jump_to_stop",
            #  ),
        ]

        invalid_codes: List[Tuple[bytes, str]] = [
            (
                Op.RJUMP(-1) + Op.STOP,
                "minus_one_relative_jump",
            ),
            (
                Op.RJUMP(-2) + Op.STOP,
                "minus_two_relative_jump",
            ),
            (
                Op.RJUMP(1) + Op.PUSH0 + Op.STOP + Op.STOP,
                "one_relative_jump_to_push_data",
            ),
            (
                Op.RJUMP(1) + Op.STOP,
                "one_relative_jump_outside_of_code",
            ),
            (
                Op.RJUMP(-4) + Op.STOP,
                "minus_4_relative_jump_outside_of_code",
            ),
        ]

        for valid_code in valid_codes:
            ALL_VALID_CONTAINERS.append(
                Container(
                    sections=[
                        Section(
                            kind=SectionKind.CODE,
                            data=valid_code[0],
                        ),
                        Section(
                            kind=SectionKind.DATA,
                            data="0x00",
                        ),
                    ],
                    name=f"valid_rjump_{valid_code[1]}",
                ),
            )

        for invalid_code in invalid_codes:
            ALL_INVALID_CONTAINERS.append(
                Container(
                    sections=[
                        Section(
                            kind=SectionKind.CODE,
                            data=invalid_code[0],
                        ),
                        Section(
                            kind=SectionKind.DATA,
                            data="0x00",
                        ),
                    ],
                    name=f"invalid_rjump_{invalid_code[1]}",
                ),
            )

        if EIP_EOF_STACK_VALIDATION in V1_EOF_EIPS:
            # TODO: Invalid due to stack underflow on relative jump
            pass
else:
    pass

# TODO: Add test case for relative jumps on legacy code


if EIP_EOF_FUNCTIONS in V1_EOF_EIPS:
    """
    EIP-4750 Valid and Invalid Containers
    """
    ALL_VALID_CONTAINERS += [
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
            ],
            name="eip_4750_single_code_section",
            force_type_section=True,
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
                Section(
                    kind=SectionKind.DATA,
                    data="0x00",
                ),
            ],
            name="eip_4750_single_code_single_data_section",
            force_type_section=True,
        ),
        #  Container(
        #      sections=[
        #          Section(
        #              kind=SectionKind.TYPE,
        #              data=bytes.fromhex("00000000") * 1024
        #          ),
        #          Section(
        #              kind=SectionKind.CODE,
        #              data="0x00",
        #          )
        #      ]
        #      * 1024,
        #      name="eip_4750_max_code_sections_1024",
        #  ),
        #  Container(
        #      sections=(
        #          [
        #              Section(
        #                  kind=SectionKind.CODE,
        #                  data="0x00",
        #              )
        #          ]
        #          * 1024
        #      )
        #      + [
        #          Section(
        #              kind=SectionKind.DATA,
        #              data="0x00",
        #          ),
        #      ],
        #      name="eip_4750_max_code_sections_1024_and_data",
        #  ),
        #  Container(
        #      sections=[
        #          Section(
        #              kind=SectionKind.CODE,
        #              data="0x00",
        #          ),
        #          Section(
        #              kind=SectionKind.CODE,
        #              data="0x00",
        #              code_inputs=255,
        #              code_outputs=255,
        #          ),
        #      ],
        #      name="eip_4750_multiple_code_section_max_inputs_max_outputs",
        #  ),
    ]

    ALL_INVALID_CONTAINERS += [
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                    code_inputs=1,
                ),
            ],
            name="eip_4750_single_code_section_non_zero_inputs",
            force_type_section=True,
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                    code_outputs=1,
                ),
            ],
            name="eip_4750_single_code_section_non_zero_outputs",
            force_type_section=True,
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                    code_inputs=1,
                ),
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
            ],
            name="eip_4750_multiple_code_section_non_zero_inputs",
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                    code_outputs=1,
                ),
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
            ],
            name="eip_4750_multiple_code_section_non_zero_outputs",
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.DATA,
                    data="0xAA",
                ),
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
            ],
            name="eip_4750_data_section_before_code_with_type",
            force_type_section=True,
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
                Section(
                    kind=SectionKind.DATA,
                    data="0x00",
                    force_type_listing=True,
                ),
            ],
            name="eip_4750_data_section_listed_in_type",
            force_type_section=True,
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                )
            ]
            * 1025,
            name="eip_4750_code_sections_above_1024",
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
                Section(
                    kind=SectionKind.DATA,
                    data="0xAA",
                ),
                Section(
                    kind=SectionKind.DATA,
                    data="0xAA",
                ),
            ],
            name="eip_4750_multiple_code_and_data_sections_1",
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
                Section(
                    kind=SectionKind.DATA,
                    data="0xAA",
                ),
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
                Section(
                    kind=SectionKind.DATA,
                    data="0xAA",
                ),
            ],
            name="eip_4750_multiple_code_and_data_sections_2",
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.TYPE,
                    data="0x00",
                ),
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
            ],
            name="eip_4750_single_code_section_incomplete_type",
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.TYPE,
                    custom_size=2,
                    data="0x00",
                ),
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
            ],
            name="eip_4750_single_code_section_incomplete_type_2",
        ),
        Container(
            sections=[
                Section(
                    kind=SectionKind.TYPE,
                    data="0x000000",
                ),
                Section(
                    kind=SectionKind.CODE,
                    data="0x00",
                ),
            ],
            name="eip_4750_single_code_section_oversized_type",
        ),
    ]


@test_from(EOF_FORK_NAME)
def test_legacy_initcode_valid_eof_v1_contract(_):
    """
    Test creating various types of valid EOF V1 contracts using legacy
    initcode and a contract creating transaction.
    """
    tx_created_contract = compute_create_address(TestAddress, 0)
    create_opcode_contract = compute_create_address(0x100, 0)

    env = Environment()

    create_initcode_from_calldata = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            let result := create(0, 0, calldatasize())
            sstore(result, 1)
        }
        """
    )
    create2_initcode_from_calldata = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            let result := create2(0, 0, calldatasize(), 0)
            sstore(result, 1)
        }
        """
    )

    pre = {
        TestAddress: Account(
            balance=1000000000000000000000,
            nonce=0,
        ),
        to_address(0x100): Account(
            code=create_initcode_from_calldata,
        ),
        to_address(0x200): Account(
            code=create2_initcode_from_calldata,
        ),
    }

    post = {
        tx_created_contract: Account(),
        create_opcode_contract: Account(),
    }
    tx_create_contract = Transaction(
        nonce=0,
        to=None,
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )
    tx_create_opcode = Transaction(
        nonce=1,
        to=to_address(0x100),
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )
    tx_create2_opcode = Transaction(
        nonce=2,
        to=to_address(0x200),
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )

    for container in ALL_VALID_CONTAINERS:
        legacy_initcode = Initcode(deploy_code=container)
        tx_create_contract.data = legacy_initcode
        tx_create_opcode.data = legacy_initcode
        tx_create2_opcode.data = legacy_initcode
        post[tx_created_contract].code = container
        post[create_opcode_contract].code = container
        create2_opcode_contract = compute_create2_address(
            0x200, 0, legacy_initcode.assemble()
        )
        post[create2_opcode_contract] = Account(code=container)
        yield StateTest(
            env=env,
            pre=pre,
            post=post,
            txs=[
                tx_create_contract,
                tx_create_opcode,
                tx_create2_opcode,
            ],
            name=container.name if container.name is not None else "unknown_container",
        )
        del post[create2_opcode_contract]


@test_from(EOF_FORK_NAME)
def test_legacy_initcode_invalid_eof_v1_contract(_):
    """
    Test creating various types of invalid EOF V1 contracts using legacy
    initcode, a contract creating transaction,
    and the CREATE opcode.
    """
    tx_created_contract = compute_create_address(TestAddress, 0)
    create_opcode_contract = compute_create_address(0x100, 0)

    env = Environment()

    create_initcode_from_calldata = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            let result := create(0, 0, calldatasize())
            sstore(result, 1)
        }
        """
    )
    create2_initcode_from_calldata = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            let result := create2(0, 0, calldatasize(), 0)
            sstore(result, 1)
        }
        """
    )

    pre = {
        TestAddress: Account(
            balance=1000000000000000000000,
            nonce=0,
        ),
        to_address(0x100): Account(
            code=create_initcode_from_calldata,
        ),
        to_address(0x200): Account(
            code=create2_initcode_from_calldata,
        ),
    }

    post = {
        to_address(0x100): Account(
            storage={
                0: 1,
            }
        ),
        tx_created_contract: Account.NONEXISTENT,
        create_opcode_contract: Account.NONEXISTENT,
    }

    tx_create_contract = Transaction(
        nonce=0,
        to=None,
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )
    tx_create_opcode = Transaction(
        nonce=1,
        to=to_address(0x100),
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )
    tx_create2_opcode = Transaction(
        nonce=2,
        to=to_address(0x200),
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )

    for container in ALL_INVALID_CONTAINERS:
        legacy_initcode = Initcode(deploy_code=container)
        tx_create_contract.data = legacy_initcode
        tx_create_opcode.data = legacy_initcode
        tx_create2_opcode.data = legacy_initcode
        create2_opcode_contract = compute_create2_address(
            0x200, 0, legacy_initcode.assemble()
        )
        post[create2_opcode_contract] = Account.NONEXISTENT
        yield StateTest(
            env=env,
            pre=pre,
            post=post,
            txs=[
                tx_create_contract,
                tx_create_opcode,
                tx_create2_opcode,
            ],
            name=container.name if container.name is not None else "unknown_container",
        )
        del post[create2_opcode_contract]


# TODO: Max initcode as specified on EIP-3860
