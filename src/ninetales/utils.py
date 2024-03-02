import ast


def is_dataclasses_dataclass(node: ast.ClassDef | ast.Assign):
    # TODO: maybe support `ast.AnnAssign`?
    match node:
        # TODO: support `ast.ClassDef.type_params` for Python >= 3.12
        case ast.ClassDef(
            name=_,
            bases=_,
            keywords=_,
            body=_,
            decorator_list=decorator_list,
            # type_params=_,
        ):
            for decorator in decorator_list:
                match decorator:
                    case ast.Name(id=id_, ctx=_):
                        return id_ == "dataclass"
                    case ast.Attribute(value=value, attr=attr, ctx=_):
                        match value:
                            case ast.Name(id=id_, ctx=_):
                                return (id_ == "dataclasses") and (attr == "dataclass")
                    case ast.Call(func=func, args=_, keywords=_):
                        match func:
                            case ast.Attribute(value=value, attr=attr, ctx=_):
                                match value:
                                    case ast.Name(id=id_, ctx=_):
                                        return (id_ == "dataclasses") and (
                                            attr == "dataclass"
                                        )
                            case ast.Name(id=id_, ctx=_):
                                return id_ == "dataclass"
        case ast.Assign(targets=_, value=_, type_comment=_):
            raise Exception("Not yet supported")
    return False
