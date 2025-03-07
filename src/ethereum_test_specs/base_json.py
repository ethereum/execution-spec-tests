"""Base class to parse test cases written in JSON/YAML."""

from abc import abstractmethod
from functools import reduce
from itertools import count
from os import path
from pathlib import Path
from typing import Callable, ClassVar, Dict, Generator, Iterator, List, Optional, Sequence

import pytest


class BaseJSONTest(BaseModel):
    """Represents a base class that reads cases from JSON/YAML files."""

    pass
