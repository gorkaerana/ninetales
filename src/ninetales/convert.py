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
        return cls(
            dm.__class__.__name__,
            [AttributeInfo.from_attrs_attribute(a) for a in attrs.fields(dm.__class__)],
        )

    @classmethod
    def from_dataclass(cls, dm) -> DataModel:
        return cls(
            dm.__class__.__name__,
            [
                AttributeInfo.from_dataclasses_field(f)
                for f in dataclasses.fields(dm.__class__)
            ],
        )

    @classmethod
    def from_msgspec(cls, dm) -> DataModel:
        return cls(
            dm.__class__.__name__,
            [
                AttributeInfo.from_msgspec_field_info(fi)
                for fi in msgspec.structs.fields(dm.__class__)
            ],
        )
