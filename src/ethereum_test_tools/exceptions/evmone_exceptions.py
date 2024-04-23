"""
Evmone eof exceptions ENUM -> str mapper
"""

from .exceptions import EOFException


class EvmoneExceptionParser:
    """
    Translate known exceptions into error strings returned by evmone
    """

    # MUST remain 1:1  both key and values unique for reverse search
    message_map = {
        # TODO EVMONE need to differentiate when the section is missing in the header or body
        EOFException.MISSING_STOP_OPCODE: "err: no_terminating_instruction",
        EOFException.MISSING_CODE_HEADER: "err: code_section_missing",
        EOFException.MISSING_TYPE_HEADER: "err: type_section_missing",
        # TODO EVMONE this exceptions are too similar, this leeds to ambiguity
        EOFException.MISSING_TERMINATOR: "err: header_terminator_missing",
        EOFException.MISSING_HEADERS_TERMINATOR: "err: section_headers_not_terminated",
        EOFException.INVALID_VERSION: "err: eof_version_unknown",
        EOFException.INVALID_MAGIC: "err: invalid_prefix",
        EOFException.INVALID_FIRST_SECTION_TYPE: "err: invalid_first_section_type",
        EOFException.INVALID_SECTION_BODIES_SIZE: "err: invalid_section_bodies_size",
        EOFException.INVALID_TYPE_SIZE: "err: invalid_type_section_size",
        EOFException.INCOMPLETE_SECTION_SIZE: "err: incomplete_section_size",
        EOFException.INCOMPLETE_SECTION_NUMBER: "err: incomplete_section_number",
        EOFException.TOO_MANY_CODE_SECTIONS: "err: too_many_code_sections",
        EOFException.ZERO_SECTION_SIZE: "err: zero_section_size",
    }

    # Reverse the message_map to create a new dictionary where values become keys
    reverse_message_map = {v: k for k, v in message_map.items()}

    def __init__(self):
        pass

    def parse_exception(self, exception: EOFException) -> str:
        """Takes an EOFException and returns a formatted string."""
        message = self.message_map.get(
            exception, f"EvmoneExceptionParser: Missing string for {exception}"
        )
        return message

    def rev_parse_exception(self, exception_string: str) -> EOFException:
        """Takes a string and tires to find matching exception"""
        exception = self.reverse_message_map.get(
            exception_string, EOFException.UNDEFINED_EXCEPTION
        )
        return exception
