from base_schema.register import register_type_definition

@register_type_definition("int", "dataclass")
def create_dataclass_int(name: str) -> tuple:
    """Return value that can be passed to `make_dataclass` to create
    a dataclass type.

    Args:
        name (str): The name of the dataclass type.

    Returns:
        tuple: The value to pass to `make_dataclass`.
    """
    return (name, int)