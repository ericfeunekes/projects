"""Int field type."""
from base_schema.register import BaseTypeRegister

int_register = BaseTypeRegister(field_type="int")

@int_register("dataclass")
def create_dataclass_int(name: str) -> tuple:
    """Return value that can be passed to `make_dataclass` to create an
    int field.

    Args:
        name (str): The name of the dataclass type.

    Returns:
        tuple: The value to pass to `make_dataclass`.
    """
    return (name, int)
