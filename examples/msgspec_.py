from msgspec import Struct, field


class A(Struct):
    a1: str
    a2: int = 5
    a3: int = field(default=5)
