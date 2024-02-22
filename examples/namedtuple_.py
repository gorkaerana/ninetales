from collections import namedtuple
from typing import NamedTuple


class A(NamedTuple):
    a1: str
    a2: int = 5


B = NamedTuple("B", [("b1", str), ("b2", int)])
C = namedtuple("C", ["b1", "b2"])
