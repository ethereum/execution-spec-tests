"""Hive instance information structures."""

from typing import List

from pydantic import BaseModel

from ethereum_test_base_types import CamelModel


class ClientInfo(BaseModel):
    """Client information."""

    client: str
    nametag: str
    dockerfile: str
    build_args: dict[str, str]


class HiveInfo(CamelModel):
    """Hive instance information."""

    command: List[str]
    client_file: List[ClientInfo]
