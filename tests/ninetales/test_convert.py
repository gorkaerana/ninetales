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


# TODO: better object equality comparison


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


@pytest.fixture
def data_model():
    return DataModel(name="Foo", attributes=[AttributeInfo(name="a", type=int)])


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


def test_data_model_to_attrs(data_model, attrs_object):
    assert data_model.to_attrs().__attrs_attrs__ == attrs_object.__attrs_attrs__


def test_data_model_to_dataclass_dataclass_fields(data_model, dataclass_object):
    df1 = data_model.to_dataclass().__dataclass_fields__
    df2 = dataclass_object.__dataclass_fields__
    assert sorted(df1.keys()) == sorted(df2.keys())
    assert all(
        all(
            getattr(v, a) == getattr(df2[k], a)
            for a in dir(v)
            if not (a.startswith("__") or callable(getattr(v, a)))
        )
        for k, v in df1.items()
    )


def test_data_model_to_dataclass_dataclass_params(data_model, dataclass_object):
    dp1 = data_model.to_dataclass().__dataclass_params__
    dp2 = dataclass_object.__dataclass_params__
    assert all(
        getattr(dp1, a) == getattr(dp2, a)
        for a in dir(dp1)
        if not (a.startswith("__") or callable(getattr(dp1, a)))
    )


def test_data_model_to_msgspec_struct_fields(data_model, msgspec_object):
    sf1 = data_model.to_msgspec().__struct_fields__
    sf2 = msgspec_object.__struct_fields__
    assert sf1 == sf2


def test_data_model_to_msgspec_struct_defaults(data_model, msgspec_object):
    sd1 = data_model.to_msgspec().__struct_defaults__
    sd2 = msgspec_object.__struct_defaults__
    assert sd1 == sd2


def test_data_model_to_msgspec_struct_config(data_model, msgspec_object):
    sc1 = data_model.to_msgspec().__struct_config__
    sc2 = msgspec_object.__struct_config__
    assert all(
        getattr(sc1, a) == getattr(sc2, a)
        for a in dir(sc1)
        if not (a.startswith("__") or callable(getattr(sc1, a)))
    )


def test_data_model_to_namedtuple_fields(data_model, namedtuple_object):
    f1 = data_model.to_namedtuple()._fields
    f2 = namedtuple_object._fields
    assert f1 == f2


def test_data_model_to_namedtuple_field_defaults(data_model, namedtuple_object):
    fd1 = data_model.to_namedtuple()._field_defaults
    fd2 = namedtuple_object._field_defaults
    assert fd1 == fd2


def test_data_model_to_pydantic_model_fields(data_model, pydantic_object):
    mf1 = data_model.to_pydantic().model_fields
    mf2 = pydantic_object.model_fields
    assert sorted(mf1.keys()) == sorted(mf2.keys())
    # TODO: for some reason `mf1._attributes_set == {'annotation': <class 'int'>}`
    # but `mf2._attributes_set == {'annotation': <class 'int'>, 'frozen': None}`
    assert all(
        all(
            getattr(v, a) == getattr(mf2[k], a)
            for a in dir(v)
            if not (
                a.startswith("__")
                or callable(getattr(v, a))
                or (a == "_attributes_set")
            )
        )
        for k, v in mf1.items()
    )


def test_data_model_to_typeddict_required_keys(data_model, typeddict_object):
    rk1 = data_model.to_typeddict().__required_keys__
    rk2 = typeddict_object.__required_keys__
    assert rk1 == rk2


def test_data_model_to_typeddict_optional_keys(data_model, typeddict_object):
    ok1 = data_model.to_typeddict().__optional_keys__
    ok2 = typeddict_object.__optional_keys__
    assert ok1 == ok2


def test_data_model_to_typeddict_total(data_model, typeddict_object):
    t1 = data_model.to_typeddict().__total__
    t2 = typeddict_object.__total__
    assert t1 == t2
