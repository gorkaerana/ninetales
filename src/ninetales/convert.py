import ast
from typing import NamedTuple

from ast_decompiler import decompile

from ninetales.utils import is_dataclasses_dataclass


def generic_not_implemented_error(expr: ast.AST):
    message_lines = [f"{type(expr)} not supported:", decompile(expr)]
    raise NotImplementedError("\n".join(message_lines))


class AttributeInfo(NamedTuple):
    # TODO: this object's attributes have been borrowed from the kwargs to
    # https://docs.python.org/3/library/dataclasses.html#dataclasses.field
    # when they should be the intersection/union of all supported frameworks
    name: str
    type_: str | None = None
    default_value: str | None = None

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, type_={self.type_}, default_value={self.default_value})"

    @classmethod
    def from_Expr(cls, expr: ast.Expr):
        e_value = expr.value
        match e_value:
            case ast.Name(id=id_, ctx=_):
                return cls(name=id_)
            case ast.Constant(value=value):
                return cls(name=value)
            case ast.expr:
                generic_not_implemented_error(expr)
            case _:
                raise Exception(f"Unexpected {type(e_value)}: {e_value}")

    @classmethod
    def from_AnnAssign(cls, ann_assign: ast.AnnAssign):
        target, annotation = (
            ann_assign.target,
            ann_assign.annotation,
        )
        match target:
            case ast.Name(id=id_, ctx=_):
                name = id_
            case ast.Attribute(value=value, attr=_, ctx=_):
                generic_not_implemented_error(target)
            case ast.Subscript(value=value, slice=_, ctx=_):
                generic_not_implemented_error(target)
            case ast.expr:
                generic_not_implemented_error(target)
            case _:
                raise Exception(f"Unexpected {type(target)}: {target}")
        match annotation:
            case ast.Constant(value=value):
                type_annotation = value
            case ast.Name(id=id_, ctx=_):
                type_annotation = id_
            case ast.expr:
                generic_not_implemented_error(target)
            case _:
                raise Exception(f"Unexpected {type(annotation)}: {annotation}")
        return cls(name, type_annotation)


class DefinitionOptions(NamedTuple):
    # TODO: this object's attributes have been borrowed from the kwargs to
    # https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass
    # when they should be the intersection/union of all supported framework
    init: str
    repr: str
    eq: str


class DataModel:
    def __init__(
        self,
        name: str,
        definition_options: dict = {},
        attributes: list[AttributeInfo] = [],
    ):
        self.name = name
        self.definition_options = definition_options
        self.attributes = attributes

    def __repr__(self):
        return f"{self.__class__.__name__}(name={repr(self.name)}, definition_options={repr(self.definition_options)}, attributes={repr(self.attributes)})"


class Converter(ast.NodeVisitor):
    data_models: list[DataModel] = []

    def run(self, tree: ast.AST):
        self.visit(tree)

    def generic_visit(self, node: ast.AST):
        print(f"Not supported {type(node)}")

    def visit_Module(self, node: ast.Module):
        for branch in node.body:
            self.visit(branch)

    def visit_Assign(self, node: ast.Assign):
        # TODO: support dataclasses, namedtuple, attrs, msgspec and pydantic
        ...

    def visit_ClassDef(self, node: ast.ClassDef):
        # TODO: support dataclasses, NamedTuple, TypedDict, attrs, msgspec and pydantic
        if is_dataclasses_dataclass(node):
            data_model = DataModel(node.name)
            # TODO: search for the `dataclass` decorator
            # TODO: please mypy
            if node.decorator_list and isinstance(node.decorator_list[0], ast.Call):
                data_model.definition_options = {
                    k.arg: k.value.value  # type: ignore
                    for k in node.decorator_list[0].keywords
                }
            # TODO: please mypy
            data_model.attributes = [
                AttributeInfo.from_AnnAssign(branch)  # type: ignore
                for branch in node.body
            ]
            breakpoint()
        ...


if __name__ == "__main__":
    from pathlib import Path

    this_file = Path(__file__).resolve()
    here = this_file.parent
    example_dir = here.parent.parent / "examples"
    example_path = example_dir / "dataclasses_.py"
    Converter().run(ast.parse(example_path.read_text()))
