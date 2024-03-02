import dataclasses
from dataclasses import dataclass, make_dataclass, field


@dataclasses.dataclass(
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=False,
    match_args=True,
    kw_only=False,
    slots=False,
    # weakref_slot=False,
)
class A1:
    a1: str
    a2: int = 5
    a3: int = field(default=5)


@dataclass(
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=False,
    match_args=True,
    kw_only=False,
    slots=False,
    # weakref_slot=False,
)
class A2:
    a1: str
    a2: int = 5
    a3: int = field(default=5)


@dataclass
class A3:
    a1: str
    a2: int = 5
    a3: int = field(default=5)


@dataclasses.dataclass
class A4:
    a1: str
    a2: int = 5
    a3: int = field(default=5)


# TODO: support all args and kwargs
B1 = dataclasses.make_dataclass(
    "B1", [("b1", str), ("b2", int, 5), ("b3", int, field(default=5))]
)
B2 = make_dataclass("B2", [("b1", str), ("b2", int, 5), ("b3", int, field(default=5))])
