from attrs import define, make_class, field


@define
class A:
    a1: str
    a2: int = 5
    a3: int = field(default=5)


# TODO: support all args and kwargs
B = make_class("B", ["b1", "b2"])

C = make_class("C", {"c1": field(type=str, default=5)})
