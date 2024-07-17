from __future__ import annotations
import dataclasses
from typing import Any, NamedTuple, Type

import attrs
import msgspec


class NoDefault:
    def __repr__(self):
        return self.__class__.__name__

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self))


NO_DEFAULT = NoDefault()
MISSING_TYPES = [
    attrs.NOTHING,
    dataclasses.MISSING,
    msgspec.NODEFAULT,
    None,
]


def no_default_if_misc_missing(o):
    """Returns `NO_DEFAULT` if `o` is one of
    - `attrs.NOTHING`
    - `dataclasses.MISSING`
    - `msgspec.NODEFAULT`
    - `None`
    otherwise it returns `o`
    """
    return NO_DEFAULT if any(o is mt for mt in MISSING_TYPES) else o


class AttributeInfo(NamedTuple):
    name: str
    type: Type | None
    default: Any

    @classmethod
    def from_attrs_attribute(cls, attribute: attrs.Attribute) -> AttributeInfo:
        return cls(
            attribute.name,
            attribute.type,
            no_default_if_misc_missing(attribute.default),
        )

    @classmethod
    def from_dataclasses_field(cls, field: dataclasses.Field) -> AttributeInfo:
        return cls(field.name, field.type, no_default_if_misc_missing(field.default))

    @classmethod
    def from_msgspec_field_info(
        cls, field_info: msgspec.structs.FieldInfo
    ) -> AttributeInfo:
        return cls(
            field_info.name,
            field_info.type,
            no_default_if_misc_missing(field_info.default),
        )


class DataModel(NamedTuple):
    name: str
    attributes: list[AttributeInfo] = []

    @classmethod
    def from_attrs(cls, dm) -> DataModel:
        dm_class = dm.__class__
        return cls(
            name=dm_class.__name__,
            attributes=[
                AttributeInfo.from_attrs_attribute(a) for a in attrs.fields(dm_class)
            ],
        )

    @classmethod
    def from_dataclass(cls, dm) -> DataModel:
        dm_class = dm.__class__
        return cls(
            name=dm_class.__name__,
            attributes=[
                AttributeInfo.from_dataclasses_field(f)
                for f in dataclasses.fields(dm_class)
            ],
        )

    @classmethod
    def from_msgspec(cls, dm) -> DataModel:
        dm_class = dm.__class__
        return cls(
            name=dm_class.__name__,
            attributes=[
                AttributeInfo.from_msgspec_field_info(fi)
                for fi in msgspec.structs.fields(dm_class)
            ],
        )

    @classmethod
    def from_namedtuple(cls, dm) -> DataModel:
        dm_class = dm.__class__
        return cls(
            name=dm_class.__name__,
            attributes=[
                AttributeInfo(
                    name=f,
                    type=dm_class.__annotations__.get(f),
                    default=no_default_if_misc_missing(dm_class._field_defaults.get(f)),
                )
                for f in dm_class._fields
            ],
        )
