from __future__ import annotations
import collections
import dataclasses
from typing import Any, ForwardRef, NamedTuple, Type, TYPE_CHECKING

import attrs
import msgspec
import pydantic
import pydantic_core

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


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
    type: Type | None
    default: Any | NoDefaultType

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


class DataModel(NamedTuple):
    name: str
    attributes: list[AttributeInfo]

    @classmethod
    def from_attrs(cls, dm: attrs.AttrsInstance) -> DataModel:
        dm_class = type(dm)
        return cls(
            name=dm_class.__name__,
            attributes=[
                AttributeInfo.from_attrs_attribute(a) for a in attrs.fields(dm_class)
            ],
        )

    @classmethod
    def from_dataclass(cls, dm: DataclassInstance) -> DataModel:
        dm_class = type(dm)
        return cls(
            name=dm_class.__name__,
            attributes=[
                AttributeInfo.from_dataclasses_field(f)
                for f in dataclasses.fields(dm_class)
            ],
        )

    @classmethod
    def from_msgspec(cls, dm: msgspec.Struct) -> DataModel:
        dm_class = type(dm)
        return cls(
            name=dm_class.__name__,
            attributes=[
                AttributeInfo.from_msgspec_field_info(fi)
                for fi in msgspec.structs.fields(dm_class)
            ],
        )

    @classmethod
    def from_namedtuple(cls, dm: NamedTuple) -> DataModel:
        dm_class = type(dm)
        return cls(
            name=dm_class.__name__,
            attributes=[
                AttributeInfo(
                    name=f,
                    type=resolve_if_forward_ref(dm_class.__annotations__.get(f)),
                    default=no_default_if_misc_missing(dm_class._field_defaults.get(f)),
                )
                for f in dm_class._fields
            ],
        )

    @classmethod
    def from_pydantic(cls, dm: pydantic.BaseModel) -> DataModel:
        dm_class = type(dm)
        return cls(
            name=dm_class.__name__,
            attributes=[
                AttributeInfo(
                    name=name,
                    type=fi.annotation,
                    default=no_default_if_misc_missing(fi.default),
                )
                for name, fi in dm_class.model_fields.items()
            ],
        )

    def to_attrs(self):
        attrs_attributes = {}
        for a in self.attributes:
            attrs_kwargs = {"type": a.type}
            if a.default is not NO_DEFAULT:
                attrs_kwargs["default"] = a.default
            attrs_attributes[a.name] = attrs.field(**attrs_kwargs)
        return attrs.make_class(name=self.name, attrs=attrs_attributes)

    def to_dataclass(self):
        dataclass_fields = [
            (a.name, a.type)
            if a.default is NO_DEFAULT
            else (a.name, a.type, dataclasses.field(default=a.default))
            for a in self.attributes
        ]
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
        return pydantic.create_model(
            self.name,
            **{
                a.name: (
                    a.type,
                    pydantic.fields.Field(
                        default=(
                            pydantic_core.PydanticUndefined
                            if a.default is pydantic_core.PydanticUndefined
                            else a.default
                        ),
                    ),
                )
                for a in self.attributes
            },
        )
