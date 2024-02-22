from dataclasses import dataclass, make_dataclass, field


@dataclass
class A:
    a1: str
    a2: int = 5
    a3: int = field(default=5)


# TODO: support all args and kwargs
B = make_dataclass("B", [("b1", str), ("b2", int, 5), ("b3", int, field(default=5))])
