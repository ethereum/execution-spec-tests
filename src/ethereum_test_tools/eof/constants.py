"""
EVM Object Format generic constants.
Applicable to all EOF versions.
"""
EOF_MAGIC = bytes([0])
"""
The second byte found on every EOF formatted contract, which was chosen to
avoid clashes with three contracts which were deployed on Mainnet.
"""
EOF_HEADER_TERMINATOR = bytes([0])
"""
Byte that terminates the header of the EOF format.
"""
LATEST_EOF_VERSION = 1
"""
Latest existing EOF version.
"""
VERSION_BYTE_LENGTH = 1
"""
Length of the version byte.
"""
