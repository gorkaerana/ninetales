from pydantic import BaseModel, Field, create_model


class A(BaseModel):
    a1: str
    a2: int = 5
    a3: int = Field(default=5)


# TODO: support all args and kwargs
B = create_model("B", b1=(str, ...), b2=(int, 5))
