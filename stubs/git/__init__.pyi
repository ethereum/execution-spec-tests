from typing import Any

class Repo:
    def __init__(self, path: str = ..., search_parent_directories: bool = ...) -> None: ...
    @property
    def head(self) -> Any: ...

class InvalidGitRepositoryError(Exception):
    pass
