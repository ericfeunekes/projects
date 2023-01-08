from dataclasses import make_dataclass

from base_schema.register import type_definitions
from base_schema.types import create_dataclass_int, create_dataclass_str


def create_dataclass(definition: dict):
    """Create a dataclass type from a definition.

    Args:
        definition (dict): The definition.

    Returns:
        type: The dataclass type.
    """
    name = definition["name"]
    fields = definition["fields"]
    dataclass_fields = []

    for field in definition["fields"]:
        name = field["name"]
        property_type = field["type"]

        constructor = type_definitions[(property_type, "dataclass")]

        field = constructor(name)
        dataclass_fields.append(field)

    return make_dataclass(cls_name=name, fields=dataclass_fields)

    #
