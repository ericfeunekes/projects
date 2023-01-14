"""The str field type."""
from base_schema.register import BaseTypeRegister

str_register = BaseTypeRegister(field_type="str")

@str_register("dataclass")
def create_dataclass_str(name: str) -> tuple:
    """Return value that can be passed to `make_dataclass` to create a
    dataclass type.

    Args:
        name (str): The name of the dataclass type.

    Returns:
        tuple: The value to pass to `make_dataclass`.
    """
    return (name, str)
