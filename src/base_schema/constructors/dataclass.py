"""Constructor for dataclasses."""
from dataclasses import make_dataclass
from functools import partial
from typing import Any, Tuple, Dict

from ..register import BaseTypeRegister


def get_dataclass_field(
    field: dict, type_definitions: Dict[str, BaseTypeRegister]
) -> Tuple[str, Any]:
    """Create a dataclass field from a field definition.

    Args:
        field (dict): The field definition.
        type_definitions (dict): The type definitions.

    Returns:
        dataclasses.Field: The dataclass field.
    """
    try:
        name = field["name"]
    except KeyError as exc:
        raise ValueError("Each field in a dataclass must have a name") from exc
    try:
        property_type = field["type"]
    except KeyError as exc:
        raise ValueError(f"Field {name} doesn't have a type") from exc

    try:
        constructor = type_definitions[property_type]["dataclass"]
    except KeyError as exc:
        raise ValueError(
            f"Field {name} has type that isn't supported for dataclasses"
        ) from exc

    return constructor(name)


def create_dataclass(definition: dict, type_definitions: dict):
    """Create a dataclass type from a definition.

    Args:
        definition (dict): The definition.

    Returns:
        type: The dataclass type.
    """
    try:
        name = definition["name"]
    except KeyError as exc:
        raise ValueError("Dataclass definition must have a name.") from exc
    try:
        fields = definition["fields"]
    except KeyError as exc:
        raise ValueError(f"Dataclass {name} doesn't have any fields.") from exc

    partial_get_field = partial(get_dataclass_field, type_definitions=type_definitions)
    dataclass_fields = [partial_get_field(field) for field in fields]

    return make_dataclass(cls_name=name, fields=dataclass_fields)
