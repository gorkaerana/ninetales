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


class AttributeInfo(NamedTuple):
    name: str
    type: Type | None
    default: Any

    @classmethod
    def from_attrs_attribute(cls, attribute: attrs.Attribute) -> AttributeInfo:
        return cls(
            attribute.name,
            attribute.type,
            NO_DEFAULT if (d := attribute.default) is attrs.NOTHING else d,
        )

    @classmethod
    def from_dataclasses_field(cls, field: dataclasses.Field) -> AttributeInfo:
        return cls(
            field.name,
            field.type,
            NO_DEFAULT if (d := field.default) is dataclasses.MISSING else d,
        )

    @classmethod
    def from_msgspec_field_info(
        cls, field_info: msgspec.structs.FieldInfo
    ) -> AttributeInfo:
        return cls(
            field_info.name,
            field_info.type,
            NO_DEFAULT if (d := field_info.default) is msgspec.NODEFAULT else d,
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
                    default=(
                        NO_DEFAULT
                        if ((d := dm_class._field_defaults.get(f)) is None)
                        else d
                    ),
                )
                for f in dm_class._fields
            ],
        )
