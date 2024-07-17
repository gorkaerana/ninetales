import dataclasses
from typing import NamedTuple

import attrs
import msgspec
import pytest

from ninetales.convert import AttributeInfo, DataModel, NO_DEFAULT


@pytest.fixture
def attrs_object():
    @attrs.define
    class Foo:
        a: int = attrs.field()

    return Foo(1)


@pytest.fixture
def dataclass_object():
    @dataclasses.dataclass
    class Foo:
        a: int = dataclasses.field()

    return Foo(1)


@pytest.fixture
def namedtuple_object():
    class Foo(NamedTuple):
        a: int

    return Foo(1)


@pytest.fixture
def msgspec_object():
    class Foo(msgspec.Struct):
        a: int = msgspec.field()

    return Foo(1)


def test_attribute_info_from_attrs_attribute(attrs_object):
    attribute_info = AttributeInfo.from_attrs_attribute(
        attrs.fields(type(attrs_object))[0]
    )
    assert attribute_info == AttributeInfo("a", int, NO_DEFAULT)


def test_attribute_info_from_dataclasses_field(dataclass_object):
    attribute_info = AttributeInfo.from_dataclasses_field(
        dataclasses.fields(type(dataclass_object))[0]
    )
    assert attribute_info == AttributeInfo("a", int, NO_DEFAULT)


def test_attribute_info_from_msgspec_field_info(msgspec_object):
    attribute_info = AttributeInfo.from_msgspec_field_info(
        msgspec.structs.fields(type(msgspec_object))[0]
    )
    assert attribute_info == AttributeInfo("a", int, NO_DEFAULT)


def test_data_model_from_attrs(attrs_object):
    data_model = DataModel.from_attrs(attrs_object)
    assert data_model == DataModel(
        attrs_object.__class__.__name__, [AttributeInfo("a", int, NO_DEFAULT)]
    )


def test_data_model_from_dataclass(dataclass_object):
    data_model = DataModel.from_dataclass(dataclass_object)
    assert data_model == DataModel(
        dataclass_object.__class__.__name__, [AttributeInfo("a", int, NO_DEFAULT)]
    )


def test_data_model_from_namedtuple(namedtuple_object):
    data_model = DataModel.from_namedtuple(namedtuple_object)
    assert data_model == DataModel(
        namedtuple_object.__class__.__name__, [AttributeInfo("a", int, NO_DEFAULT)]
    )


def test_data_model_from_msgspec(msgspec_object):
    data_model = DataModel.from_msgspec(msgspec_object)
    assert data_model == DataModel(
        msgspec_object.__class__.__name__, [AttributeInfo("a", int, NO_DEFAULT)]
    )
