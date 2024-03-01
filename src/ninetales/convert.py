import ast


class AttributeInfo:
    # TODO: this object's attributes have been borrowed from the kwargs to
    # https://docs.python.org/3/library/dataclasses.html#dataclasses.field
    # when they should be the intersection/union of all supported frameworks
    name: str
    type_: str | None = None
    default_value: str | None = None


class DefinitionOptions:
    # TODO: this object's attributes have been borrowed from the kwargs to
    # https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass
    # when they should be the intersection/union of all supported framework
    init: str
    repr: str
    eq: str


class DataModel:
    name: str
    definition_options: list[DefinitionOptions] = []
    attributes: list[AttributeInfo] = []
    
    

class Converter(ast.NodeVisitor):
    def __init__(self):
        data_models: list[DataModel] = []
        ...

    def run(self, tree: ast.AST):
        self.visit(tree)
        
    def generic_visit(self, node: ast.AST):
        print(f"Not supported {type(node)}")

    def visit_Module(self, node: ast.AST):
        for branch in node.body:
            self.visit(branch)

    def visit_Assign(self, node: ast.Assign):
        # TODO: support dataclasses, namedtuple, attrs, msgspec and pydantic
        ...

    def visit_ClassDef(self, node: ast.ClassDef):
        # TODO: support dataclasses, NamedTuple, TypedDict, attrs, msgspec and pydantic
        data_model = DataModel(node.name)
        self.data_models.append(data_model)
        ...


if __name__ == "__main__":
    from pathlib import Path


    this_file = Path(__file__).resolve()
    here = this_file.parent
    example_dir = here.parent.parent / "examples"
    example_path = example_dir / "dataclasses_.py"
    Converter().run(ast.parse(example_path.read_text()))
