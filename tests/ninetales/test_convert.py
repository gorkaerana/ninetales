import dataclasses
from typing import NamedTuple, TypedDict

import attrs
import msgspec
import pydantic
import pytest

from ninetales.convert import (
    AttributeInfo,
    DataModel,
    NO_DEFAULT,
    MISSING_TYPES,
    no_default_if_misc_missing,
)


@pytest.fixture
def attrs_object():
    @attrs.define
    class Foo:
        a: int = attrs.field()

    return Foo


@pytest.fixture
def dataclass_object():
    @dataclasses.dataclass
    class Foo:
        a: int = dataclasses.field()

    return Foo


@pytest.fixture
def msgspec_object():
    class Foo(msgspec.Struct):
        a: int = msgspec.field()

    return Foo


@pytest.fixture
def namedtuple_object():
    class Foo(NamedTuple):
        a: int

    return Foo


@pytest.fixture
def pydantic_object():
    class Foo(pydantic.BaseModel):
        a: int

    return Foo


@pytest.fixture
def typeddict_object():
    class Foo(TypedDict):
        a: int

    return Foo


@pytest.mark.parametrize("o", MISSING_TYPES)
def test_no_default_if_misc_missing_returns_no_default_for_missing_types(o):
    assert no_default_if_misc_missing(o) == NO_DEFAULT


# TODO: improve this with hypothesis
@pytest.mark.parametrize("o", ["a", b"a", 1, 1.0, 1j])
def test_no_default_if_misc_missing_is_identity_for_non_missing_types(o):
    assert no_default_if_misc_missing(o) == o


def test_attribute_info_from_attrs_attribute(attrs_object):
    attribute_info = AttributeInfo.from_attrs_attribute(attrs.fields(attrs_object)[0])
    assert attribute_info == AttributeInfo("a", int, NO_DEFAULT)


def test_attribute_info_from_dataclasses_field(dataclass_object):
    attribute_info = AttributeInfo.from_dataclasses_field(
        dataclasses.fields(dataclass_object)[0]
    )
    assert attribute_info == AttributeInfo("a", int, NO_DEFAULT)


def test_attribute_info_from_msgspec_field_info(msgspec_object):
    attribute_info = AttributeInfo.from_msgspec_field_info(
        msgspec.structs.fields(msgspec_object)[0]
    )
    assert attribute_info == AttributeInfo("a", int, NO_DEFAULT)


def test_data_model_from_attrs(attrs_object):
    data_model = DataModel.from_attrs(attrs_object)
    assert data_model == DataModel(
        attrs_object.__name__, [AttributeInfo("a", int, NO_DEFAULT)]
    )


def test_data_model_from_dataclass(dataclass_object):
    data_model = DataModel.from_dataclass(dataclass_object)
    assert data_model == DataModel(
        dataclass_object.__name__, [AttributeInfo("a", int, NO_DEFAULT)]
    )


def test_data_model_from_msgspec(msgspec_object):
    data_model = DataModel.from_msgspec(msgspec_object)
    assert data_model == DataModel(
        msgspec_object.__name__, [AttributeInfo("a", int, NO_DEFAULT)]
    )


def test_data_model_from_namedtuple(namedtuple_object):
    data_model = DataModel.from_namedtuple(namedtuple_object)
    assert data_model == DataModel(
        namedtuple_object.__name__, [AttributeInfo("a", int, NO_DEFAULT)]
    )


def test_data_model_from_pydantic(pydantic_object):
    data_model = DataModel.from_pydantic(pydantic_object)
    assert data_model == DataModel(
        pydantic_object.__name__, [AttributeInfo("a", int, NO_DEFAULT)]
    )


def test_data_model_from_typeddict(typeddict_object):
    data_model = DataModel.from_typeddict(typeddict_object)
    assert data_model == DataModel(
        typeddict_object.__name__, [AttributeInfo("a", int, NO_DEFAULT)]
    )
