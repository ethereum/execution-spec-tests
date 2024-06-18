"""
Types used in the Ethereum test fork module.
"""


from enum import Enum, auto


class EVMCodeType(Enum):
    """
    Enum representing the type of EVM code that is supported in a given fork.
    """

    LEGACY = auto()
    EOF_V1 = auto()

    def __str__(self) -> str:
        """
        Return the name of the EVM code type.
        """
        return self.name
