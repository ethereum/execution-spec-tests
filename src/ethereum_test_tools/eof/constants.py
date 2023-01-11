"""
EVM Object Format generic constants.
Applicable to all EOF versions.
"""
EOF_MAGIC = bytes.fromhex("00")
"""
The second byte found on every EOF formatted contract, which was chosen to
avoid clashes with three contracts which were deployed on Mainnet.
"""
EOF_HEADER_TERMINATOR = bytes.fromhex("00")
"""
Byte that terminates the header of the EOF format.
"""
LATEST_EOF_VERSION = 0x01
"""
Latest existing EOF version.
"""
