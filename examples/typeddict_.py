from typing import TypedDict


# Right hand side values not allowed for TypedDict
class A(TypedDict):
    a1: str
    a2: int


B = TypedDict("B", {"b1": str, "b2": int})
