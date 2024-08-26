class Witness:
    pass


def vkt_chunkify(bytecode):
    """
    Return the chunkification of the provided bytecode.
    """
    # TODO(verkle):
    #   Must call `evm transition verkle-chunkify-code <bytecode-hex>` which returns a hex of
    #   the chunkified code. The returned byte length is a multiple of 32. `code_chunks` must be
    #   a list of 32-byte chunks (i.e: partition the returned bytes into 32-byte bytes)
    code_chunks: list[bytes] = []

    return code_chunks
