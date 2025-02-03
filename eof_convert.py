import json
import os
import shutil
import sys


def exception_to_pytest(exception):
    if exception is None:
        return "None"

    match exception:
        case _ if exception.startswith("EOFException."):
            return exception
        case "EOF_MaxStackHeightExceeded":
            return "EOFException.MAX_STACK_HEIGHT_ABOVE_LIMIT"
        case "EOF_InvalidMaxStackHeight":
            return "EOFException.INVALID_MAX_STACK_HEIGHT"
        case "EOF_ConflictingStackHeight":
            return "EOFException.STACK_HEIGHT_MISMATCH"
        case "EOF_InvalidPrefix":
            return "EOFException.INVALID_MAGIC"
        case "EOF_UnknownVersion":
            return "EOFException.INVALID_VERSION"
        case "EOF_UndefinedInstruction":
            return "EOFException.UNDEFINED_INSTRUCTION"
        case "EOF_StackUnderflow":
            return "EOFException.STACK_UNDERFLOW"
        case "EOF_StackOverflow":
            return "EOFException.STACK_OVERFLOW"
        case "EOF_InvalidFirstSectionType":
            return "EOFException.INVALID_FIRST_SECTION_TYPE"
        case "EOF_InvalidCodeSectionIndex":
            return "EOFException.INVALID_CODE_SECTION_INDEX"
        case "EOF_InvalidJumpDestination":
            return "EOFException.INVALID_RJUMP_DESTINATION"
        case "EOF_TypeSectionMissing":
            return "EOFException.MISSING_TYPE_HEADER"
        case "EOF_InvalidNumberOfOutputs":
            return "EOFException.STACK_HIGHER_THAN_OUTPUTS"
        case "EOF_InvalidNumberOfInputs":
            return "EOFException.INVALID_INPUTS_NUMBER"
        case "EOF_UnreachableCode":
            return "EOFException.UNREACHABLE_INSTRUCTIONS"
        case "EOF_InvalidCodeTermination":
            return "EOFException.MISSING_STOP_OPCODE"
        case "EOF_CodeSectionMissing":
            return "EOFException.MISSING_CODE_HEADER"
        case "EOF_InvalidNonReturningFlag":
            return "EOFException.INVALID_NON_RETURNING_FLAG"
        case "err: toplevel_container_truncated":
            return "EOFException.TOPLEVEL_CONTAINER_TRUNCATED"
        case "EOF_DataSectionMissing":
            return "EOFException.MISSING_DATA_SECTION"
        case "EOF_HeaderTerminatorMissing":
            return "EOFException.MISSING_TERMINATOR"
        case "EOF_InvalidSectionBodiesSize":
            return "EOFException.INVALID_SECTION_BODIES_SIZE"
        case "EOF_InvalidTypeSectionSize":
            return "EOFException.INVALID_TYPE_SECTION_SIZE"
        case "EOF_IncompleteSectionNumber":
            return "EOFException.INCOMPLETE_SECTION_NUMBER"
        case "EOF_SectionHeadersNotTerminated":
            return "EOFException.MISSING_HEADERS_TERMINATOR"
        case "EOF_IncompleteSectionSize":
            return "EOFException.INCOMPLETE_SECTION_SIZE"
        case "EOF_ZeroSectionSize":
            return "EOFException.ZERO_SECTION_SIZE"
        case "EOF_TooManyCodeSections":
            return "EOFException.TOO_MANY_CODE_SECTIONS"
        case "EOF_TooManyContainerSections":
            return "EOFException.TOO_MANY_CONTAINERS"
        case "EOF_TruncatedImmediate":
            return "EOFException.TRUNCATED_INSTRUCTION"
        case "EOF_InvalidContainerSectionIndex":
            return "EOFException.INVALID_CONTAINER_SECTION_INDEX"
        case "EOF_EofCreateWithTruncatedContainer":
            return "EOFException.EOFCREATE_WITH_TRUNCATED_CONTAINER"
        case "EOF_InputsOutputsNumAboveLimit":
            return "EOFException.INPUTS_OUTPUTS_NUM_ABOVE_LIMIT"
        case "EOF_JumpfDestinationIncompatibleOutputs":
            return "EOFException.JUMPF_DESTINATION_INCOMPATIBLE_OUTPUTS"
        case _:
            print(f"# {exception}")
            # return "EOFException.DEFAULT_EXCEPTION"
            assert False, f"Unknown exception: {exception}"


def convert_json_to_pytest(json_file, output_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    test_cases = next(iter(data.values()))["vectors"]

    with open(output_file, 'w') as f:
        f.write("import pytest\n")
        f.write("from ethereum_test_exceptions import EOFException\n")
        f.write("from ethereum_test_types.eof.v1 import Container, Section\n\n")

        f.write("REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'\n")
        f.write("REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'\n\n")

        f.write("@pytest.mark.parametrize(\n")
        f.write("    'container',\n")
        f.write("    [\n")

        for name, details in test_cases.items():
            raw_bytes = details.get("code")[2:]
            exception = details["results"]["Osaka"].get("exception", None)
            f.write(f"        Container(\n")
            f.write(f"            name='{name}',\n")
            f.write(f"            raw_bytes=\"{raw_bytes}\",\n")
            if exception is not None:
                f.write(f"            validity_error={exception_to_pytest(exception)},\n")
            f.write(f"        ),\n")

        f.write("    ],\n")
        f.write("    ids=lambda x: x.name,\n")
        f.write(")\n")
        f.write("def test_eof_validation(eof_test, container):\n")
        f.write("    eof_test(container=container)\n")

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # Empty the output directory before writing files to it
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

for root, _, files in os.walk(input_dir):
    for json_file in files:
        if json_file.endswith('.json'):
            print(f"Converting {json_file}")
            relative_path = os.path.relpath(root, input_dir)
            output_file_name = os.path.join(relative_path, os.path.splitext(json_file)[0] + '.py').replace('/', '_')
            output_file = os.path.join(output_dir, output_file_name)
            convert_json_to_pytest(os.path.join(root, json_file), output_file)
