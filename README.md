# ninetales - A Python library to convert between Python data model paradigms

> "The fox spirit is an especially prolific shapeshifter"

There are a few too many ways of describing a data model in Python--see below code chunk for a non-comprehensive list. All of them represent the same concept, but have different approaches in their philosophies and implementations. This library strives, to a reasonable and useful extent, to provide a seamless translation between them.
```python
from dataclasses import dataclass
from typing import NamedTuple, TypedDict
from collections import namedtuple

import attrs
import msgspec
import pydantic

@dataclass
class FooDataclass:
    bar: str
    baz: int = 1


class FooNamedTuple(NamedTuple):
    bar: str
    baz: int = 1


# `typing.TypedDict` does not allow right hand side assignment
class FooNamedTuple(TypedDict):
    bar: str
    baz: int


# Attributes can be specified via:
# - a sequence of strings (as below)
# - a single string with each field name separated by whitespace and/or commas 
# (e.g., "bar baz", "bar, baz")
FooNamedTuple2 = namedtuple("FooNamedTuple2", ["bar", "baz"])


@attrs.define
class FooAttrs:
    bar: str
    baz: int = 1


FooAttrs2 = attrs.make_class(
    "FooAttrs2",
    {"bar": attrs.field(type=str), "baz": attrs.field(type=int, default=1)}
)


class FooMsgspec(msgspec.Struct):
    bar: str
    baz: int = 1


class FooPydantic(pydantic.BaseModel):
    bar: str
    baz: int = 1


FooPydantic2 = pydantic.create_model("FooPydantic2", bar=(str, ...), baz=(int, 1))
```

## Etymology
[Ninetales](https://bulbapedia.bulbagarden.net/wiki/Ninetales_(Pok%C3%A9mon)) is a Pokemon loosely based on the [nine-tailed fox](https://en.wikipedia.org/wiki/Nine-tailed_fox), mythical fox entity in Chinese, Korean, Vietnamese, and Japanese folklore. "The fox spirit is an especially prolific shapeshifter", is the approach this library takes to converting between Python data model paragigms.

## Installation
For the time being and until we have a stable enough API:
```bash
git clone git@github.com:gorkaerana/ninetales.git
cd ninetales
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install .
```

## Development
Im using [`rye`](https://rye-up.com/) with [`uv`](https://github.com/astral-sh/uv) backend:
```bash
git clone git@github.com:gorkaerana/ninetales.git
cd ninetales
rye sync
```
