from __future__ import annotations
import collections
import dataclasses
from typing import (
    Any,
    ForwardRef,
    NamedTuple,
    Type,
    TypedDict,
    TYPE_CHECKING,
    Protocol,
)

import attrs
import msgspec
import pydantic
import pydantic_core

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


class TypedDictProtocol(Protocol):
    __annotations__: dict[str, Any]
    __name__: str

    def __optional_keys__(self) -> frozenset[str]:
        ...

    def __required_keys__(self) -> frozenset[str]:
        ...

    def __total__(self) -> bool:
        ...


class NoDefaultType:
    def __repr__(self):
        return type(self).__name__

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self))


NO_DEFAULT = NoDefaultType()
MISSING_TYPES = [
    attrs.NOTHING,
    dataclasses.MISSING,
    msgspec.NODEFAULT,
    pydantic_core.PydanticUndefined,
    None,
]


"""
TODO:
- handle optionally providing type annotations
"""


def no_default_if_misc_missing(o):
    """Returns `NO_DEFAULT` if `o` is one of
    - `attrs.NOTHING`
    - `dataclasses.MISSING`
    - `msgspec.NODEFAULT`
    - `pydantic_core.PydanticUndefined`
    - `None`
    otherwise it returns `o`
    """
    return NO_DEFAULT if any(o is mt for mt in MISSING_TYPES) else o


def resolve_if_forward_ref(t):
    """If `t` is a `ForwardRef` it returns an evaluated version of it, otherwise
    it returns `t`
    """
    # TODO: do this only for "base" types
    # TODO: I might be shooting myself in the foot with this?
    if isinstance(t, ForwardRef):
        return t._evaluate(globals(), locals(), frozenset())
    return t


class AttributeInfo(NamedTuple):
    name: str
    type: type | None
    default: Any | NoDefaultType = NO_DEFAULT

    @classmethod
    def from_attrs_attribute(cls, attribute: attrs.Attribute) -> AttributeInfo:
        return cls(
            name=attribute.name,
            type=attribute.type,
            default=no_default_if_misc_missing(attribute.default),
        )

    @classmethod
    def from_dataclasses_field(cls, field: dataclasses.Field) -> AttributeInfo:
        return cls(
            name=field.name,
            type=field.type,
            default=no_default_if_misc_missing(field.default),
        )

    @classmethod
    def from_msgspec_field_info(
        cls, field_info: msgspec.structs.FieldInfo
    ) -> AttributeInfo:
        return cls(
            name=field_info.name,
            type=field_info.type,
            default=no_default_if_misc_missing(field_info.default),
        )

    def to_attrs_attribute(self) -> attrs.Attribute:
        kwargs: dict[str, Any] = {
            "type": self.type,
            "default": (
                self.default if self.default is not NO_DEFAULT else attrs.NOTHING
            ),
        }
        return attrs.field(**kwargs)


class DataModel(NamedTuple):
    name: str
    attributes: list[AttributeInfo]

    @classmethod
    def from_attrs(cls, dm: Type[attrs.AttrsInstance]) -> DataModel:
        return cls(
            name=dm.__name__,
            attributes=[
                AttributeInfo.from_attrs_attribute(a) for a in attrs.fields(dm)
            ],
        )

    @classmethod
    def from_dataclass(cls, dm: Type[DataclassInstance]) -> DataModel:
        return cls(
            name=dm.__name__,
            attributes=[
                AttributeInfo.from_dataclasses_field(f) for f in dataclasses.fields(dm)
            ],
        )

    @classmethod
    def from_msgspec(cls, dm: Type[msgspec.Struct]) -> DataModel:
        return cls(
            name=dm.__name__,
            attributes=[
                AttributeInfo.from_msgspec_field_info(fi)
                for fi in msgspec.structs.fields(dm)
            ],
        )

    @classmethod
    def from_namedtuple(cls, dm: Type[NamedTuple]) -> DataModel:
        return cls(
            name=dm.__name__,
            attributes=[
                AttributeInfo(
                    name=f,
                    type=resolve_if_forward_ref(dm.__annotations__.get(f)),
                    default=no_default_if_misc_missing(dm._field_defaults.get(f)),
                )
                for f in dm._fields
            ],
        )

    @classmethod
    def from_pydantic(cls, dm: Type[pydantic.BaseModel]) -> DataModel:
        return cls(
            name=dm.__name__,
            attributes=[
                AttributeInfo(
                    name=name,
                    type=resolve_if_forward_ref(fi.annotation),
                    default=no_default_if_misc_missing(fi.default),
                )
                for name, fi in dm.model_fields.items()
            ],
        )

    @classmethod
    def from_typeddict(cls, dm: Type[TypedDictProtocol]) -> DataModel:
        return cls(
            name=dm.__name__,
            attributes=[
                AttributeInfo(
                    name=name,
                    type=no_default_if_misc_missing(type_),
                )
                for name, type_ in dm.__annotations__.items()
            ],
        )

    def to_attrs(self):
        return attrs.make_class(
            name=self.name,
            attrs={a.name: a.to_attrs_attribute() for a in self.attributes},
        )

    def to_dataclass(self):
        dataclass_fields = []
        for a in self.attributes:
            if a.default is NO_DEFAULT:
                dataclass_fields.append((a.name, a.type))
            else:
                dataclass_fields.append(
                    (
                        a.name,
                        a.type,
                        dataclasses.field(default=a.default),
                    )
                )
        return dataclasses.make_dataclass(self.name, dataclass_fields)

    def to_msgspec(self):
        msgspec_fields = [
            (a.name, a.type)
            if a.default is NO_DEFAULT
            else (a.name, a.type, msgspec.field(default=a.default))
            for a in self.attributes
        ]
        return msgspec.defstruct(self.name, msgspec_fields)

    def to_namedtuple(self):
        return collections.namedtuple(self.name, [a.name for a in self.attributes])

    def to_pydantic(self):
        pydantic_fields = {}
        for attribute in self.attributes:
            default = (
                pydantic_core.PydanticUndefined
                if attribute.default is NO_DEFAULT
                else attribute.default
            )
            pydantic_fields[attribute.name] = (
                attribute.type,
                pydantic.fields.Field(default=default),
            )
        return pydantic.create_model(self.name, **pydantic_fields)

    def to_typeddict(self):
        return TypedDict(self.name, {a.name: a.type for a in self.attributes})
