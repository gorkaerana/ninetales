import ast
from typing import Any, NamedTuple


def generic_not_implemented_error(expr: ast.expr):
    message_lines = [f"{type(expr)} not supported:", ast.dump(expr, indent=4)]
    raise NotImplementedError("\n".join(message_lines))


class AttributeInfo(NamedTuple):
    name: str
    type_annotation: str | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_ast_expr(cls, expr: ast.Expr):
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
    def from_ast_ann_assign(cls, ann_assign: ast.AnnAssign):
        target, annotation = (
            ann_assign.target,
            ann_assign.annotation,
        )
        metadata: dict[str, Any] = {}
        match target:
            case ast.Name(id=id_, ctx=ctx):
                name = id_
                metadata["ann_assign__target_name_ctx"] = ctx
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
            case ast.Name(id=id_, ctx=ctx):
                type_annotation = id_
                metadata["ann_assign__target_name_ctx"] = ctx
            case ast.expr:
                generic_not_implemented_error(target)
            case _:
                raise Exception(f"Unexpected {type(annotation)}: {annotation}")
        metadata["ann_assign__value"] = ann_assign.value
        metadata["ann_assign__simple"] = ann_assign.simple
        return cls(name, type_annotation, metadata)


class IntermediateRepresentation(NamedTuple):
    name: str
    attributes: list[AttributeInfo] = []
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_ast_class_def(cls, class_def: ast.ClassDef):
        attributes: list[AttributeInfo] = []
        for element in class_def.body:
            match element:
                case ast.Expr(value=_):
                    attributes.append(AttributeInfo.from_ast_expr(element))
                case ast.AnnAssign(target=_, annotation=_, value=_, simple=_):
                    attributes.append(AttributeInfo.from_ast_ann_assign(element))
                case ast.expr:
                    generic_not_implemented_error(element)
                case _:
                    raise Exception(f"Unexpected {type(element)}: {element}")
        return cls(
            class_def.name,
            attributes,
            {
                "class_def__bases": class_def.bases,
                "class_def__keywords": class_def.keywords,
                "class_def__decorator_list": class_def.decorator_list,
                "class_def__type_params": class_def.type_params,
            },
        )

    @classmethod
    def from_ast_assign(cls, class_def: ast.ClassDef):
        raise NotImplementedError


if __name__ == "__main__":
    from pathlib import Path
    from pprint import pprint

    this_file = Path(__file__).resolve()
    here = this_file.parent
    example_dir = here / "examples"
    example_path = example_dir / "dataclasses_.py"
    for path in example_dir.glob("*.py"):
        intermediate_representations = []
        for node in ast.walk(ast.parse(path.read_text())):
            match node:
                case ast.Module(body=body, type_ignores=type_ignores):
                    continue
                case ast.Import(names=names):
                    # TODO: collect
                    ...
                case ast.ImportFrom(module=module, names=names, level=level):
                    # TODO: collect
                    ...
                # TODO: Python 3.12 should support `type_params` argument
                case ast.ClassDef(
                    name=name,
                    bases=bases,
                    keywords=keywords,
                    body=body,
                    decorator_list=decorator_list,
                ):
                    print("Got ast.ClassDef")
                    intermediate_representations.append(
                        IntermediateRepresentation.from_ast_class_def(node)
                    )
                case ast.Assign(
                    targets=targets, value=value, type_comment=type_comment
                ):
                    # TODO:
                    print("Got ast.Assign")
                    ...
                case _:
                    # print(f"Unexpected {type(node)}: {node}")
                    continue
        print(intermediate_representations)
        pprint(intermediate_representations[0].attributes)
